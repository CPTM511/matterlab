"""Inert until explicitly installed; uses injected torch only during future execution."""
import types

def bond_forward(module,center,neighbor,undirected2directed,image,lattice,*,ops,condition,observe):
 t=image @ lattice
 observe('operands',{'center':center,'neighbor':neighbor,'image':image,'lattice':lattice,'mapping':undirected2directed,'product':t})
 if condition=='control':
  shifted=neighbor+t
  vectors=center-shifted
 elif condition=='altered':
  difference=center-neighbor
  vectors=difference-t
 else:raise ValueError('Unknown condition')
 observe('vectors',{'vectors':vectors})
 lengths=ops.norm(vectors,dim=1)
 normalized=vectors/lengths[:,None]
 undirected=ops.index_select(lengths,0,undirected2directed)
 ag=module.rbf_expansion_ag(undirected)
 bg=module.rbf_expansion_bg(undirected)
 observe('features',{'lengths':lengths,'normalized':normalized,'radial_ag':ag,'radial_bg':bg})
 return ag,bg,normalized

class Adapter:
 def __init__(self,model,torch,out,condition,control):
  from pathlib import Path
  self.model=model;self.torch=torch;self.out=Path(out);self.condition=condition;self.control=Path(control);self.calls={'bond':0,'angle':0};self.failed=False;self.stages=set();self.original_bond=model.bond_basis_expansion.forward;self.original_angle=model.angle_basis_expansion.forward
 def persist(self):
  import json
  (self.out/'association-counts.json').write_text(json.dumps({'calls':self.calls,'failed':self.failed,'captured_stages':sorted(self.stages)})+'\n')
 def observe(self,stage,values):
  import numpy as np
  arrays={}
  def flatten(name,x):
   if isinstance(x,(tuple,list)):
    for i,v in enumerate(x):flatten(name+'_'+str(i),v)
   else:
    a=x.detach().cpu().numpy().copy()
    if not a.size or not np.isfinite(a).all():raise ValueError('Missing/nonfinite adapter capture')
    arrays[name]=a
  for name,x in values.items():flatten(name,x)
  if stage=='operands':
   if not values['product'].requires_grad or values['product'].grad_fn is None:raise ValueError('Detached live product')
  path=self.out/('association-'+stage+'.npz');np.savez(path,**arrays)
  if stage=='operands' and self.condition=='altered':
   from native_gate import exact_npz
   exact_npz(path,self.control/path.name)
  self.stages.add(stage);self.persist()
 def install(self):
  owner=self
  def bond(module,center,neighbor,undirected2directed,image,lattice):
   owner.calls['bond']+=1;owner.persist()
   try:
    if owner.failed or owner.calls['bond']!=1:raise ValueError('Extra/failed bond evaluation')
    return bond_forward(module,center,neighbor,undirected2directed,image,lattice,ops=owner.torch,condition=owner.condition,observe=owner.observe)
   except BaseException:
    owner.failed=True;owner.persist();raise
  def angle(module,*a,**kw):
   owner.calls['angle']+=1;owner.persist()
   try:
    if owner.failed or owner.calls['angle']!=1:raise ValueError('Extra/failed angle evaluation')
    result=owner.original_angle(*a,**kw);owner.observe('angles',{'angles':result});return result
   except BaseException:
    owner.failed=True;owner.persist();raise
  self.model.bond_basis_expansion.forward=types.MethodType(bond,self.model.bond_basis_expansion)
  self.model.angle_basis_expansion.forward=types.MethodType(angle,self.model.angle_basis_expansion)
 def finish(self):
  self.persist()
  if self.failed or self.calls!={'bond':1,'angle':1} or self.stages!={'operands','vectors','features','angles'}:raise ValueError('Incomplete/failed adapter capture')
 def restore(self):
  self.model.bond_basis_expansion.forward=self.original_bond;self.model.angle_basis_expansion.forward=self.original_angle
