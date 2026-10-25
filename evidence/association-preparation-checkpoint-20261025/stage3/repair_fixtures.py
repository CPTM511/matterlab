import sys,os,time,json,datetime as dt,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;C=R/'candidate-v3';sys.path.insert(0,str(C))
import lifecycle,guards
checks=[];began=time.monotonic()
for name,code,expected in [('normal','pass',True),('stalled_execution','import time;time.sleep(30)',False),('terminal_stall','import time;print("DUMMY_COMPLETE",flush=True);time.sleep(30)',False)]:
 start=time.monotonic();passed=False;error=None
 with (R/(name+'.stdout')).open('xb') as out,(R/(name+'.stderr')).open('xb') as err:
  try:
   status,elapsed=lifecycle.run_guarded([sys.executable,'-B','-c',code],dict(os.environ),out.fileno(),err.fileno(),start+.2,start+.75,new_group=True,admit=lambda:None)
   passed=expected and status==0
  except lifecycle.SupervisionError as e:error=str(e);passed=not expected and error=='Supervised timeout; no retry'
 checks.append({'name':name,'passed':passed,'elapsed':time.monotonic()-start,'error':error})
t=dt.datetime(2030,1,1,tzinfo=dt.timezone.utc)
r={'usage_observed_at':(t-dt.timedelta(seconds=899)).isoformat(),'ownership_observed_at':t.isoformat(),'investigation_start':t.isoformat()}
for name,advance,expected in [('fresh_now',0,True),('expired_after_metadata',2,False),('investigation_expired',600,False)]:
 try:guards.freshness(r,t+dt.timedelta(seconds=advance));passed=expected
 except ValueError:passed=not expected
 checks.append({'name':name,'passed':passed})
result={'scope':'3 dummy child processes and synthetic timestamps; no scientific imports or entrypoint','all_pass':all(x['passed'] for x in checks),'checks':checks,'elapsed_seconds':time.monotonic()-began,'within_8_second_fixture_bound':time.monotonic()-began<=8,'source_hashes':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['lifecycle.py','guards.py']},'limits':'Does not test stalled fork, uninterruptible I/O, real controller/supervisor entrypoint, native model or hard-real-time guarantees.'}
(R/'fixture-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
