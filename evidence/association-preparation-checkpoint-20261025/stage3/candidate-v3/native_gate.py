"""Future execution gates; scientific array loading is deferred until called."""
import os,json
from pathlib import Path
import guards as g
BASE=Path('evidence/g1-selected-gamma-20261024/result/R-CaTiO3__base')
N1=Path('evidence/n1-precision-geometric-checkpoint-20261025/n1/result')
def exact_npz(actual,expected):
 import numpy as np
 with np.load(actual,allow_pickle=False) as a,np.load(expected,allow_pickle=False) as b:
  if set(a.files)!=set(b.files):raise ValueError('Array keys mismatch')
  for k in a.files:
   x,y=a[k],b[k]
   if x.dtype!=y.dtype or x.shape!=y.shape or x.tobytes()!=y.tobytes() or not np.isfinite(x).all():raise ValueError('Exact array mismatch: '+k)
def references(root):
 for n,v in g.read(g.BUNDLE/'INPUT_MANIFEST.json')['files'].items():
  p=Path(root)/n
  if p.stat().st_size!=v['bytes'] or g.sha(p)!=v['sha256']:raise ValueError('Pinned reference mismatch: '+n)
def condition():
 c=os.environ['ASSOCIATION_CONDITION']
 if c not in ('control','altered'):raise ValueError('Invalid condition')
 return c

def verify_execution_context(bundle):
 if Path(bundle).resolve()!=g.BUNDLE:raise ValueError('Wrong bundle')
 r=g.context();root=Path(os.environ['MATTERLAB_ROOT']).resolve()
 if str(root)!=r['root']:raise ValueError('Child root differs from release')
 g.coordination(root);references(root)
 c=condition();out=Path(os.environ['ASSOCIATION_OUTPUT'])
 if str(out.resolve())!=r['output']:raise ValueError('Wrong output')
 if c=='altered' and g.read(out/'control'/'point-complete.json')!={'passed':True,'condition':'control'}:raise ValueError('Control incomplete')
 return g.freshness(r,g.now())

def forward_permission(bundle,out):
 r=verify_execution_context(bundle);root=Path(os.environ['MATTERLAB_ROOT'])
 for n in ['input-arrays.npz','neighbors.npz','graph.npz']:exact_npz(out/n,root/BASE/n)
 g.claim(Path(os.environ['ASSOCIATION_OUTPUT'])/(condition()+'-forward.json'),{'condition':condition(),'maximum':1})
 return g.freshness(r,g.now())

def exact_baseline(root,out):
 from runtime_compare import typed_equal,compare_runtime
 c=condition()
 for n in ['input-arrays.npz','graph.npz','neighbors.npz']+(['model-output.npz'] if c=='control' else []):exact_npz(out/n,root/BASE/n)
 for n in ['model-tensor-hashes.json','config-original.json','point.json']+(['observations.json'] if c=='control' else []):
  if not typed_equal(g.read(out/n),g.read(root/BASE/n)):raise ValueError('Exact metadata mismatch: '+n)
 if not compare_runtime(g.read(out/'runtime.json'),g.read(root/BASE/'runtime.json'))['passed']:raise ValueError('Runtime mismatch')
 if c=='control':exact_npz(out/'native-pre-normalization.npz',root/N1/'native-pre-normalization.npz')
 else:
  import numpy as np
  with np.load(out/'native-pre-normalization.npz',allow_pickle=False) as a,np.load(root/N1/'native-pre-normalization.npz',allow_pickle=False) as b:
   x,y=a['positions'],b['positions']
   if x.dtype!=y.dtype or x.shape!=y.shape or x.tobytes()!=y.tobytes():raise ValueError('Native positions changed')
 (out/'baseline-gate.json').write_text(json.dumps({'passed':True,'condition':c})+'\n')

def final_point_gate(root,out):
 verify_execution_context(g.BUNDLE);c=condition()
 if g.read(out/'native-call-counts.json')!={'counts':{'force':1,'stress':1,'added':1},'terminal_failure':False}:raise ValueError('Native counts invalid')
 if c=='control':exact_npz(out/'native-row-50.npz',root/N1/'native-row-50.npz')
 required=['association-operands.npz','association-vectors.npz','association-features.npz','association-angles.npz','native-row-50.npz','model-output.npz','native-pre-normalization.npz']
 import numpy as np
 for n in required:
  with np.load(out/n,allow_pickle=False) as a:
   if not a.files or any(not a[k].size or not np.isfinite(a[k]).all() for k in a.files):raise ValueError('Missing/nonfinite capture: '+n)
 (out/'point-complete.json').write_text(json.dumps({'passed':True,'condition':c})+'\n')
