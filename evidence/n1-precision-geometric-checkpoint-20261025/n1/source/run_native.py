"""One-shot future controller. No execution during preparation; exact release required."""
import argparse,datetime as dt,json,os,sys,time,signal
from pathlib import Path
from control_common import *
from native_gate import ANCHOR

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--release',type=Path,required=True);parser.add_argument('--execute-once',action='store_true',required=True);a=parser.parse_args()
 if sys.flags.optimize or not sys.dont_write_bytecode:raise ValueError('Use reviewed -B launcher, no optimization')
 bundle=Path(__file__).resolve().parent;freeze=read(bundle/'freeze.json');verify_bundle(bundle,freeze)
 if freeze['status']!='reviewed_for_parent_release':raise ValueError('Execution blocked pending independent review')
 release=read(a.release);start=verify_release(release,freeze,dt.datetime.now(dt.timezone.utc))
 if release.get('frozen_bundle_private')!=str(bundle):raise ValueError('Wrong fixed bundle')
 root=a.root.resolve();out=a.output.resolve()
 if out.is_relative_to(root) or out.is_relative_to(bundle) or root.is_relative_to(out) or bundle.is_relative_to(out):raise ValueError('Unsafe output location')
 remaining=lambda:1800-(dt.datetime.now(dt.timezone.utc)-start).total_seconds()
 def deadline(_sig,_frame):raise TimeoutError('Immutable all-role deadline')
 signal.signal(signal.SIGALRM,deadline);signal.setitimer(signal.ITIMER_REAL,max(0.001,remaining()))
 local_coordination(root,remaining());remote_head(root,remaining())
 out.mkdir(parents=True,exist_ok=False);check_live_processes(out)
 old_anchor=Path('REDACTED_PRIVATE_PATH_4')
 if sha(old_anchor)!='6a495f91bac3f238d64861ea1b3be21032bc0f346767946c0c9ba84467c603fd':raise ValueError('Closed G1 anchor changed')
 claim_attempt(ANCHOR,{'start':release['investigation_started_at_utc'],'controller_pid':os.getpid(),'maximum_forwards':1,'maximum_added_queries':2})
 save(out/'release-private.json',release);record={}
 env=os.environ.copy();env.pop('MKL_CBWR',None)
 env.update(PYTHONOPTIMIZE='0',PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='20261024',ATEN_CPU_CAPABILITY='default',PYTHONPATH=str(root/'src'),MATTERLAB_ROOT=str(root),MATTERLAB_EXPECTED_CODE=str(root/'evidence/restoration-20261023/replay/code.json'),MATTERLAB_CONDITION=PROTOCOL_ID,N1_RELEASE=str(a.release.resolve()),N1_CONTROLLER_PID=str(os.getpid()))
 for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:env[k]='1'
 try:
  verify_bundle(bundle,freeze);current=read(a.release);verify_release(current,freeze,dt.datetime.now(dt.timezone.utc))
  if current['investigation_started_at_utc']!=release['investigation_started_at_utc'] or current.get('frozen_bundle_private')!=str(bundle):raise ValueError('Immutable release changed')
  local_coordination(root,remaining());remote_head(root,remaining())
  claim_attempt(out/'launch-attempt.json',{'controller_pid':os.getpid(),'maximum_launches':1})
  with (out/'calculation.log').open('w') as log:run_bounded([sys.executable,'-B',str(bundle/'native_child.py'),str(os.getpid()),str(root),str(out/'raw')],seconds=min(600,remaining()),env=env,cwd=root,log=log,record=record)
  if record['returncode']!=0 or not (0<=record['wall_seconds']<=600) or remaining()<=0:raise RuntimeError('Terminal child/resource failure')
  record['status']='completed_pending_independent_review'
 except BaseException:
  record['status']='terminal_failure_no_retry';raise
 finally:
  record['investigation_start']=release['investigation_started_at_utc'];record['investigation_elapsed_seconds']=1800-remaining();save(out/'execution-private.json',record)
if __name__=='__main__':main()
