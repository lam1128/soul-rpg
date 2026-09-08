#!/usr/bin/env python3
import argparse, copy, hashlib, json, subprocess, zipfile
from pathlib import Path

MANIFEST = '魂师修炼RPG_manifest.json'
REGISTRY = 'runtime/registry.json'
MEMBERS_CFG = 'compatibility/runtime-members.json'

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def git_head_sha(project: Path) -> str:
    try:
        value = subprocess.check_output(
            ['git', '-C', str(project), 'rev-parse', 'HEAD'],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip().lower()
    except Exception as exc:
        raise SystemExit(f'cannot resolve source Git HEAD: {exc}')
    if len(value) != 40 or any(c not in '0123456789abcdef' for c in value):
        raise SystemExit('invalid source Git HEAD sha')
    return value

def build_manifest(project: Path):
    registry = load_json(project / REGISTRY)
    cfg = load_json(project / MEMBERS_CFG)
    members = list(cfg['members'])
    if cfg.get('manifest') != MANIFEST:
        raise SystemExit('runtime-members manifest path mismatch')
    if MANIFEST not in members:
        raise SystemExit('runtime-members must include manifest')
    if len(members) != len(set(members)):
        raise SystemExit('duplicate runtime member path')

    source_sha = git_head_sha(project)
    derived = copy.deepcopy(registry)
    derived['generated_view'] = {
        'derived': True,
        'source': REGISTRY,
        'purpose': 'compatibility_runtime_export',
        'source_authority': 'git main HEAD',
        'source_git_commit_sha': source_sha,
        'state_projection': 'canonical_git_state_excluded_use_external_checkpoint_import'
    }
    derived['hash_policy'] = {
        'algorithm': 'sha256',
        'manifest_self_hash': 'omitted_to_avoid_self_reference',
        'hashes_cover': 'all other formal package members'
    }
    files = {}
    for name in members:
        if name == MANIFEST:
            files[name] = {}
            continue
        path = project / name
        if not path.is_file():
            raise SystemExit(f'missing runtime member: {name}')
        raw = path.read_bytes()
        files[name] = {'bytes': len(raw), 'sha256': sha256(raw)}
    derived['files'] = files
    return derived, members

def manifest_bytes(project: Path):
    manifest, members = build_manifest(project)
    raw = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    return raw, members

def verify_zip(path: Path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise SystemExit('duplicate zip members')
        if MANIFEST not in names:
            raise SystemExit('manifest missing')
        data = json.loads(z.read(MANIFEST))
        source_sha = data.get('generated_view', {}).get('source_git_commit_sha')
        if not isinstance(source_sha, str) or len(source_sha) != 40 or any(c not in '0123456789abcdef' for c in source_sha.lower()):
            raise SystemExit('source Git commit identity missing')
        registered = set(data.get('files', {}))
        if registered != set(names):
            raise SystemExit('zip membership mismatch')
        for name, meta in data['files'].items():
            if name == MANIFEST:
                continue
            raw = z.read(name)
            if meta.get('bytes') != len(raw):
                raise SystemExit(f'bytes mismatch: {name}')
            if meta.get('sha256') != sha256(raw):
                raise SystemExit(f'sha mismatch: {name}')
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', default='.')
    ap.add_argument('--out')
    args = ap.parse_args()
    project = Path(args.project).resolve()
    raw_manifest, members = manifest_bytes(project)
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = project / out
        out.parent.mkdir(parents=True, exist_ok=True)
        # Deterministic compatibility export: source bytes and exact Git HEAD define the artifact, not wall-clock ZIP metadata.
        with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_STORED) as z:
            for name in members:
                raw = raw_manifest if name == MANIFEST else (project / name).read_bytes()
                zi = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                zi.create_system = 3
                zi.compress_type = zipfile.ZIP_STORED
                zi.external_attr = (0o100644 & 0xFFFF) << 16
                z.writestr(zi, raw)
        verify_zip(out)
        manifest = json.loads(raw_manifest)
        print(json.dumps({'status':'PASS','out':str(out),'members':len(members),'source_git_commit_sha':manifest['generated_view']['source_git_commit_sha']}, ensure_ascii=False))
    else:
        print(raw_manifest.decode('utf-8'))

if __name__ == '__main__':
    main()
