#!/usr/bin/env python3
import hashlib, json, sys, zipfile
from pathlib import Path
MANIFEST='魂师修炼RPG_manifest.json'
def sha256(b): return hashlib.sha256(b).hexdigest()
def valid_git_sha(value):
    return isinstance(value,str) and len(value)==40 and all(c in '0123456789abcdef' for c in value.lower())
def main():
    if len(sys.argv)!=2: raise SystemExit('usage: audit_runtime_package.py <runtime.zip>')
    path=Path(sys.argv[1])
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if MANIFEST not in names: raise SystemExit('FAIL: manifest missing')
        if len(names)!=len(set(names)): raise SystemExit('FAIL: duplicate zip members')
        data=json.loads(z.read(MANIFEST))
        gv=data.get('generated_view',{})
        if not gv.get('derived'): raise SystemExit('FAIL: manifest is not derived view')
        source_sha=gv.get('source_git_commit_sha')
        if not valid_git_sha(source_sha): raise SystemExit('FAIL: exact source Git commit identity missing')
        if data.get('versioning',{}).get('package_manifest_must_embed_source_commit') is not True: raise SystemExit('FAIL: package source commit requirement missing')
        if data.get('source_authority',{}).get('compatibility_export_identity')!='generated_view.source_git_commit_sha': raise SystemExit('FAIL: compatibility export identity pointer mismatch')
        registered=set(data.get('files',{})); actual=set(names)
        if registered!=actual:
            print('FAIL: membership mismatch'); print('unregistered:',sorted(actual-registered)); print('missing:',sorted(registered-actual)); raise SystemExit(2)
        failures=[]
        for name,meta in data['files'].items():
            if name==MANIFEST: continue
            raw=z.read(name)
            if meta.get('bytes')!=len(raw): failures.append((name,'bytes'))
            if meta.get('sha256')!=sha256(raw): failures.append((name,'sha256'))
        routes=data.get('topic_routes',{})
        ordinary=data.get('interaction_route_activation',[])
        entries=set()
        for item in ordinary:
            if isinstance(item,str): entries.add(item)
            elif isinstance(item,dict) and item.get('route'): entries.add(item['route'])
        for v in data.get('control_intents',{}).values():
            if v.get('route'): entries.add(v['route'])
        for r in routes.values():
            for d in r.get('delegates_to',[]) or []:
                if isinstance(d,str): entries.add(d)
                elif isinstance(d,dict) and d.get('route'): entries.add(d['route'])
        entries.update(['governance_boot','ordinary_gameplay_startup'])
        orphan=[r for r in routes if r not in entries]
        if failures or orphan:
            print('FAIL')
            if failures: print('hash/size:',failures)
            if orphan: print('orphan routes:',orphan)
            raise SystemExit(3)
        skills={v.get('skill') for v in data.get('control_intents',{}).values() if v.get('dispatch_type')=='skill'}
        print(json.dumps({'status':'PASS','release':data.get('release'),'source_git_commit_sha':source_sha,'members':len(names),'routes':len(routes),'skill_dispatches':sorted(s for s in skills if s),'control_intents':len(data.get('control_intents',{}))},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
