#!/usr/bin/env python3
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

MANIFEST = '魂师修炼RPG_manifest.json'
RELEASE_RE = re.compile(r'^\d+\.\d+$')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def valid_git_sha(value) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(c in '0123456789abcdef' for c in value.lower())
    )


def expected_package_filename(data: dict) -> str:
    release = str(data.get('release', ''))
    if not RELEASE_RE.fullmatch(release):
        raise SystemExit('FAIL: invalid package release')
    return f'魂师修炼RPG_v{release}.zip'


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('usage: audit_runtime_package.py <runtime.zip>')

    path = Path(sys.argv[1])
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if MANIFEST not in names:
            raise SystemExit('FAIL: manifest missing')
        if len(names) != len(set(names)):
            raise SystemExit('FAIL: duplicate zip members')

        data = json.loads(archive.read(MANIFEST))
        generated = data.get('generated_view', {})
        if not generated.get('derived'):
            raise SystemExit('FAIL: manifest is not derived view')

        source_sha = generated.get('source_git_commit_sha')
        if not valid_git_sha(source_sha):
            raise SystemExit('FAIL: exact source Git commit identity missing')
        if data.get('versioning', {}).get('package_manifest_must_embed_source_commit') is not True:
            raise SystemExit('FAIL: package source commit requirement missing')
        if data.get('source_authority', {}).get('compatibility_export_identity') != 'generated_view.source_git_commit_sha':
            raise SystemExit('FAIL: compatibility export identity pointer mismatch')

        if data.get('versioning', {}).get('package_filename_must_match_release') is True:
            expected = expected_package_filename(data)
            if path.name != expected:
                raise SystemExit(f'FAIL: package filename mismatch; expected {expected}')

        registered = set(data.get('files', {}))
        actual = set(names)
        if registered != actual:
            print('FAIL: membership mismatch')
            print('unregistered:', sorted(actual - registered))
            print('missing:', sorted(registered - actual))
            raise SystemExit(2)

        failures = []
        for name, meta in data['files'].items():
            if name == MANIFEST:
                continue
            raw = archive.read(name)
            if meta.get('bytes') != len(raw):
                failures.append((name, 'bytes'))
            if meta.get('sha256') != sha256(raw):
                failures.append((name, 'sha256'))

        routes = data.get('topic_routes', {})
        ordinary = data.get('interaction_route_activation', [])
        entries = set()
        for item in ordinary:
            if isinstance(item, str):
                entries.add(item)
            elif isinstance(item, dict) and item.get('route'):
                entries.add(item['route'])
        for value in data.get('control_intents', {}).values():
            if value.get('route'):
                entries.add(value['route'])
        for route in routes.values():
            for delegate in route.get('delegates_to', []) or []:
                if isinstance(delegate, str):
                    entries.add(delegate)
                elif isinstance(delegate, dict) and delegate.get('route'):
                    entries.add(delegate['route'])
        entries.update(['governance_boot', 'ordinary_gameplay_startup'])

        orphan = [name for name in routes if name not in entries]
        if failures or orphan:
            print('FAIL')
            if failures:
                print('hash/size:', failures)
            if orphan:
                print('orphan routes:', orphan)
            raise SystemExit(3)

        skills = {
            value.get('skill')
            for value in data.get('control_intents', {}).values()
            if value.get('dispatch_type') == 'skill'
        }
        print(json.dumps({
            'status': 'PASS',
            'release': data.get('release'),
            'source_git_commit_sha': source_sha,
            'members': len(names),
            'routes': len(routes),
            'skill_dispatches': sorted(skill for skill in skills if skill),
            'control_intents': len(data.get('control_intents', {})),
        }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
