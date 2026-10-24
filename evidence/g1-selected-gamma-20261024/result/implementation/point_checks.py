"""Capture integrity and exact repeat checks; saved-array operations only."""
import hashlib,json
from pathlib import Path
import numpy as np
from runtime_compare import compare_runtime

def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arrays(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
def record(a):return {k:{'dtype':str(v.dtype),'shape':list(v.shape),'data_sha256':hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest()} for k,v in a.items()}
def check_graph(d):
 d=Path(d);a=arrays(d/'input-arrays.npz');n=arrays(d/'neighbors.npz');g=arrays(d/'graph.npz')
 schema={'atomic_numbers':('int64',(20,)),'positions':('float64',(20,3)),'cell':('float64',(3,3)),'pbc':('bool',(3,)),'frac_coords':('float64',(20,3)),'lattice':('float64',(3,3))}
 assert set(a)==set(schema)
 for k,(dtype,shape) in schema.items():assert str(a[k].dtype)==dtype and a[k].shape==shape
 assert np.array_equal(a['cell'],a['lattice'])
 assert np.allclose(a['frac_coords']@a['lattice'],a['positions'],rtol=0,atol=1e-12)
 E=len(n['center']);U=len(g['undirected2directed']);B=len(g['bond_graph'])
 ns={'center':('int64',(E,)),'neighbor':('int64',(E,)),'image':('float64',(E,3)),'distance':('float64',(E,))}
 assert set(n)==set(ns)
 for k,(dtype,shape) in ns.items():assert str(n[k].dtype)==dtype and n[k].shape==shape
 gs={'atomic_number':('int32',(20,)),'atom_frac_coord':('float32',(20,3)),'atom_graph':('int32',(E,2)),'neighbor_image':('float32',(E,3)),'directed2undirected':('int32',(E,)),'undirected2directed':('int32',(U,)),'bond_graph':('int32',(B,5)),'lattice':('float32',(3,3))}
 assert set(g)==set(gs)
 for k,(dtype,shape) in gs.items():assert str(g[k].dtype)==dtype and g[k].shape==shape
 assert E==2*U and U>0
 du,ud,bg=g['directed2undirected'],g['undirected2directed'],g['bond_graph']
 assert np.all((du>=0)&(du<U)) and np.all((ud>=0)&(ud<E))
 assert np.array_equal(du[ud],np.arange(U)) and np.array_equal(np.bincount(du,minlength=U),np.full(U,2))
 for group in range(U):
  left,right=np.flatnonzero(du==group)
  assert ud[group]==left
  assert n['center'][left]==n['neighbor'][right] and n['neighbor'][left]==n['center'][right]
  assert np.array_equal(n['image'][left],-n['image'][right])
  assert abs(n['distance'][left]-n['distance'][right])<=1e-6
 assert np.all((bg[:,0]>=0)&(bg[:,0]<20))
 assert np.all((bg[:,[1,3]]>=0)&(bg[:,[1,3]]<U)) and np.all((bg[:,[2,4]]>=0)&(bg[:,[2,4]]<E))
 assert np.array_equal(du[bg[:,2]],bg[:,1]) and np.array_equal(du[bg[:,4]],bg[:,3])
 assert np.array_equal(n['center'][bg[:,2]],bg[:,0]) and np.array_equal(n['center'][bg[:,4]],bg[:,0])
 assert np.all(bg[:,2]!=bg[:,4])
 assert np.all(n['distance']>0) and np.all(n['distance']<=6+1e-8)
 assert np.array_equal(n['image'],np.rint(n['image']))
 delta=(a['frac_coords'][n['neighbor']]-a['frac_coords'][n['center']]+n['image'])@a['lattice']
 assert np.allclose(np.linalg.norm(delta,axis=1),n['distance'],rtol=0,atol=1e-10)
 expected=[]
 for left in range(E):
  if n['distance'][ud[du[left]]]<=3:
   for right in np.flatnonzero((n['center']==n['center'][left])&(n['distance']<3)):
    if left!=right:expected.append((int(n['center'][left]),int(du[left]),left,int(du[right]),int(right)))
 assert sorted(map(tuple,bg.tolist()))==sorted(expected)
 assert set(g)=={'atomic_number','atom_frac_coord','atom_graph','neighbor_image','directed2undirected','undirected2directed','bond_graph','lattice'}
 assert set(n)=={'center','neighbor','image','distance'}
 for v in [*a.values(),*n.values(),*g.values()]:assert v.size and np.isfinite(v).all()
 for k in ['center','neighbor']:assert np.array_equal(n[k],n[k].astype(np.int32).astype(n[k].dtype))
 assert np.array_equal(g['atom_frac_coord'],a['frac_coords'].astype(np.float32))
 assert np.array_equal(g['lattice'],a['lattice'].astype(np.float32))
 assert np.array_equal(g['atom_graph'],np.column_stack([n['center'],n['neighbor']]).astype(np.int32))
 assert np.array_equal(g['neighbor_image'],n['image'].astype(np.float32))
 assert np.array_equal(g['atomic_number'],a['atomic_numbers'].astype(np.int32))
 assert len(n['center'])==len(n['neighbor'])==len(n['image'])==len(n['distance'])
 assert np.all((n['center']>=0)&(n['center']<20)) and np.all((n['neighbor']>=0)&(n['neighbor']<20))
 assert np.array_equal(a['pbc'],[True]*3)

def validate_point(d,p,root):
 d=Path(d);root=Path(root);m=load(d/'manifest.json')['files']
 assert set(m)=={str(f.relative_to(d)) for f in d.rglob('*') if f.is_file() and f.name!='manifest.json'}
 assert all(sha(d/n)==h for n,h in m.items())
 assert load(d/'point.json')==p
 assert load(d/'call-attempts.json')=={'graph':1,'model':1,'neighbor':1}
 c=load(d/'capture-summary.json');assert c['graph_calls']==c['model_calls']==c['neighbor_calls']==1
 for name,rec in [('input-arrays.npz','input-array-hashes.json'),('neighbors.npz','neighbor-hashes.json'),('graph.npz','graph-hashes.json'),('model-output.npz','model-output-hashes.json')]:assert record(arrays(d/name))==load(d/rec)
 a=arrays(d/'input-arrays.npz');assert np.array_equal(a['positions'],np.array(p['positions'],dtype=np.float64));assert np.array_equal(a['cell'],np.array(p['cell'],dtype=np.float64))
 from ase.data import atomic_numbers
 assert np.array_equal(a['atomic_numbers'],[atomic_numbers[s] for s in p['symbols']]);check_graph(d)
 model=arrays(d/'model-output.npz');shapes={'e':(1,),'f_0':(20,3),'s_0':(3,3),'m_0':(20,),'crystal_fea':(1,64),'atoms_per_graph':(1,)};assert set(model)==set(shapes)
 for k,v in model.items():assert v.shape==shapes[k] and str(v.dtype)==('int64' if k=='atoms_per_graph' else 'float32') and np.isfinite(v).all()
 assert model['atoms_per_graph'][0]==20
 from ase import units
 converted=model['s_0']*units.GPa;obs=load(d/'observations.json')
 assert obs['energy_eV']==float(model['e'][0]*20)
 assert np.array_equal(obs['forces_eV_A'],model['f_0'])
 assert np.array_equal(obs['stress_eV_A3'],(converted+converted.T)/2)
 assert load(d/'model-tensor-hashes.json')==load(root/'evidence/dispatch-contrast-20261023/C1-default/model-tensor-hashes.json')
 assert compare_runtime(load(d/'runtime.json'),load(root/'evidence/dispatch-contrast-20261023/C1-default/runtime.json'))['passed']

def check_repeat(a,b):
 a,b=Path(a),Path(b)
 for n in ['input-array-hashes.json','neighbor-hashes.json','graph-hashes.json','model-tensor-hashes.json','model-output-hashes.json','observations.json']:
  assert load(a/n)==load(b/n),'Repeat mismatch:'+n
 for n in ['input-arrays.npz','neighbors.npz','graph.npz','model-output.npz']:
  x,y=arrays(a/n),arrays(b/n);assert set(x)==set(y)
  for k in x:assert x[k].dtype==y[k].dtype and x[k].shape==y[k].shape and x[k].tobytes()==y[k].tobytes(),'Repeat bytes:'+n+':'+k
 assert compare_runtime(load(a/'runtime.json'),load(b/'runtime.json'))['passed']

def save_repeat_differences(a,b,path):
 a,b=Path(a),Path(b);result={}
 for name in ['input-arrays.npz','neighbors.npz','graph.npz','model-output.npz']:
  x,y=arrays(a/name),arrays(b/name);rows={}
  for k in set(x)|set(y):
   if k not in x or k not in y or x[k].shape!=y[k].shape:rows[k]={'comparison_unavailable':'missing field or shape mismatch'}
   else:rows[k]={'signed_difference':(x[k].astype(float)-y[k].astype(float)).tolist(),'same_dtype':x[k].dtype==y[k].dtype}
  result[name]=rows
 oa,ob=load(a/'observations.json'),load(b/'observations.json')
 result['ASE']={k:(np.asarray(oa[k])-np.asarray(ob[k])).tolist() for k in ['energy_eV','forces_eV_A','stress_eV_A3']}
 Path(path).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
