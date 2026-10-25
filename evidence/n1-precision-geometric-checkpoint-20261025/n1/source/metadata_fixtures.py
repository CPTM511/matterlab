"""Synthetic control-flow fixtures. No torch import, model, real AD or execution anchor."""
import ast,json,tempfile,types,datetime as dt
from pathlib import Path
import numpy as np
from native_capture import Budget,NativeCapture
import native_gate
from control_common import verify_release
checks=[]
def ok(name,value):
 checks.append({'name':name,'passed':bool(value)})
 if not value:raise AssertionError(name)
def rejects(name,fn):
 try:fn()
 except Exception:ok(name,True)
 else:ok(name,False)
for kind in ['force','stress','added']:
 b=Budget()
 for _ in range(2 if kind=='added' else 1):b.claim(kind)
 rejects('counter_'+kind,lambda:b.claim(kind));rejects('terminal_no_retry_'+kind,lambda:b.claim('force'))
class FakeTensor:
 def __init__(self,value,requires=True):self.a=np.asarray(value);self.requires_grad=requires;self.ndim=self.a.ndim;self.shape=self.a.shape
 def detach(self):return self
 def cpu(self):return self
 def numpy(self):return self.a
 def reshape(self,*shape):return FakeTensor(self.a.reshape(*shape),self.requires_grad)
 def __getitem__(self,j):return FakeTensor(self.a[j],self.requires_grad)
original_gate=native_gate.verify_execution_context;native_gate.verify_execution_context=lambda _b:123
try:
 for mode in ['valid','disconnected','unsupported','nonfinite','unused']:
  calls=[]
  def grad(*args,**kwargs):
   calls.append(kwargs)
   if mode=='unsupported':raise RuntimeError('synthetic unsupported second derivative')
   if mode=='unused':return (None,)
   return (FakeTensor(np.full((20,3),np.nan if mode=='nonfinite' else 1.0)),)
  fake=types.SimpleNamespace(autograd=types.SimpleNamespace(grad=grad))
  with tempfile.TemporaryDirectory() as tmp:
   cap=NativeCapture(fake,None,tmp);cap.positions=[FakeTensor(np.zeros((20,3)))];cap.live_forces=[FakeTensor(np.zeros((20,3)),mode!='disconnected')];cap.budget.counts.update(force=1,stress=1)
   if mode=='valid':
    cap.query_rows();ok('two_rows_only',len(calls)==2 and cap.budget.counts['added']==2);rejects('no_reentry_after_two',cap.query_rows)
   else:
    rejects('stop_'+mode,cap.query_rows);ok('no_fallback_'+mode,len(calls)<=1 and cap.budget.failed);rejects('no_retry_'+mode,cap.query_rows)
finally:native_gate.verify_execution_context=original_gate
with tempfile.TemporaryDirectory() as tmp:
 a=Path(tmp)/'a.npz';b=Path(tmp)/'b.npz';np.savez(a,x=np.array([1.],dtype=np.float32));np.savez(b,x=np.array([2.],dtype=np.float32));rejects('array_mismatch_stops',lambda:native_gate.exact_npz(a,b));np.savez(b,x=np.array([1.],dtype=np.float64));rejects('dtype_mismatch_stops',lambda:native_gate.exact_npz(a,b))
now=dt.datetime(2026,10,24,13,tzinfo=dt.timezone.utc);freeze={'protocol_sha256':'a','implementation_manifest_sha256':'b'}
release={k:True for k in ['parent_released_exact_protocol','ordinary_included_use_allowed','all_displayed_windows_recorded','usage_unambiguous','current_cloud_ownership','no_other_physical_job','fallback_nonoverlap_verified','single_existing_schedule_verified']};release.update(protocol_sha256='a',implementation_manifest_sha256='b',remote_head='c3c089ff893dda65d12713aea49d9a17a08991be',usage_observed_at_utc='2026-10-24T12:55:00Z',ownership_checked_at_utc='2026-10-24T12:55:00Z',included_windows_consumed_fraction=[0.67],extra_spending_allowed=False,investigation_started_at_utc='2026-10-24T12:55:00Z')
ok('fresh_release_metadata',verify_release(release,freeze,now).isoformat()==release['investigation_started_at_utc'].replace('Z','+00:00'))
for key,value in [('included_windows_consumed_fraction',[0.8]),('usage_observed_at_utc','2026-10-24T12:00:00Z'),('investigation_started_at_utc','2026-10-24T12:00:00Z'),('investigation_started_at_utc','2026-10-24T14:00:00Z')]:
 bad=dict(release);bad[key]=value;rejects('release_reject_'+key+'_'+str(value),lambda:verify_release(bad,freeze,now))
root=Path(__file__).parent
for p in root.glob('*.py'):ast.parse(p.read_text());ok('syntax_'+p.name,True)
ok('no_torch_imported','torch' not in __import__('sys').modules)
print(json.dumps({'scope':'Synthetic metadata/control-flow only; fake derivative callback is not autograd or physical evidence','checks':checks,'passed':all(c['passed'] for c in checks),'real_forwards':0,'real_AD_queries':0,'real_attempt_tokens':0},indent=2))
