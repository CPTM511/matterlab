import sys,importlib.util,tempfile,json,hashlib,types
from pathlib import Path
from datetime import datetime,timezone,timedelta
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent.parent
sp=importlib.util.spec_from_file_location('synthetic_launch',R/'launch.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
checks=[]
def test(n,f,raises=False):
 try:v=f()
 except Exception as e:checks.append({'name':n,'pass':raises,'exception':type(e).__name__});return
 checks.append({'name':n,'pass':not raises and v is not False})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='launcher-fixture-',dir=R/'reviewer') as td:
 root=Path(td);(root/'reviewer').mkdir();m.ROOT=root;m.SOURCE=root/'never-read-real-inputs'
 for n in ('audit.py','fixtures.py','launch.py'):(root/n).write_bytes((R/n).read_bytes())
 t=datetime(2030,1,1,tzinfo=timezone.utc);m.now=lambda:t
 stage={'start':(t-timedelta(seconds=1)).isoformat(),'deadline':(t+timedelta(seconds=500)).isoformat(),'usage_observation':(t-timedelta(seconds=10)).isoformat(),'freshness_deadline':(t+timedelta(seconds=600)).isoformat()}
 (root/'stage-private.json').write_text(json.dumps(stage))
 review={'outcome':'PASS','stage_private_sha256':sha(root/'stage-private.json'),'approved_files':{n:sha(root/n) for n in ('audit.py','fixtures.py','launch.py')}}
 rp=root/'reviewer/preexecution-review.json';rp.write_text(json.dumps(review))
 expected={'native-row-50.npz':'9f266858e0d1c5c1164241a8425099ebec0c9c8305f7ea5803cb0f9c4369e328','native-row-59.npz':'fe30ec0c926385cd412cdd39bb5e316e5445398046c68e342de842b1c910854f'}
 m.sha=lambda p:expected[p.name] if p.parent==m.SOURCE else sha(p)
 test('synthetic_gate_pass',lambda:m.gates()==stage)
 for key,value in [('stage_private_sha256','0'*64),('outcome','FAIL'),('approved_files',{'audit.py':review['approved_files']['audit.py']})]:
  bad=dict(review);bad[key]=value;rp.write_text(json.dumps(bad));test('reject_'+key,m.gates,True)
 rp.write_text(json.dumps(review))
 p=root/'audit.py';original=p.read_bytes();p.write_bytes(original+b'\n');test('source_mutation',m.gates,True);p.write_bytes(original)
 cache=root/'__pycache__';cache.mkdir();test('bytecode_rejected',m.gates,True);cache.rmdir()
 p=root/'unexpected.py';p.write_text('');test('extra_source_rejected',m.gates,True);p.unlink()
 for name,delta in [('before_start',-2),('insufficient_reserve',400),('past_deadline',501)]:
  m.now=lambda delta=delta:t+timedelta(seconds=delta);test(name,m.gates,True)
 m.now=lambda:t
 # Exercise terminal logic with no subprocess and synthetic invocation only.
 m.subprocess.run=lambda *args,**kw:types.SimpleNamespace(returncode=0)
 times=iter([0,61]);m.time.monotonic=lambda:next(times)
 test('elapsed_over_cap_rejected',m.main,True)
 receipt=json.loads((root/'process-receipt.json').read_text());test('resource_failure_preserved',lambda:receipt['status']=='failed' and bool(receipt['resource_failure']))
 test('exclusive_no_retry',m.main,True)
print(json.dumps({'launcher_sha256':sha(R/'launch.py'),'real_input_read':False,'real_process_launched':False,'passed':sum(x['pass'] for x in checks),'total':len(checks),'checks':checks},indent=2))
