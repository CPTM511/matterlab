import sys,types,tempfile,json,hashlib,copy,builtins
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent.parent;C=R/'candidate-v2';sys.path.insert(0,str(C))
import guards,association_adapter,native_gate,native_capture,runtime_compare,controller
checks=[]
def test(n,f,reject=False):
 try:v=f()
 except Exception as e:checks.append({'name':n,'pass':reject,'exception':type(e).__name__});return
 checks.append({'name':n,'pass':not reject and v is not False})
class Truth:
 def __init__(self,v):self.v=v
 def all(self):return self.v
class A:
 size=1;shape=(1,);dtype='synthetic-f32';requires_grad=True;grad_fn='live'
 def __init__(self,data=b'a',finite=True):self.data=data;self.finite=finite
 def detach(self):return self
 def cpu(self):return self
 def numpy(self):return self
 def copy(self):return self
 def tobytes(self):return self.data
class Z:
 def __init__(self,v):self.v=v;self.files=list(v)
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def __getitem__(self,k):return self.v[k]
np=types.ModuleType('numpy');np.isfinite=lambda a:Truth(a.finite);np.savez=lambda *a,**kw:None;np.load=lambda p,**kw:p
sys.modules['numpy']=np
for name,left,right in [('values',{'x':A()},{'x':A(b'b')}),('keys',{'x':A()},{'y':A()}),('nonfinite',{'x':A(finite=False)},{'x':A()})]:test('array_mismatch_'+name,lambda left=left,right=right:native_gate.exact_npz(Z(left),Z(right)),True)
a=A();b=A();b.shape=(2,);test('array_shape_mismatch',lambda:native_gate.exact_npz(Z({'x':a}),Z({'x':b})),True)
b=A();b.dtype='other';test('array_dtype_mismatch',lambda:native_gate.exact_npz(Z({'x':a}),Z({'x':b})),True)
test('array_exact_pass',lambda:native_gate.exact_npz(Z({'x':A()}),Z({'x':A()})))
with tempfile.TemporaryDirectory(prefix='fixture-capture-',dir=R/'reviewer') as td:
 out=Path(td);m=types.SimpleNamespace(bond_basis_expansion=types.SimpleNamespace(forward=lambda *a:None),angle_basis_expansion=types.SimpleNamespace(forward=lambda *a:None))
 adapter=association_adapter.Adapter(m,None,out,'control',out)
 a=A();a.requires_grad=False;test('detached_product_rejected',lambda:adapter.observe('operands',{'product':a}),True)
 test('nonfinite_capture_rejected',lambda:adapter.observe('vectors',{'vectors':A(finite=False)}),True)
 test('missing_capture_stages_rejected',adapter.finish,True)
 # Native added-query error branches use Python stand-ins, never real AD.
 native_gate.verify_execution_context=lambda *a:None
 class F:
  def reshape(self,*a):return self
  def __getitem__(self,k):assert k==50;return types.SimpleNamespace(requires_grad=False)
 calls=[];torch=types.SimpleNamespace(autograd=types.SimpleNamespace(grad=lambda *a,**kw:calls.append('mock-query')))
 cap=native_capture.NativeCapture(torch,None,out);cap.budget.counts={'force':1,'stress':1,'added':0};cap.positions=[object()];cap.live_forces=[F()]
 test('unsupported_derivative_rejected_before_call',cap.query_rows,True);test('no_mock_query_on_disconnected_scalar',lambda:not calls)
 root=out/'root';bundle=out/'bundle';root.mkdir();bundle.mkdir()
 test('safe_sibling_output',lambda:guards.paths_gate(root,out/'new-output',bundle))
 for name,target in [('root_child',root/'x'),('bundle_child',bundle/'x'),('ancestor',out),('existing',root)]:test('path_'+name,lambda target=target:guards.paths_gate(root,target,bundle),True)
 v={'condition':'control','cpu_capability':'NO AVX','torch_build':'  - CPU capability usage: NO AVX\n','threads':1}
 w=dict(v,condition='altered');test('runtime_label_only_pass',lambda:runtime_compare.compare_runtime(v,w)['passed'])
 for name,w in [('bool',dict(v,threads=True)),('dtype',dict(v,threads=1.0)),('extra',dict(v,extra=1)),('duplicate',dict(v,torch_build=v['torch_build']*2)),('capability',dict(v,cpu_capability='other'))]:test('runtime_'+name,lambda w=w:not runtime_compare.compare_runtime(v,w)['passed'])
 # Direct cleanup helper with mocked syscalls, no process or signal delivery.
 original=controller.os.killpg;events=[];controller.os.killpg=lambda *a:events.append(a)
 class P:
  pid=123
  def wait(self,timeout):events.append(('wait',timeout))
 test('bounded_cleanup',lambda:controller.kill_group(P()));test('cleanup_reap_bounded',lambda:events[-1]==('wait',1.0))
 class BadP(P):
  def wait(self,timeout):raise controller.subprocess.TimeoutExpired('synthetic',timeout)
 test('unconfirmed_cleanup_blocks',lambda:controller.kill_group(BadP()),True);controller.os.killpg=original
print(json.dumps({'scope':'Injected fake numpy/array objects and Python mock-gradient; no actual scientific module/data/AD/process/entrypoint','passed':sum(x['pass'] for x in checks),'total':len(checks),'checks':checks,'source_hashes':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['association_adapter.py','native_gate.py','native_capture.py','guards.py','runtime_compare.py','controller.py']}},indent=2))
