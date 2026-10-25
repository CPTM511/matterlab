"""Outer lifecycle owner, outside the controller/worker process group."""
import os,sys,time,json,datetime as dt
from pathlib import Path
import guards as g
from lifecycle import run_guarded

def main():
 if not sys.dont_write_bytecode or sys.flags.optimize:raise ValueError('Safe interpreter flags required')
 release,root,out=sys.argv[1:];r=g.read(release)
 # The immutable release clock is never renewed by this supervisor.
 start=dt.datetime.fromisoformat(r['investigation_start']);remaining=600-(g.now()-start).total_seconds()
 if not 5<remaining<=600:raise ValueError('Insufficient immutable investigation allowance')
 hard=time.monotonic()+remaining;stop=hard-5
 g.paths_gate(root,out,g.BUNDLE);f=g.verify_bundle();g.release_gate(r,f,g.now())
 os.environ['ASSOCIATION_SUPERVISOR_PID']=str(os.getpid())
 receipt=Path(out+'.supervision.json');stdout=Path(out+'.controller-stdout.txt');stderr=Path(out+'.controller-stderr.txt')
 result={'status':'FAILED','start':r['investigation_start'],'execution_completed':False}
 try:
  with stdout.open('xb') as a,stderr.open('xb') as b:
   code,elapsed=run_guarded([sys.executable,'-B',str(g.BUNDLE/'controller.py'),release,root,out],dict(os.environ),a.fileno(),b.fileno(),stop,hard,new_group=True,admit=lambda:g.freshness(r,g.now()))
  result.update(returncode=code,controller_seconds=elapsed)
  if code:raise RuntimeError('Controller failed; no retry')
  if time.monotonic()>=hard:raise RuntimeError('Observed investigation overrun')
  result['status']='CONTROLLER_COMPLETED_REVIEW_PENDING';result['execution_completed']=True
 finally:
  result['terminal']=g.now().isoformat();result['within_immutable_deadline']=time.monotonic()<hard
  # Best-effort terminal receipt: uninterruptible filesystem/scheduler stalls remain uncertified.
  with receipt.open('x') as stream:json.dump(result,stream,indent=2)
if __name__=='__main__':main()
