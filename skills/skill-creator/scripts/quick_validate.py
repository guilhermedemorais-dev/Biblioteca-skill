#!/usr/bin/env python3
"""Static validation. Does not certify runtime behavior or instruction quality."""
import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
import yaml

NAME_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

def valid_name(name):
    return isinstance(name, str) and 1 <= len(name) <= 64 and NAME_RE.fullmatch(name) is not None

def load_frontmatter(root):
    path = Path(root) / 'SKILL.md'
    if not path.is_file() or path.is_symlink():
        raise ValueError('SKILL.md must be a regular file, not a symlink')
    content = path.read_text(encoding='utf-8')
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', content, re.S)
    if not match:
        raise ValueError('Missing or invalid YAML frontmatter')
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError('Frontmatter must be a mapping')
    return data, content[match.end():]

def local_file(root, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative:
        raise ValueError(f'Unsafe local reference: {relative}')
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError(f'Missing or external local file: {relative}')
    return resolved

def local_references(body):
    in_fence = None
    for line in body.splitlines():
        fence = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fence:
            marker = fence.group(1)[0]
            if in_fence is None:
                in_fence = marker
            elif in_fence == marker:
                in_fence = None
            continue
        if in_fence:
            continue
        for link in re.findall(r'\]\(([^)]+)\)', line):
            target = link.strip().strip('<>')
            parts = urlsplit(target)
            if not parts.scheme and parts.path:
                yield unquote(parts.path)

def validate_skill(skill_path, profile='portable'):
    try:
        root = Path(skill_path).resolve(strict=True)
        if not root.is_dir():
            raise ValueError('Skill path must be a directory')
        meta, body = load_frontmatter(root)
        allowed = {'name', 'description', 'license', 'compatibility', 'allowed-tools', 'metadata'}
        extra = set(meta) - allowed
        if extra:
            raise ValueError('Unexpected frontmatter fields: ' + ', '.join(map(str, sorted(extra, key=str))))
        if not valid_name(meta.get('name')):
            raise ValueError('Name must be 1–64 lowercase alphanumeric/hyphen characters, without repeated or edge hyphens')
        if meta['name'] != root.name:
            raise ValueError('Name must match parent directory name')
        desc = meta.get('description')
        if not isinstance(desc, str) or not desc.strip() or len(desc) > 1024:
            raise ValueError('Description must be a nonempty string of at most 1024 characters')
        for field in ('license', 'allowed-tools'):
            if field in meta and not isinstance(meta[field], str):
                raise ValueError(f'{field} must be a string')
        if 'compatibility' in meta:
            value = meta['compatibility']
            if not isinstance(value, str) or not value.strip() or len(value) > 500:
                raise ValueError('Compatibility must be a nonempty string of at most 500 characters')
        custom = meta.get('metadata', {})
        if not isinstance(custom, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in custom.items()):
            raise ValueError('metadata must map strings to strings')
        for relative in custom.get('required-files', '').split():
            local_file(root, relative)
        for relative in local_references(body):
            local_file(root, relative)
        ui = root / 'agents/openai.yaml'
        if profile == 'codex' or ui.exists():
            if not ui.is_file():
                raise ValueError('Codex profile requires agents/openai.yaml')
            if not ui.resolve().is_relative_to(root):
                raise ValueError('UI metadata must stay inside skill root')
            config = yaml.safe_load(ui.read_text(encoding='utf-8'))
            interface = config.get('interface') if isinstance(config, dict) else None
            if not isinstance(interface, dict) or not isinstance(interface.get('display_name'), str) or not interface['display_name'].strip():
                raise ValueError('UI metadata requires interface.display_name')
        return True, 'Skill is valid! (static checks only)'
    except (OSError, ValueError, TypeError, yaml.YAMLError) as error:
        return False, str(error)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_directory')
    parser.add_argument('--profile', choices=['portable', 'codex'], default='portable')
    args = parser.parse_args()
    valid, message = validate_skill(args.skill_directory, args.profile)
    print(message)
    raise SystemExit(0 if valid else 1)
