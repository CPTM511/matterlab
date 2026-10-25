"""One child; parent-death protection and preflight precede model imports."""
import ctypes,os,signal,sys,random,runpy
from pathlib import Path
def main():
 parent,root,out=sys.argv[1:];libc=ctypes.CDLL(None,use_errno=True)
 if libc.prctl(1,signal.SIGKILL,0,0,0)!=0:raise OSError(ctypes.get_errno(),'parent death protection')
 if os.getppid()!=int(parent) or int(os.environ['N1_CONTROLLER_PID'])!=int(parent):raise RuntimeError('Parent mismatch')
 os.sched_setaffinity(0,{0});random.seed(20261024)
 from control_common import verify_bundle,read
 bundle=Path(__file__).resolve().parent;verify_bundle(bundle,read(bundle/'freeze.json'))
 from native_gate import verify_execution_context
 verify_execution_context(bundle)
 metadata=Path(out+'.preflight-private');metadata.mkdir(exist_ok=False)
 from preflight import main as preflight
 preflight(Path(root),metadata)
 from control_common import sha
 baseline=read(bundle/'baseline.json');base=Path(root)/baseline['public_evidence_base']
 for name,v in baseline['files'].items():
  if sha(base/name)!=v['sha256'] or (base/name).stat().st_size!=v['bytes']:raise ValueError('Baseline binding mismatch')
 import numpy as np
 np.random.seed(20261024);sys.argv=[str(bundle/'native_worker.py'),out];runpy.run_path(sys.argv[0],run_name='__main__')
if __name__=='__main__':main()
