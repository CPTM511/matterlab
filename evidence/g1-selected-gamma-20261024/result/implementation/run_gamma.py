"""Reviewed future batch controller. No inference unless exact frozen release passes."""
import argparse,datetime as dt,os,sys,time,traceback,shutil
from pathlib import Path
from control_common import *

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--release',type=Path,required=True);parser.add_argument('--execute-once',action='store_true',required=True);args=parser.parse_args()
 if sys.flags.optimize!=0:raise RuntimeError('Optimized Python disables integrity assertions')
 os.sched_setaffinity(0,{0})
 bundle=Path(__file__).resolve().parent;freeze=read(bundle/'freeze.json');verify_bundle(bundle,freeze)
 if freeze['status']!='reviewed_for_parent_release':raise ValueError('Not reviewed/released')
 release=read(args.release);started=verify_release(release,freeze,dt.datetime.now(dt.timezone.utc))
 if release.get('frozen_bundle_private')!=str(bundle):raise ValueError('Release not bound to this exact bundle location')
 root=args.root.resolve();out=args.output.resolve()
 if out.is_relative_to(root) or out.is_relative_to(bundle):raise ValueError('Separate output required')
 guard=Path('<PRIVATE_WORKSPACE_PATH>')/(PROTOCOL_ID+'.attempt.json');claim_attempt(guard,{'maximum_evaluations':32,'start':started.isoformat(),'controller_pid':os.getpid()})
 out.mkdir(parents=True,exist_ok=False);save(out/'release-private.json',release)
 env=dict(os.environ)
 for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS']:env[key]='1'
 env.pop('MKL_CBWR',None);env.update(PYTHONOPTIMIZE='0',ATEN_CPU_CAPABILITY='default',PYTHONHASHSEED='20261024',PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(root/'src'),MATTERLAB_ROOT=str(root),MATTERLAB_EXPECTED_CODE=str(root/'evidence/restoration-20261023/replay/code.json'),MATTERLAB_CONDITION=PROTOCOL_ID,G1_RELEASE=str(args.release.resolve()),G1_STARTED=release['investigation_started_at_utc'],G1_CONTROLLER_PID=str(os.getpid()))
 os.environ.update(env)
 calc_seconds=0.;records=[];completed=False
 def deadline(*_):raise TimeoutError('Investigation wall-clock deadline')
 signal.signal(signal.SIGALRM,deadline)
 signal.setitimer(signal.ITIMER_REAL,max(.001,1800-(dt.datetime.now(dt.timezone.utc)-started).total_seconds()-6))
 def fresh():
  current=read(args.release);verify_release(current,freeze,dt.datetime.now(dt.timezone.utc))
  if current['investigation_started_at_utc']!=release['investigation_started_at_utc'] or current.get('frozen_bundle_private')!=str(bundle):raise ValueError('Release binding/start changed')
 def remaining():return 1800-(dt.datetime.now(dt.timezone.utc)-started).total_seconds()
 def gates():
  verify_bundle(bundle,freeze);r=read(args.release);verify_release(r,freeze,dt.datetime.now(dt.timezone.utc))
  if r['investigation_started_at_utc']!=release['investigation_started_at_utc']:raise ValueError('Start changed')
  remote_head(root,remaining());local_coordination(root,remaining());check_live_processes(out);fresh()
 try:
  gates()
  shutil.copytree(bundle,out/'implementation',ignore=shutil.ignore_patterns('__pycache__'))
  with (out/'preflight.log').open('wb') as log:
   pre=run_bounded([sys.executable,str(bundle/'child_entry.py'),str(os.getpid()),'preflight',str(root),str(out)],seconds=min(120,remaining()-6),env=env,cwd=out,log=log)
  save(out/'preflight-execution.json',pre)
  if pre['returncode']!=0:raise ValueError('Preflight failed')
  points=read(bundle/'points.json');assert len(points)==32
  for index,point in enumerate(points):
   gates();claim_attempt(out/(point['id']+'.attempt.json'),{'index':index,'point_id':point['id'],'controller_pid':os.getpid()})
   pp=out/(point['id']+'.input.json');save(pp,point);env['G1_POINT']=str(pp);record={'index':index,'point_id':point['id']};records.append(record)
   try:
    fresh()
    with (out/(point['id']+'.log')).open('wb') as log:
     run_bounded([sys.executable,str(bundle/'child_entry.py'),str(os.getpid()),'inference',str(root),str(out/point['id'])],seconds=min(600-calc_seconds,remaining())-6,env=env,cwd=out,log=log,record=record)
   finally:
    calc_seconds+=record.get('wall_seconds',0);save(out/'execution.json',{'records':records,'total_calculation_process_seconds':calc_seconds,'complete':False})
   if record['returncode']!=0 or calc_seconds>600:raise ValueError('Point failed/resource exceeded; no retry')
   from point_checks import validate_point,check_repeat
   validate_point(out/point['id'],point,root)
   if 'repeat_of' in point:
    from point_checks import save_repeat_differences
    save_repeat_differences(out/point['id'],out/point['repeat_of'],out/(point['id']+'.signed-repeat.json'))
    check_repeat(out/point['id'],out/point['repeat_of'])
  with (out/'analysis.log').open('wb') as log:
   ar=run_bounded([sys.executable,str(bundle/'child_entry.py'),str(os.getpid()),'analyze',str(root),str(out)],seconds=min(120,remaining()-6),env=env,cwd=out,log=log)
  save(out/'analysis-execution.json',ar)
  if ar['returncode']!=0:raise ValueError('Analysis integrity failed')
  if calc_seconds>600 or remaining()<0:raise TimeoutError('Final elapsed budget failed')
  completed=True
 except BaseException:
  (out/'failure.txt').write_text(traceback.format_exc());raise
 finally:
  if (out/'decision.json').exists():
   raw=read(out/'decision.json');save(out/'raw-analysis-decision.json',raw)
   eligible=completed and calc_seconds<=600 and remaining()>=0
   save(out/'final-decision.json',{'execution_eligible':False,'execution_checks_observed_passed':eligible,'status':'Requires independent terminal execution and saved-evidence review; no automatic scientific acceptance','scientific_decision':None,'raw_analysis_retained':True,'full_migration_complete':False})
  save(out/'execution.json',{'records':records,'total_calculation_process_seconds':calc_seconds,'complete':completed,'investigation_elapsed_seconds':1800-remaining()})
  save(out/'manifest.json',{'algorithm':'SHA256','files':{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p!=out/'manifest.json'}})
  signal.setitimer(signal.ITIMER_REAL,0)
if __name__=='__main__':main()
