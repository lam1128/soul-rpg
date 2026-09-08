#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def fail(msg): raise SystemExit('FAIL: '+msg)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project',default='.'); a=ap.parse_args()
    p=Path(a.project).resolve(); r=json.loads((p/'runtime/registry.json').read_text(encoding='utf-8'))
    if r.get('source_authority',{}).get('mode')!='git_first': fail('source_authority.mode')
    if r.get('source_authority',{}).get('branch')!='main': fail('source_authority.branch')
    cur=r.get('current',{})
    for k,v in cur.items():
        if isinstance(v,str) and '#' not in v and not (p/v).exists(): fail(f'current.{k} missing: {v}')
    routes=r.get('topic_routes',{})
    if not routes: fail('topic_routes empty')
    for name,route in routes.items():
        owner=route.get('owner')
        if owner and not (p/owner).exists(): fail(f'route {name} owner missing: {owner}')
        for src in route.get('sources',[]):
            f=src.get('file')
            if f and not (p/f).exists(): fail(f'route {name} source missing: {f}')
    for cid,path in r.get('companion_episode_files',{}).items():
        if not (p/path).is_file(): fail(f'chapter missing {cid}: {path}')
    vals=list(r.get('companion_episode_files',{}).values())
    if len(vals)!=45 or len(set(vals))!=45: fail('companion_episode_files must be 45 unique files')
    print(json.dumps({'status':'PASS','routes':len(routes),'chapters':len(vals)},ensure_ascii=False))
if __name__=='__main__': main()
