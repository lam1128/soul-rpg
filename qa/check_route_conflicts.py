#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def fail(msg): raise SystemExit('FAIL: '+msg)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project',default='.'); a=ap.parse_args()
    r=json.loads((Path(a.project)/'runtime/registry.json').read_text(encoding='utf-8'))
    routes=r.get('topic_routes',{})
    act=r.get('interaction_route_activation',[])
    names=[]; fallbacks=[]
    for i,x in enumerate(act):
        n=x.get('route') if isinstance(x,dict) else x
        if not n or n not in routes: fail(f'activation route invalid: {n}')
        names.append(n)
        if isinstance(x,dict) and x.get('fallback'): fallbacks.append((i,n))
    if len(names)!=len(set(names)): fail('duplicate ordinary activation')
    if len(fallbacks)!=1 or fallbacks[0][0] != len(act)-1: fail('exactly one final fallback required')
    skill_controls={k:v for k,v in r.get('control_intents',{}).items() if v.get('dispatch_type')=='skill'}
    for k,v in skill_controls.items():
        if v.get('route') and v['route'] in routes: fail(f'skill control keeps parallel route: {k}')
        if not v.get('skill') or not v.get('operation'): fail(f'skill control incomplete: {k}')
    entries=set(names)
    for v in r.get('control_intents',{}).values():
        if v.get('route'): entries.add(v['route'])
    for route in routes.values():
        for d in route.get('delegates_to',[]) or []:
            if isinstance(d,str): entries.add(d)
            elif isinstance(d,dict) and d.get('route'): entries.add(d['route'])
    entries.update(['governance_boot','ordinary_gameplay_startup'])
    orphan=[n for n in routes if n not in entries]
    if orphan: fail('orphan routes: '+','.join(orphan))
    print(json.dumps({'status':'PASS','ordinary_activation':len(names),'skill_controls':len(skill_controls),'routes':len(routes)},ensure_ascii=False))
if __name__=='__main__': main()
