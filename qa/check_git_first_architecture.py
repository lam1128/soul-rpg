#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def fail(msg): raise SystemExit('FAIL: '+msg)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project',default='.'); a=ap.parse_args()
    p=Path(a.project)
    required=[
        'governance/project.md',
        'runtime/registry.json',
        '.github/workflows/qa.yml',
        '.gitignore',
        'state/current/SOUL_STATE_V1.yaml',
        'compatibility/runtime-members.json',
        'scripts/export_runtime_zip.py',
    ]
    for f in required:
        if not (p/f).is_file(): fail(f'missing {f}')
    gov=(p/'governance/project.md').read_text(encoding='utf-8')
    if '`main` HEAD' not in gov or 'Git' not in gov: fail('governance does not declare main HEAD authority')
    reg=json.loads((p/'runtime/registry.json').read_text(encoding='utf-8'))
    if 'files' in reg or 'hash_policy' in reg: fail('source registry must not own package hashes/membership')
    if reg.get('source_authority',{}).get('identity')!='git_commit_sha': fail('source release identity not git commit sha')
    if reg.get('source_authority',{}).get('state_authority')!='state/current/SOUL_STATE_V1.yaml': fail('state authority not registered')
    cfg=json.loads((p/'compatibility/runtime-members.json').read_text(encoding='utf-8'))
    manifest_name=reg.get('source_authority',{}).get('compatibility_manifest')
    if cfg.get('manifest')!=manifest_name: fail('registry/runtime-members compatibility manifest name mismatch')
    if manifest_name not in cfg.get('members',[]): fail('compatibility manifest not registered as package member')
    if (p/manifest_name).exists(): fail('derived compatibility manifest must not be persisted in Git source tree')
    ignored=(p/'.gitignore').read_text(encoding='utf-8')
    if 'dist/' not in ignored or '*.zip' not in ignored: fail('exports not ignored')
    print(json.dumps({'status':'PASS','authority':'git main HEAD','registry':'runtime/registry.json','state':'state/current/SOUL_STATE_V1.yaml','compat_manifest':'generated_at_export'},ensure_ascii=False))
if __name__=='__main__': main()
