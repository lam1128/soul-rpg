#!/usr/bin/env python3
import argparse, json
from pathlib import Path
import yaml

def fail(msg): raise SystemExit('FAIL: '+msg)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project',default='.'); a=ap.parse_args()
    p=Path(a.project); r=json.loads((p/'runtime/registry.json').read_text(encoding='utf-8'))
    sm=r.get('state_model',{})
    if sm.get('schema_owner')!='12_状态存档.md': fail('state schema owner changed')
    owner=sm.get('current_state_owner')
    if owner!='state/current/SOUL_STATE_V1.yaml': fail('current_state_owner mismatch')
    state_path=p/owner
    if not state_path.is_file(): fail('canonical current state missing')
    try: doc=yaml.safe_load(state_path.read_text(encoding='utf-8'))
    except Exception as e: fail(f'current state YAML invalid: {e}')
    if not isinstance(doc,dict): fail('current state must be mapping')
    h=doc.get('SAVE_HEADER',{})
    if h.get('CHECKPOINT_FORMAT_VERSION')!='SOUL_STATE_V1': fail('checkpoint format mismatch')
    if str(h.get('SCHEMA_VERSION'))!='2.1': fail('schema version mismatch')
    if not h.get('ADVENTURE_ID'): fail('ADVENTURE_ID missing')
    if not isinstance(h.get('STATE_REV'),int) or h['STATE_REV'] < 1: fail('STATE_REV invalid')
    if sm.get('persisted_current_source')!='state_model.current_state_owner': fail('Git state not persisted authority')
    if sm.get('project_state_persistence')!='git_main_head': fail('project state persistence is not git_main_head')
    if sm.get('checkpoint_persistence')!='derived_import_export_only_non_authoritative': fail('checkpoint role mismatch')
    ext=r.get('external_sources',{}).get('checkpoint_import')
    if not ext or ext.get('checkpoint_format')!='SOUL_STATE_V1': fail('checkpoint_import source missing')
    if ext.get('role')!='non_authoritative_compatibility_import_candidate': fail('checkpoint_import role must be non-authoritative')
    svc=r.get('internal_services',{}).get('state_commit',{})
    if svc.get('skill')!='soul-rpg-project-maintainer' or svc.get('operation')!='STATE_COMMIT': fail('STATE_COMMIT interface missing')
    controls=r.get('control_intents',{})
    for name in ['LOAD_SAVE','SAVE_EXPORT','STATE_MIGRATION']:
        x=controls.get(name,{})
        if x.get('dispatch_type')!='skill' or x.get('skill')!='soul-rpg-save-manager': fail(f'{name} dispatcher changed')
    ignored=(p/'.gitignore').read_text(encoding='utf-8')
    if 'state/' in {line.strip() for line in ignored.splitlines()}: fail('state directory is ignored by git')
    accidental=[]
    for x in p.rglob('SOUL_STATE_V1.yaml'):
        rel=str(x.relative_to(p))
        if rel!=owner and '.git' not in x.parts: accidental.append(rel)
    if accidental: fail('multiple canonical-like state files: '+','.join(accidental))
    print(json.dumps({'status':'PASS','checkpoint_mode':'git_current_state','state_owner':owner,'state_rev':h['STATE_REV'],'save_skill':'soul-rpg-save-manager'},ensure_ascii=False))
if __name__=='__main__': main()
