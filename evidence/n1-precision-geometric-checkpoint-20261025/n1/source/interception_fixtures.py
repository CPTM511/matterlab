"""Fake native-call fixture; no torch/model/AD computation or real execution tokens."""
import tempfile,types,json,sys
from pathlib import Path
import numpy as np
from native_capture import NativeCapture
class T:
 def __init__(self,v):self.a=np.asarray(v);self.shape=self.a.shape;self.ndim=self.a.ndim
 def detach(self):return self
 def cpu(self):return self
 def numpy(self):return self.a
class Model:
 def __init__(self,t):self.t=t
 def _compute(self,g,scalar,mode='normal'):
  x=self.t.autograd.grad(scalar,g.atom_positions,create_graph=True,retain_graph=True)
  if mode=='duplicate':self.t.autograd.grad(scalar,g.atom_positions,create_graph=True,retain_graph=True)
  self.t.autograd.grad(scalar,g.strains,create_graph=True,retain_graph=True)
  return x
checks=[]
for mode in ['normal','duplicate','nonfinite']:
 calls=[]
 def original(*a,**kw):calls.append((a,kw));return ('unchanged-result',)
 torch=types.SimpleNamespace(autograd=types.SimpleNamespace(grad=original));model=Model(torch);g=types.SimpleNamespace(atom_positions=[T(np.zeros((20,3)))],strains=[T(np.zeros((3,3)))]);scalar=T(np.nan if mode=='nonfinite' else 7.0)
 with tempfile.TemporaryDirectory() as d:
  cap=NativeCapture(torch,model,d);cap.install()
  try:
   result=model._compute(g,scalar,mode)
   assert mode=='normal' and result==('unchanged-result',) and len(calls)==2
   assert calls[0][0][0] is scalar and calls[0][0][1] is g.atom_positions
   scalar.a[...]=99
   with np.load(Path(d)/'native-pre-normalization.npz') as saved:assert saved['scalar']==7
   assert cap.scalar is scalar and cap.positions is g.atom_positions
  except RuntimeError:
   assert mode!='normal' and cap.budget.failed and len(calls)<=1
  finally:cap.restore()
  assert torch.autograd.grad is original
  checks.append({'mode':mode,'passed':True,'actual_callback_calls':len(calls)})
assert 'torch' not in sys.modules
print(json.dumps({'scope':'fake callback interception, not model/autograd evaluation','checks':checks,'passed':True,'real_model_forwards':0,'real_AD_queries':0},indent=2))
