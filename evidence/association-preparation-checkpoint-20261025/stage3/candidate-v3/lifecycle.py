"""POSIX supervision of fixed child commands; no scientific imports."""
import os,time,signal,ctypes
class SupervisionError(RuntimeError):pass

def run_guarded(command,env,stdout,stderr,stop_at,hard_end,*,new_group,admit):
 """Keep spawn/exec in the child; supervise from an independent runnable parent.
 No hard-real-time guarantee is made. Any observed overrun is rejected.
 """
 start=time.monotonic();admit()
 if not start<stop_at<hard_end:raise SupervisionError('No reserved cleanup time')
 parent=os.getpid();pid=os.fork()
 if pid==0:
  try:
   if new_group:os.setsid()
   libc=ctypes.CDLL(None,use_errno=True)
   if libc.prctl(1,signal.SIGKILL,0,0,0)!=0 or os.getppid()!=parent:os._exit(124)
   os.dup2(stdout,1);os.dup2(stderr,2)
   os.execve(command[0],command,env)
  except BaseException:os._exit(125)
 group=pid if new_group else os.getpgrp();status=None;timed_out=False
 try:
  while True:
   got,value=os.waitpid(pid,os.WNOHANG)
   if got:status=value;break
   if time.monotonic()>=stop_at:
    timed_out=True;break
   time.sleep(min(.005,max(0,stop_at-time.monotonic())))
 finally:
  if status is None:
   # An inherited job group includes its controller: timeout stops the entire attempt.
   try:os.killpg(group,signal.SIGKILL)
   except ProcessLookupError:pass
   try:os.kill(pid,signal.SIGKILL)
   except ProcessLookupError:pass
   while time.monotonic()<hard_end:
    got,value=os.waitpid(pid,os.WNOHANG)
    if got:status=value;break
    time.sleep(.005)
 if status is None:raise SupervisionError('Cleanup unconfirmed before hard deadline')
 elapsed=time.monotonic()-start
 if time.monotonic()>hard_end:raise SupervisionError('Observed lifecycle overrun')
 if new_group:
  try:os.killpg(group,0)
  except ProcessLookupError:pass
  else:
   os.killpg(group,signal.SIGKILL)
   raise SupervisionError('Surviving group; termination requested, cleanup unconfirmed')
 if timed_out:raise SupervisionError('Supervised timeout; no retry')
 return os.waitstatus_to_exitcode(status),elapsed
