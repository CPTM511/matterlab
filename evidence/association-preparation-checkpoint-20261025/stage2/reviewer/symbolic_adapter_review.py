import importlib.util,json,hashlib,sys
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parent.parent;path=root/'candidate-v2/association_adapter.py'
spec=importlib.util.spec_from_file_location('reviewed_adapter',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def check(n,v):checks.append({'name':n,'pass':bool(v)})
def run(condition,stop=False):
 events=[];seen={}
 class T:
  def __init__(self,s):self.s=s;self.requires_grad=True;self.grad_fn='symbolic-live'
  def op(self,kind,x):events.append(kind);return T('('+self.s+kind+x.s+')')
  def __matmul__(self,x):return self.op('@',x)
  def __add__(self,x):return self.op('+',x)
  def __sub__(self,x):return self.op('-',x)
  def __truediv__(self,x):return self.op('/',x)
  def __getitem__(self,x):events.append('broadcast');return T('broadcast('+self.s+')')
 class Ops:
  def norm(self,x,dim):assert dim==1;events.append('norm');return T('norm('+x.s+')')
  def index_select(self,x,dim,idx):assert dim==0 and idx is mapping;events.append('select');return T('select('+x.s+')')
 class Module:
  def rbf_expansion_ag(self,x):events.append('ag');return T('ag('+x.s+')')
  def rbf_expansion_bg(self,x):events.append('bg');return T('bg('+x.s+')')
 center,neighbor,image,lattice,mapping=[T(n) for n in ['c','n','image','lattice','mapping']]
 def observe(stage,values):
  events.append('observe:'+stage);seen[stage]=values
  if stage=='operands':
   assert values['center'] is center and values['neighbor'] is neighbor and values['image'] is image and values['lattice'] is lattice and values['mapping'] is mapping
   assert values['product'].s=='(image@lattice)'
   if stop:raise ValueError('synthetic operand gate')
 try:result=m.bond_forward(Module(),center,neighbor,mapping,image,lattice,ops=Ops(),condition=condition,observe=observe)
 except ValueError:return events,seen,None
 return events,seen,result
for condition,formula,ops in [('control','(c-(n+(image@lattice)))',['+','-']),('altered','((c-n)-(image@lattice))',['-','-'])]:
 events,seen,result=run(condition)
 expected=['@','observe:operands',*ops,'observe:vectors','norm','broadcast','/','select','ag','bg','observe:features']
 check(condition+'_exact_operation_trace',events==expected)
 check(condition+'_vector_expression',seen['vectors']['vectors'].s==formula)
 check(condition+'_once_product',events.count('@')==1)
 check(condition+'_unchanged_return_values',result[0] is seen['features']['radial_ag'] and result[1] is seen['features']['radial_bg'] and result[2] is seen['features']['normalized'])
 events,seen,result=run(condition,True)
 check(condition+'_operand_gate_before_association',events==['@','observe:operands'] and result is None)
events,seen,result=run('invalid');check('invalid_condition_stops',result is None and events==['@','observe:operands'])
print(json.dumps({'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Pure symbolic operator tracing; no torch, numpy, model, numeric array, AD or real attempt','passed':sum(x['pass'] for x in checks),'total':len(checks),'checks':checks},indent=2))
