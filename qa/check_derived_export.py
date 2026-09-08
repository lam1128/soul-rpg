#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, subprocess
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

def git_head(project: Path):
    try:
        value=subprocess.check_output(['git','-C',str(project),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip().lower()
    except Exception as exc:
        fail(f'cannot resolve Git HEAD: {exc}')
    if len(value)!=40 or any(c not in '0123456789abcdef' for c in value): fail('invalid Git HEAD')
    return value

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
    expected_head=git_head(p)
    if gv.get('source_git_commit_sha')!=expected_head: fail('generated manifest source Git commit mismatch')
    if reg.get('versioning',{}).get('package_manifest_must_embed_source_commit') is not True: fail('registry does not require package source commit identity')
    if reg.get('source_authority',{}).get('compatibility_export_identity')!='generated_view.source_git_commit_sha': fail('compatibility export identity pointer mismatch')
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
    print(json.dumps({'status':'PASS','members':len(members),'manifest':'generated_at_export','source_git_commit_sha':expected_head},ensure_ascii=False))
if __name__=='__main__': main()
