"""Inert on import. Runtime interception preserves the original native grad call."""
import inspect,json
from pathlib import Path
class Budget:
 def __init__(self):self.counts={'force':0,'stress':0,'added':0};self.failed=False
 def claim(self,kind):
  if self.failed:raise RuntimeError('Terminal failure; no retry')
  self.counts[kind]+=1
  if self.counts[kind] > (2 if kind=='added' else 1):self.failed=True;raise RuntimeError('Call cap exceeded')
 def fail(self):self.failed=True
class NativeCapture:
 def __init__(self,torch,model,out):
  self.torch=torch;self.model=model;self.out=Path(out);self.original=torch.autograd.grad;self.budget=Budget();self.positions=None;self.live_forces=None;self.installed=False
 def save_counts(self):
  (self.out/'native-call-counts.json').write_text(json.dumps({'counts':self.budget.counts,'terminal_failure':self.budget.failed},indent=2)+'\n')
 def install(self):
  if self.installed:raise RuntimeError('Already installed')
  def intercepted(*args,**kwargs):
   frame=inspect.currentframe().f_back
   try:
    if frame.f_code is not type(self.model)._compute.__code__ or frame.f_locals.get('self') is not self.model:raise RuntimeError('Unexpected native grad caller')
    g=frame.f_locals['g'];inputs=args[1] if len(args)>1 else kwargs.get('inputs')
    if inputs is g.atom_positions:kind='force'
    elif inputs is g.strains:kind='stress'
    else:raise RuntimeError('Unknown native grad input identity')
    if len(args)!=2 or kwargs!={'create_graph':True,'retain_graph':True}:raise RuntimeError('Native call signature changed')
    self.budget.claim(kind);self.save_counts()
    if kind=='force':
     self.scalar=args[0];self.positions=inputs
     if self.scalar.ndim!=0 or len(inputs)!=1 or tuple(inputs[0].shape)!=(20,3):raise RuntimeError('Unexpected native scalar/positions')
     import numpy as np
     scalar_copy=self.scalar.detach().cpu().numpy().copy();position_copy=inputs[0].detach().cpu().numpy().copy()
     np.savez(self.out/'native-pre-normalization.npz',scalar=scalar_copy,positions=position_copy)
     if not np.isfinite(scalar_copy).all() or not np.isfinite(position_copy).all():raise RuntimeError('Nonfinite native scalar/positions')
    return self.original(*args,**kwargs)
   except BaseException:
    self.budget.fail();self.save_counts();raise
   finally:del frame
  self.wrapper=intercepted;self.torch.autograd.grad=intercepted;self.installed=True
 def restore(self):
  if self.installed:
   if self.torch.autograd.grad is not self.wrapper:raise RuntimeError('Native wrapper replaced unexpectedly')
   self.torch.autograd.grad=self.original;self.installed=False
 def query_rows(self):
  import numpy as np
  self.restore()
  if self.budget.counts!={'force':1,'stress':1,'added':0} or self.budget.failed:raise RuntimeError('Native count gate failed')
  if self.live_forces is None or len(self.live_forces)!=1 or self.positions is None:raise RuntimeError('Missing live force graph')
  for j in (50,59):
   try:
    from native_gate import verify_execution_context
    verify_execution_context(Path(__file__).resolve().parent)
    self.budget.claim('added');self.save_counts()
    scalar=self.live_forces[0].reshape(-1)[j]
    if not scalar.requires_grad:raise RuntimeError('Disconnected force scalar')
    derivative=self.original(scalar,self.positions,create_graph=False,retain_graph=True,allow_unused=False)
    if len(derivative)!=1 or derivative[0] is None:raise RuntimeError('Disconnected derivative')
    row=-derivative[0].detach().cpu().numpy().copy().reshape(-1)
    np.savez(self.out/f'native-row-{j}.npz',row=row)
    if row.shape!=(60,) or not np.isfinite(row).all():raise RuntimeError('Nonfinite or malformed derivative')
   except BaseException:
    self.budget.fail();self.save_counts();raise
