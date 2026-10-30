#!/usr/bin/env python3
"""Inventory and atomically package a skill, excluding sensitive/generated files."""
import argparse
import fnmatch
import os
import tempfile
import zipfile
from pathlib import Path
from quick_validate import validate_skill

MAX_SKILL_ZIP_BYTES = 25 * 1024 * 1024  # Distribution default, not a universal host limit.
IGNORED_DIRS = {'.git', '.hg', '.svn', '__pycache__', '.pytest_cache', '.venv', 'node_modules'}
IGNORED_FILES = {'skill.zip', '.DS_Store'}
SENSITIVE_PATTERNS = ('.env', '.env.*', '*.pem', '*.key', '*.p12', '*.pfx', 'id_rsa*', 'id_ed25519*', 'credentials.json', '*service-account*.json')

def inventory(root):
    files, excluded = [], []
    for folder, directories, names in os.walk(root, followlinks=False):
        for name in list(directories):
            path = Path(folder) / name
            if path.is_symlink():
                raise ValueError(f'Symlink directories are not supported: {path.relative_to(root)}')
            if name in IGNORED_DIRS:
                directories.remove(name)
                excluded.append(str(path.relative_to(root)) + '/')
        for name in names:
            path = Path(folder) / name
            relative = path.relative_to(root)
            if path.is_symlink():
                raise ValueError(f'Symlink files are not supported: {relative}')
            if not path.is_file():
                raise ValueError(f'Not a regular file: {relative}')
            sensitive = any(fnmatch.fnmatch(name.lower(), pattern) for pattern in SENSITIVE_PATTERNS)
            if (sensitive and name != '.env.example') or name in IGNORED_FILES or name.endswith(('.pyc', '.pyo')):
                excluded.append(str(relative))
            else:
                files.append(relative)
    return sorted(files), sorted(excluded)

def package_skill(skill_path, output_dir=None, *, dry_run=False):
    temporary = None
    try:
        root = Path(skill_path).resolve(strict=True)
        valid, message = validate_skill(root)
        if not valid:
            raise ValueError(message)
        destination = Path(output_dir).resolve() if output_dir else Path.cwd().resolve()
        if destination.is_relative_to(root):
            raise ValueError('Output directory must be outside the skill root')
        files, excluded = inventory(root)
        print('Inventory (no file contents):')
        for relative in files:
            print(f'  INCLUDE {relative}')
        for relative in excluded:
            print(f'  EXCLUDE {relative}')
        # A declared resource must not silently disappear because of an exclusion.
        packaged = {relative.as_posix() for relative in files}
        from quick_validate import load_frontmatter, local_references
        meta, body = load_frontmatter(root)
        for required in [*meta.get('metadata', {}).get('required-files', '').split(), *local_references(body)]:
            if Path(required).as_posix() not in packaged:
                raise ValueError(f'Required file excluded from package: {required}')
        if dry_run:
            return destination / 'skill.zip'
        destination.mkdir(parents=True, exist_ok=True)
        handle, filename = tempfile.mkstemp(prefix='.skill-', suffix='.zip.tmp', dir=destination)
        os.close(handle)
        temporary = Path(filename)
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
            for relative in files:
                path = root / relative
                # Recheck before reading. Do not follow a replaced file symlink.
                if path.is_symlink() or not path.resolve().is_relative_to(root):
                    raise ValueError(f'File changed to external reference: {relative}')
                with open(path, 'rb', opener=lambda path, flags: os.open(path, flags | os.O_NOFOLLOW)) as source:
                    archive.writestr(f'{root.name}/{relative.as_posix()}', source.read())
        if temporary.stat().st_size > MAX_SKILL_ZIP_BYTES:
            raise ValueError(f'Package exceeds configured limit ({MAX_SKILL_ZIP_BYTES} bytes)')
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError('ZIP integrity check failed')
        target = destination / 'skill.zip'
        os.replace(temporary, target)
        print(f'Packaged: {target}')
        return target
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f'Packaging failed: {error}')
        return None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_folder')
    parser.add_argument('output_directory', nargs='?')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    raise SystemExit(0 if package_skill(args.skill_folder, args.output_directory, dry_run=args.dry_run) else 1)
