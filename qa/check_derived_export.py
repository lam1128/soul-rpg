#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

def sha(b): return hashlib.sha256(b).hexdigest()
def fail(msg): raise SystemExit('FAIL: '+msg)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project',default='.'); a=ap.parse_args()
    p=Path(a.project)
    reg=json.loads((p/'runtime/registry.json').read_text(encoding='utf-8'))
    man=json.loads((p/'魂师修炼RPG_manifest.json').read_text(encoding='utf-8'))
    cfg=json.loads((p/'compatibility/runtime-members.json').read_text(encoding='utf-8'))
    for key in reg:
        if man.get(key)!=reg[key]: fail(f'derived manifest drift at key {key}')
    gv=man.get('generated_view',{})
    if gv.get('state_projection')!='canonical_git_state_excluded_use_external_checkpoint_import': fail('compatibility state projection missing')
    members=cfg['members']
    if 'state/current/SOUL_STATE_V1.yaml' in members: fail('canonical Git state must not be bundled into compatibility runtime')
    if set(man.get('files',{}))!=set(members): fail('derived manifest membership drift')
    for name in members:
        if name=='魂师修炼RPG_manifest.json': continue
        raw=(p/name).read_bytes(); meta=man['files'][name]
        if meta.get('bytes')!=len(raw) or meta.get('sha256')!=sha(raw): fail(f'derived hash drift: {name}')
    print(json.dumps({'status':'PASS','members':len(members)},ensure_ascii=False))
if __name__=='__main__': main()
