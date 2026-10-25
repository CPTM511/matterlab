"""Future exclusive two-condition controller. Importing does not launch anything."""
import os,sys,json,time,subprocess,signal,datetime as dt,traceback,math
from pathlib import Path
import guards as g
INTERPRETER=Path('PRIVATE_PATH_ALIAS_1')
ACTIVE_CHILD=None
def kill_group(p):
 if p is not None:
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  try:p.wait(timeout=1.)
  except subprocess.TimeoutExpired:raise RuntimeError('Cleanup reap unconfirmed; no retry')
def deadline_stop(signum,frame):
 kill_group(ACTIVE_CHILD)
 raise TimeoutError('Immutable investigation deadline/termination')

INTERPRETER_SHA='fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7'
class Sequence:
 def __init__(self):self.launched=[];self.completed=[];self.seconds=0.;self.failed=False
 def before(self,c,remaining):
  if type(remaining) not in (int,float) or not math.isfinite(remaining):self.failed=True;raise ValueError('Invalid remaining time')
  if self.failed or c not in ('control','altered') or self.launched!=self.completed or self.launched!=list(('control','altered')[:len(self.launched)]) or len(self.launched)>=2:raise ValueError('Sequence/terminal gate')
  if c!=('control','altered')[len(self.launched)] or remaining<=0 or self.seconds>=120:raise ValueError('Order/resource gate')
  self.launched.append(c)
  return min(60.,120.-self.seconds,remaining)
 def after(self,c,elapsed,ok):
  if type(elapsed) not in (int,float) or not math.isfinite(elapsed) or type(ok) is not bool:self.failed=True;raise ValueError('Invalid process receipt')
  self.seconds+=elapsed
  if not ok or elapsed<0 or elapsed>60 or self.seconds>120 or not self.launched or self.launched[-1]!=c or c in self.completed:self.failed=True;raise ValueError('Terminal process/resource failure')
  self.completed.append(c)

def main():
 global ACTIVE_CHILD
 if not sys.dont_write_bytecode or sys.flags.optimize:raise ValueError('Use launch.sh with -B and assertions enabled')
 release_path,root_arg,out_arg=sys.argv[1:];root=Path(root_arg).resolve();out=Path(out_arg).resolve()
 os.environ['ASSOCIATION_RELEASE']=str(Path(release_path).resolve());os.environ['ASSOCIATION_CONTROLLER_PID']=str(os.getpid());os.environ['ASSOCIATION_OUTPUT']=str(out);os.environ['MATTERLAB_ROOT']=str(root)
 r=g.read(release_path);prestart=dt.datetime.fromisoformat(r['investigation_start']);remaining=600-(g.now()-prestart).total_seconds()
 if not 0<remaining<=600:raise ValueError('Expired/future start')
 signal.signal(signal.SIGALRM,deadline_stop);signal.signal(signal.SIGTERM,deadline_stop);signal.setitimer(signal.ITIMER_REAL,remaining)
 f=g.verify_bundle();start=g.release_gate(r,f,g.now())
 if r['output']!=str(out) or r['root']!=str(root):raise ValueError('Release paths')
 g.paths_gate(root,out,g.BUNDLE)
 if g.sha(INTERPRETER.resolve())!=INTERPRETER_SHA or Path(sys.executable).resolve()!=INTERPRETER.resolve():raise ValueError('Interpreter identity')
 g.coordination(root)
 from native_gate import references
 references(root)
 g.release_gate(g.read(release_path),f,g.now());release_hash=g.sha(release_path)
 g.claim(g.ANCHOR,{'controller_pid':os.getpid(),'investigation_start':r['investigation_start'],'freeze_sha256':g.sha(g.BUNDLE/'freeze.json'),'release_sha256':release_hash})
 out.mkdir(exist_ok=False);sequence=Sequence();status='FAILED';failure=None
 env=os.environ.copy();env.update({'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'20261024','ATEN_CPU_CAPABILITY':'default','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1','VECLIB_MAXIMUM_THREADS':'1','MATTERLAB_EXPECTED_CODE':str(root/'evidence/restoration-20261023/replay/code.json')});env.pop('MKL_CBWR',None)
 try:
  for c in ('control','altered'):
   if g.sha(release_path)!=release_hash:raise ValueError('Release changed after admission')
   g.verify_bundle();g.release_gate(g.read(release_path),f,g.now());g.coordination(root);references(root)
   if c=='altered' and g.read(out/'control'/'point-complete.json')!={'passed':True,'condition':'control'}:raise ValueError('Control not passed')
   remaining=600-(g.now()-start).total_seconds();limit=sequence.before(c,remaining)
   g.claim(out/(c+'-launch.json'),{'condition':c,'timeout_seconds':limit,'utc':g.now().isoformat()})
   childenv=dict(env,ASSOCIATION_CONDITION=c,MATTERLAB_CONDITION='association-'+c)
   began=time.monotonic();p=None;ok=False
   try:
    with (out/(c+'-stdout.txt')).open('wb') as stdout,(out/(c+'-stderr.txt')).open('wb') as stderr:
     oldmask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM,signal.SIGTERM})
     try:
      p=subprocess.Popen([str(INTERPRETER),'-B',str(g.BUNDLE/'child.py'),str(os.getpid()),str(root),str(out/c)],env=childenv,stdout=stdout,stderr=stderr,start_new_session=True)
      ACTIVE_CHILD=p
     finally:signal.pthread_sigmask(signal.SIG_SETMASK,oldmask)
     try:
      wait_remaining=limit-(time.monotonic()-began)
      if wait_remaining<=0:raise TimeoutError('Spawn consumed process allowance')
      code=p.wait(timeout=wait_remaining)
      try:os.killpg(p.pid,0)
      except ProcessLookupError:pass
      else:kill_group(p);raise RuntimeError('Surviving child process group')
     except BaseException:
      kill_group(p);raise
     finally:ACTIVE_CHILD=None
     ok=code==0
   finally:
    elapsed=time.monotonic()-began
    (out/(c+'-process.json')).write_text(json.dumps({'seconds':elapsed,'returncode':None if p is None else p.returncode,'passed':ok})+'\n')
    sequence.after(c,elapsed,ok)
    if elapsed>limit:raise TimeoutError('Actual process allowance exceeded')
   if g.read(out/c/'point-complete.json')!={'passed':True,'condition':c}:raise ValueError('Point gate missing')
  g.release_gate(g.read(release_path),f,g.now())
  from comparator import main as compare
  compare(out);g.release_gate(g.read(release_path),f,g.now());status='CAPTURE_COMPLETE_REVIEW_PENDING'
 except BaseException:
  sequence.failed=True;failure=traceback.format_exc();(out/'failure.txt').write_text(failure);raise
 finally:
  (out/'terminal.json').write_text(json.dumps({'status':status,'sequence':sequence.__dict__,'start':r['investigation_start'],'terminal':g.now().isoformat(),'failure':failure},indent=2)+'\n')
  (out/'manifest.json').write_text(json.dumps({'files':{str(p.relative_to(out)):g.sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p!=out/'manifest.json'}},indent=2)+'\n')
if __name__=='__main__':main()
