#!/usr/bin/env python3
"""Check manifest structure and declared local evidence; never execute model evals."""
import argparse
import hashlib
import json
from pathlib import Path
import yaml
from quick_validate import load_frontmatter, validate_skill

VALID_TYPES = {'positive', 'negative', 'ambiguous', 'failure', 'adversarial', 'regression'}
VALID_STATUS = {'NOT_RUN', 'PASS', 'FAIL', 'INCONCLUSIVE'}

def validate(folder, manifest, release=False):
    root = Path(folder).resolve(strict=True)
    valid, message = validate_skill(root)
    if not valid:
        raise ValueError(message)
    meta, _ = load_frontmatter(root)
    manifest_path = Path(manifest).resolve(strict=True)
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Manifest must be an object')
    if data.get('skill') != meta.get('name') or not isinstance(data.get('skill'), str):
        raise ValueError('Manifest skill ID must match SKILL.md')
    version = data.get('version')
    if version is not None and (not isinstance(version, str) or not version.strip()):
        raise ValueError('version must be a nonempty string')
    declared_hash = data.get('skill_sha256')
    actual_hash = hashlib.sha256((root / 'SKILL.md').read_bytes()).hexdigest()
    if declared_hash is not None and declared_hash != actual_hash:
        raise ValueError('Manifest hash does not match SKILL.md')
    if release:
        if declared_hash is None or not version:
            raise ValueError('Release requires version and skill_sha256')
        actual_version = meta.get('metadata', {}).get('version')
        if actual_version is not None and version != actual_version:
            raise ValueError('Release version does not match skill metadata')
    cases = data.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('At least one case is required')
    seen = set()
    for case in cases:
        required_fields = {'id', 'type', 'prompt', 'expected_skill', 'status'}
        if not isinstance(case, dict) or not required_fields.issubset(case):
            raise ValueError('Invalid evaluation case')
        identifier = case['id']
        if not isinstance(identifier, str) or not identifier.strip() or identifier in seen:
            raise ValueError('Missing/duplicate case ID')
        seen.add(identifier)
        if not isinstance(case['type'], str) or case['type'] not in VALID_TYPES:
            raise ValueError(f'Invalid type: {identifier}')
        if not isinstance(case['status'], str) or case['status'] not in VALID_STATUS:
            raise ValueError(f'Invalid status: {identifier}')
        if not isinstance(case['prompt'], str) or not case['prompt'].strip():
            raise ValueError('Empty prompt')
        expected = case['expected_skill']
        if expected is not None and (not isinstance(expected, str) or not expected.strip()):
            raise ValueError('Expected skill must be a nonempty string or null')
        required = case.get('required', True)
        if not isinstance(required, bool):
            raise ValueError('required must be boolean')
        evidence = case.get('evidence')
        if evidence is not None:
            if not isinstance(evidence, str) or not evidence.strip():
                raise ValueError('Evidence must be a nonempty relative file path')
            path = Path(evidence)
            if path.is_absolute() or '..' in path.parts or '\\' in evidence:
                raise ValueError('Evidence must stay inside the manifest directory')
            resolved = (manifest_path.parent / path).resolve()
            if not resolved.is_relative_to(manifest_path.parent) or not resolved.is_file() or not resolved.stat().st_size:
                raise ValueError(f'Missing, empty or external evidence: {identifier}')
        if release and required and (case['status'] != 'PASS' or evidence is None):
            raise ValueError(f'Release blocked: {identifier} needs PASS with local evidence')
    return len(cases)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill_folder')
    parser.add_argument('manifest')
    parser.add_argument('--release', action='store_true', help='Require version/hash and PASS evidence for required cases')
    args = parser.parse_args()
    try:
        count = validate(args.skill_folder, args.manifest, args.release)
        print(f'Manifest valid: {count} cases (structure/evidence only; behavior NOT executed)')
    except (ValueError, OSError, TypeError, yaml.YAMLError) as error:
        print(f'Manifest invalid: {error}')
        raise SystemExit(1)
