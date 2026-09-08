#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def fail(msg):
    raise SystemExit('FAIL: ' + msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', default='.')
    args = ap.parse_args()
    project = Path(args.project)

    required = [
        'governance/project.md',
        'runtime/registry.json',
        '.github/workflows/qa.yml',
        '.gitignore',
        'state/current/SOUL_STATE_V1.yaml',
        '魂师修炼RPG_项目索引.md',
    ]
    for rel in required:
        if not (project / rel).is_file():
            fail(f'missing {rel}')

    forbidden = [
        'compatibility',
        'scripts/export_runtime_zip.py',
        'qa/audit_runtime_package.py',
        'qa/check_derived_export.py',
        '魂师修炼RPG_manifest.json',
        '魂师修炼RPG_文档索引与版本状态.md',
    ]
    for rel in forbidden:
        if (project / rel).exists():
            fail(f'legacy compatibility runtime structure still exists: {rel}')

    governance = (project / 'governance/project.md').read_text(encoding='utf-8')
    if '`main` HEAD' not in governance or 'Git commit SHA' not in governance:
        fail('governance does not declare Git main HEAD / commit SHA authority')
    if '项目不维护 `MAJOR.MINOR`' not in governance:
        fail('governance does not explicitly reject numbered project releases')

    registry = json.loads((project / 'runtime/registry.json').read_text(encoding='utf-8'))
    if 'release' in registry:
        fail('registry must not contain project/package release field')
    if 'versioning' in registry:
        fail('registry must not maintain a second project versioning block')
    if 'files' in registry or 'hash_policy' in registry:
        fail('registry must not own package hashes/membership')

    source = registry.get('source_authority', {})
    if source.get('mode') != 'git_first':
        fail('source_authority.mode is not git_first')
    if source.get('branch') != 'main':
        fail('source_authority.branch is not main')
    if source.get('identity') != 'git_commit_sha':
        fail('source identity is not Git commit SHA')
    if source.get('state_authority') != 'state/current/SOUL_STATE_V1.yaml':
        fail('state authority not registered')
    if any(key.startswith('compatibility_') for key in source):
        fail('source_authority still exposes compatibility runtime metadata')

    qa = registry.get('qa', {})
    if 'compatibility_export_audit' in qa:
        fail('registry QA still references compatibility runtime export audit')

    ignored = (project / '.gitignore').read_text(encoding='utf-8')
    if '*.zip' not in ignored or 'dist/' not in ignored:
        fail('disposable archive/build outputs are not ignored')

    print(json.dumps({
        'status': 'PASS',
        'authority': 'git main HEAD',
        'source_identity': 'git_commit_sha',
        'state': 'state/current/SOUL_STATE_V1.yaml',
        'numbered_project_release': False,
        'compatibility_runtime': False,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
