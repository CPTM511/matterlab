"""Future child; never run during implementation preparation."""
import ctypes,os,signal,sys,random,runpy
from pathlib import Path
def main():
 signal.pthread_sigmask(signal.SIG_UNBLOCK,{signal.SIGALRM,signal.SIGTERM})
 if not sys.dont_write_bytecode or sys.flags.optimize:raise ValueError('Bytecode enabled')
 parent,root,out=sys.argv[1:];libc=ctypes.CDLL(None,use_errno=True)
 if libc.prctl(1,signal.SIGKILL,0,0,0)!=0:raise OSError(ctypes.get_errno(),'parent death protection')
 if os.getppid()!=int(parent) or int(os.environ['ASSOCIATION_CONTROLLER_PID'])!=int(parent):raise RuntimeError('Parent mismatch')
 os.sched_setaffinity(0,{0});random.seed(20261024)
 from native_gate import verify_execution_context,references
 import guards as g
 release=verify_execution_context(g.BUNDLE)
 expected=Path(release['output'])/os.environ['ASSOCIATION_CONDITION']
 if str(Path(root).resolve())!=release['root'] or Path(out).resolve()!=expected:raise ValueError('Child argument binding mismatch')
 references(Path(root))
 metadata=Path(out+'.preflight-private');metadata.mkdir(exist_ok=False)
 from preflight import main as preflight
 preflight(Path(root),metadata)
 verify_execution_context(g.BUNDLE)
 import numpy as np
 np.random.seed(20261024)
 sys.argv=[str(g.BUNDLE/'worker.py'),out];runpy.run_path(sys.argv[0],run_name='__main__')
if __name__=='__main__':main()
