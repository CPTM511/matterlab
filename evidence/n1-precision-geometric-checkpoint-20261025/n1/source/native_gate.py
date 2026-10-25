"""Exact baseline gate and forward permission; imports do not load a model."""
import os,json,datetime as dt
from pathlib import Path
from control_common import read,sha,verify_bundle,verify_release,claim_attempt
BASE=Path('evidence/g1-selected-gamma-20261024/result/R-CaTiO3__base')
ANCHOR=Path('N1_PREPARATION/execution-guard/N1-native-reference-curvature-20261024.attempt.json')
def exact_npz(actual,expected):
 import numpy as np
 with np.load(actual,allow_pickle=False) as a,np.load(expected,allow_pickle=False) as b:
  if set(a.files)!=set(b.files):raise ValueError('Array keys mismatch')
  for k in a.files:
   x,y=a[k],b[k]
   if x.dtype!=y.dtype or x.shape!=y.shape or x.tobytes()!=y.tobytes() or not np.isfinite(x).all():raise ValueError('Exact array mismatch: '+k)
def exact_baseline(root,out):
 from runtime_compare import typed_equal,compare_runtime
 for name in ['input-arrays.npz','graph.npz','neighbors.npz','model-output.npz']:exact_npz(out/name,root/BASE/name)
 for name in ['observations.json','model-tensor-hashes.json','config-original.json','point.json']:
  if not typed_equal(read(out/name),read(root/BASE/name)):raise ValueError('Exact metadata mismatch: '+name)
 if not compare_runtime(read(out/'runtime.json'),read(root/BASE/'runtime.json'))['passed']:raise ValueError('Complete runtime mismatch')
 (out/'baseline-gate.json').write_text(json.dumps({'passed':True,'exact_arrays':True,'runtime_exclusion':'condition label only'})+'\n')
def verify_execution_context(bundle):
 freeze=read(bundle/'freeze.json');verify_bundle(bundle,freeze)
 if freeze['status']!='reviewed_for_parent_release':raise ValueError('Bundle not released for review gate')
 release=read(os.environ['N1_RELEASE']);verify_release(release,freeze,dt.datetime.now(dt.timezone.utc))
 guard=read(ANCHOR);pid=int(os.environ['N1_CONTROLLER_PID'])
 if os.getppid()!=pid or guard['controller_pid']!=pid or guard['start']!=release['investigation_started_at_utc']:raise ValueError('Controller/immutable start mismatch')
 if release.get('frozen_bundle_private')!=str(bundle.resolve()):raise ValueError('Release bundle mismatch')
 return pid
def forward_permission(bundle,out):
 pid=verify_execution_context(bundle)
 root=Path(os.environ['MATTERLAB_ROOT'])
 from control_common import remote_head,local_coordination
 remote_head(root,30);local_coordination(root,30)
 for name in ['input-arrays.npz','neighbors.npz','graph.npz']:exact_npz(out/name,root/BASE/name)
 verify_execution_context(bundle)
 claim_attempt(out.parent/'forward-attempt.json',{'maximum_forwards':1,'controller_pid':pid})
