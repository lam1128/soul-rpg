#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

TEXT_SUFFIXES = {'.md', '.json', '.yaml', '.yml', '.py'}
FORBIDDEN_BASENAMES = {
    '.DS_Store',
    'Thumbs.db',
    '魂师修炼RPG_manifest.json',
}
FORBIDDEN_SUFFIXES = {
    '.zip',
    '.bak',
    '.backup',
    '.old',
    '.orig',
    '.rej',
    '.patch',
    '.tmp',
    '.pyc',
    '.pyo',
}
FORBIDDEN_DIRS = {
    'dist',
    'build',
    'tmp',
    'temp',
    'backup',
    'backups',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    '.venv',
    'venv',
}
FORBIDDEN_NAME_TOKENS = ('_old', '_backup', 'final_final')
HARDCODED_PACKAGE_RE = re.compile(r'魂师修炼RPG_v\d+\.\d+\.zip')


def fail(message: str) -> None:
    raise SystemExit('FAIL: ' + message)


def tracked_files(project: Path) -> list[str]:
    try:
        raw = subprocess.check_output(
            ['git', '-C', str(project), 'ls-files', '-z'],
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        fail(f'cannot enumerate tracked files: {exc}')
    return [item.decode('utf-8') for item in raw.split(b'\0') if item]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', default='.')
    args = parser.parse_args()
    project = Path(args.project).resolve()

    files = tracked_files(project)
    if not files:
        fail('repository has no tracked files')

    artifact_violations: list[str] = []
    format_violations: list[str] = []
    hardcoded_package_refs: list[str] = []
    json_files = 0
    markdown_files = 0

    for rel in files:
        posix = PurePosixPath(rel)
        lower_name = posix.name.lower()
        lower_parts = {part.lower() for part in posix.parts[:-1]}

        if posix.name in FORBIDDEN_BASENAMES:
            artifact_violations.append(rel)
        if any(lower_name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
            artifact_violations.append(rel)
        if lower_name.endswith('~'):
            artifact_violations.append(rel)
        if lower_parts & FORBIDDEN_DIRS:
            artifact_violations.append(rel)
        if any(token in lower_name for token in FORBIDDEN_NAME_TOKENS):
            artifact_violations.append(rel)

        path = project / rel
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue

        raw = path.read_bytes()
        if raw.startswith(b'\xef\xbb\xbf'):
            format_violations.append(f'{rel}: UTF-8 BOM')
        if b'\r' in raw:
            format_violations.append(f'{rel}: CR/CRLF line endings')
        if raw and not raw.endswith(b'\n'):
            format_violations.append(f'{rel}: missing final newline')

        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            format_violations.append(f'{rel}: not valid UTF-8')
            continue

        if '\t' in text:
            format_violations.append(f'{rel}: tab character')
        if HARDCODED_PACKAGE_RE.search(text):
            hardcoded_package_refs.append(rel)

        if path.suffix.lower() == '.json':
            json_files += 1
            try:
                json.loads(text)
            except Exception as exc:
                format_violations.append(f'{rel}: invalid JSON ({exc})')
        elif path.suffix.lower() == '.md':
            markdown_files += 1
            first_nonempty = next((line for line in text.splitlines() if line.strip()), '')
            if not first_nonempty.startswith('# '):
                format_violations.append(f'{rel}: first content line is not H1')

    if artifact_violations:
        fail('tracked artifact/tombstone paths: ' + ', '.join(sorted(set(artifact_violations))))
    if format_violations:
        fail('text hygiene violations: ' + '; '.join(format_violations))
    if hardcoded_package_refs:
        fail('hard-coded compatibility package filenames outside registry-derived export: ' + ', '.join(sorted(set(hardcoded_package_refs))))

    state_dir = project / 'state' / 'current'
    state_files = sorted(
        str(path.relative_to(project))
        for path in state_dir.iterdir()
        if path.is_file()
    )
    if state_files != ['state/current/SOUL_STATE_V1.yaml']:
        fail('state/current must contain only state/current/SOUL_STATE_V1.yaml')

    print(json.dumps({
        'status': 'PASS',
        'tracked_files': len(files),
        'markdown_files': markdown_files,
        'json_files': json_files,
        'forbidden_artifacts': 0,
        'hardcoded_package_filenames': 0,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
