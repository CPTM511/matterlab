"""Single-use launcher. No calculation retry path; public recorder bytes are unchanged."""
import os,sys,json,hashlib,time,subprocess
from pathlib import Path
from datetime import datetime,timezone
P=Path(os.environ['MATTERLAB_VALIDATION_OUTPUT']);R=Path(os.environ['MATTERLAB_ROOT'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
assert sha(P/'protocol.json')==json.loads((P/'protocol-freeze.json').read_text())['sha256']
protocol=json.loads((P/'protocol.json').read_text())
assert sha(Path(__file__))==protocol['launcher_sha256']
recorder=R/'evidence/diagnosis-20261023/diagnostic_eval_proposed.py'
assert sha(recorder)==protocol['recorder_sha256']
assert json.loads((P/'preflight.json').read_text())['passed']
assert subprocess.check_output(['git','-C',str(R),'ls-remote','origin','refs/heads/main'],text=True).split()[0]==protocol['public_checkpoint']
assert subprocess.check_output(['git','-C',str(R),'status','--porcelain'],text=True).strip()==''
# O_EXCL token prevents a second attempt even after interruption or failed inference.
with (P/'ATTEMPT-STARTED.json').open('x') as f:json.dump({'utc':datetime.now(timezone.utc).isoformat(),'maximum_attempts':1},f)
env=dict(os.environ)
for key in ['ATEN_CPU_CAPABILITY','MKL_CBWR']:env.pop(key,None)
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS']:env[key]='1'
env.update(MATTERLAB_ROOT=str(R),MATTERLAB_EXPECTED_CODE=str(R/'evidence/restoration-20261023/replay/code.json'),MATTERLAB_CONDITION=protocol['id'],PYTHONHASHSEED='20261024',PYTHONPATH=str(R/'src'),PYTHONDONTWRITEBYTECODE='1')
bootstrap="import os,sys,random,runpy; os.sched_setaffinity(0,"+repr(protocol['resource_limits']['cpu_affinity'])+"); random.seed(20261024); import numpy as np; np.random.seed(20261024); sys.path.insert(0,"+repr(str(recorder.parent))+"); sys.argv=["+repr(str(recorder))+","+repr(str(P/'R1'))+"]; runpy.run_path(sys.argv[0],run_name='__main__')"
start=time.monotonic();result={'started_at_utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':sha(P/'protocol.json'),'maximum_calculation_seconds':600,'attempts':1,'timeout':False}
with (P/'calculation.log').open('wb') as log:
    try:
        completed=subprocess.run([sys.executable,'-c',bootstrap],env=env,cwd=P,stdout=log,stderr=subprocess.STDOUT,timeout=600)
        result['returncode']=completed.returncode
    except subprocess.TimeoutExpired:result.update(timeout=True,returncode=None)
    except Exception as exc:result.update(exception=repr(exc),returncode=None)
result.update(wall_seconds=time.monotonic()-start,ended_at_utc=datetime.now(timezone.utc).isoformat())
save('execution.json',result)
print(json.dumps(result))
