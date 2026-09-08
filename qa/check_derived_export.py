#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json
from pathlib import Path

def sha(b): return hashlib.sha256(b).hexdigest()
def fail(msg): raise SystemExit('FAIL: '+msg)

def load_exporter(project: Path):
    path=project/'scripts/export_runtime_zip.py'
    spec=importlib.util.spec_from_file_location('soul_rpg_export_runtime_zip', path)
    if spec is None or spec.loader is None: fail('cannot load runtime exporter')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project',default='.'); a=ap.parse_args()
    p=Path(a.project).resolve()
    exporter=load_exporter(p)
    raw1,members1=exporter.manifest_bytes(p)
    raw2,members2=exporter.manifest_bytes(p)
    if raw1!=raw2 or members1!=members2: fail('derived manifest generation is not deterministic')
    man=json.loads(raw1)
    reg=json.loads((p/'runtime/registry.json').read_text(encoding='utf-8'))
    cfg=json.loads((p/'compatibility/runtime-members.json').read_text(encoding='utf-8'))
    for key in reg:
        if man.get(key)!=reg[key]: fail(f'generated manifest drift at key {key}')
    gv=man.get('generated_view',{})
    if not gv.get('derived'): fail('generated manifest not marked derived')
    if gv.get('source')!='runtime/registry.json': fail('generated manifest source mismatch')
    if gv.get('state_projection')!='canonical_git_state_excluded_use_external_checkpoint_import': fail('compatibility state projection missing')
    members=cfg['members']
    if members1!=members: fail('exporter member order differs from runtime-members config')
    if 'state/current/SOUL_STATE_V1.yaml' in members: fail('canonical Git state must not be bundled into compatibility runtime')
    if set(man.get('files',{}))!=set(members): fail('generated manifest membership drift')
    manifest_name=cfg['manifest']
    if (p/manifest_name).exists(): fail('generated compatibility manifest must not be persisted in source tree')
    for name in members:
        if name==manifest_name: continue
        raw=(p/name).read_bytes(); meta=man['files'][name]
        if meta.get('bytes')!=len(raw) or meta.get('sha256')!=sha(raw): fail(f'generated hash mismatch: {name}')
    print(json.dumps({'status':'PASS','members':len(members),'manifest':'generated_at_export'},ensure_ascii=False))
if __name__=='__main__': main()
