#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def fail(msg): raise SystemExit('FAIL: '+msg)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project',default='.'); a=ap.parse_args()
    p=Path(a.project)
    for f in ['governance/project.md','runtime/registry.json','.github/workflows/qa.yml','.gitignore','state/current/SOUL_STATE_V1.yaml']:
        if not (p/f).is_file(): fail(f'missing {f}')
    gov=(p/'governance/project.md').read_text(encoding='utf-8')
    if '`main` HEAD' not in gov or 'Git' not in gov: fail('governance does not declare main HEAD authority')
    reg=json.loads((p/'runtime/registry.json').read_text(encoding='utf-8'))
    if 'files' in reg or 'hash_policy' in reg: fail('source registry must not own package hashes/membership')
    if reg.get('source_authority',{}).get('identity')!='git_commit_sha': fail('source release identity not git commit sha')
    man=json.loads((p/'魂师修炼RPG_manifest.json').read_text(encoding='utf-8'))
    if not man.get('generated_view',{}).get('derived'): fail('compatibility manifest not marked derived')
    if man.get('generated_view',{}).get('source')!='runtime/registry.json': fail('compatibility manifest source mismatch')
    ignored=(p/'.gitignore').read_text(encoding='utf-8')
    if 'dist/' not in ignored or '*.zip' not in ignored: fail('exports not ignored')
    
    if reg.get('source_authority',{}).get('state_authority')!='state/current/SOUL_STATE_V1.yaml': fail('state authority not registered')
    print(json.dumps({'status':'PASS','authority':'git main HEAD','registry':'runtime/registry.json','state':'state/current/SOUL_STATE_V1.yaml'},ensure_ascii=False))
if __name__=='__main__': main()
