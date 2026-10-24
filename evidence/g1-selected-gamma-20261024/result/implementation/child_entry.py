"""Future child; import is inert. No evaluation authorized by preparation."""
import ctypes,os,signal,sys,runpy,random
from pathlib import Path

def main():
 if sys.flags.optimize!=0:raise RuntimeError('Optimized Python disables integrity assertions')
 parent,mode,root,out=sys.argv[1:];libc=ctypes.CDLL(None,use_errno=True)
 if libc.prctl(1,signal.SIGKILL,0,0,0)!=0:raise OSError(ctypes.get_errno(),'parent death protection')
 if os.getppid()!=int(parent):raise RuntimeError('Parent exited')
 os.sched_setaffinity(0,{0});random.seed(20261024)
 if mode=='preflight':
  from preflight import main as check
  check(Path(root),Path(out))
 elif mode=='inference':
  from control_common import verify_bundle,read
  bundle=Path(__file__).resolve().parent;freeze=read(bundle/'freeze.json');verify_bundle(bundle,freeze)
  if freeze['status']!='reviewed_for_parent_release':raise ValueError('Unreviewed child entry')
  if int(os.environ['G1_CONTROLLER_PID'])!=int(parent):raise ValueError('Controller binding differs')
  metadata=Path(out+'.preflight-private');metadata.mkdir(exist_ok=False)
  from preflight import main as check
  check(Path(root),metadata)
  import numpy as np
  np.random.seed(20261024);sys.argv=[str(Path(__file__).with_name('gamma_worker.py')),out];runpy.run_path(sys.argv[0],run_name='__main__')
 elif mode=='analyze':
  from analyze_saved import analyze
  analyze(Path(root),Path(out),Path(__file__).parent)
 else:raise ValueError('Unknown mode')
if __name__=='__main__':main()
