"""Shrink JSON by deleting fields or array elements while preserving an observed failure."""
import argparse,copy,json,math,re,subprocess,tempfile,sys
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument("input",type=Path)
p.add_argument("-o",type=Path,required=True)
p.add_argument("--match",help="required regex on combined stdout/stderr (default: exact last nonblank line)")
p.add_argument("--timeout",type=float,default=10)
p.add_argument("--runs",type=int,default=500,help="maximum total predicate invocations")
if "--" not in sys.argv: p.error("separate the test command with --")
sep=sys.argv.index("--")
a=p.parse_args(sys.argv[1:sep])
cmd=sys.argv[sep+1:]
if not cmd or "{}" not in cmd or a.input.resolve()==a.o.resolve() or a.runs<1 or a.timeout<=0: p.error("need distinct output, positive limits, and a literal {} argument for the candidate")
root=json.loads(a.input.read_bytes())
rx=re.compile(a.match) if a.match else None
runs=0
with tempfile.TemporaryDirectory() as folder:
    candidate=Path(folder,"candidate.json")
    def signature(value):
        global runs
        runs+=1
        candidate.write_text(json.dumps(value,ensure_ascii=False),encoding="utf8")
        try: res=subprocess.run([str(candidate) if s=="{}" else s for s in cmd],capture_output=True,timeout=a.timeout)
        except subprocess.TimeoutExpired: return None
        if not res.returncode: return None
        lines=(res.stdout+b"\n"+res.stderr).decode("utf8","replace").strip()
        if rx: return (res.returncode,rx.pattern) if rx.search(lines) else None
        return (res.returncode,lines.splitlines()[-1]) if lines else None
    wanted=signature(root)
    if wanted is None: p.error("input did not reproduce a nonzero failure with a matching signature")
    def at(value,path):
        for k in path: value=value[k]
        return value
    pending=[()]
    while pending and runs<a.runs:
        path=pending.pop()
        node=at(root,path)
        if not isinstance(node,(dict,list)): continue
        width=len(node)
        while width and runs<a.runs:
            keys=list(node) if isinstance(node,dict) else list(range(len(node)))
            accepted=False
            for i in range(0,len(keys),width):
                trial=copy.deepcopy(root)
                target=at(trial,path)
                for k in reversed(keys[i:i+width]): del target[k]
                if signature(trial)==wanted:
                    root,node=trial,target
                    accepted=True
                    break
                if runs>=a.runs: break
            if not accepted: width=0 if width==1 else math.ceil(width/2)
        pending.extend(path+(k,) for k in (node if isinstance(node,dict) else range(len(node))))
    a.o.write_text(json.dumps(root,ensure_ascii=False),encoding="utf8")
    print(f"{runs} predicate runs; {a.o.stat().st_size} bytes",file=sys.stderr)
