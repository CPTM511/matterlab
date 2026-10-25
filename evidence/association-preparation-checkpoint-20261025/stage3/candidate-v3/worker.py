"""G1 derivative recorder: not physically validated. One predeclared displaced point."""
import os,sys,json,hashlib,time,platform,shutil
from pathlib import Path
import numpy as np
import torch
from ase import Atoms
R=Path(os.environ['MATTERLAB_ROOT']).resolve()
sys.path.insert(0,str(R/'src'))
import matterlab
assert Path(matterlab.__file__).resolve().is_relative_to(R/'src'), 'Imported source differs from MATTERLAB_ROOT'
from capture_helpers import capture_method
from preinference_guards import check_hash_record, check_runtime, check_model_finite
from matterlab.simulate import make_calculator
from matterlab.evidence import environment
P=Path(sys.argv[1]).resolve();P.mkdir(exist_ok=False)
R=Path(os.environ['MATTERLAB_ROOT']).resolve()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def array_record(values):return {k:{'dtype':str(v.dtype),'shape':list(v.shape),'data_sha256':hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest()} for k,v in values.items()}
try:
 expected_code=json.loads(Path(os.environ['MATTERLAB_EXPECTED_CODE']).read_text())
 assert all(sha(R/name)==value for name,value in expected_code['sources_sha256'].items()), 'Source hash mismatch'
 save('expected-source-code.json',expected_code)
 torch.set_num_interop_threads(1)
 config=json.loads((R/'configs/round-001.json').read_text())
 assert config['threads']==1 and config['device']=='cpu'
 point=json.loads(Path(str(Path(__file__).with_name('point.json'))).read_text());save('point.json',point)
 points=json.loads(Path(__file__).with_name('points.json').read_text())
 assert point==next(p for p in points if p['id']==point['id'])
 assert len(point['positions'])==20 and len(point['symbols'])==20
 shutil.copy2(R/'configs/round-001.json',P/'config-original.json')
 shutil.copy2(__file__,P/'diagnostic_eval.py')
 shutil.copy2(Path(__file__).with_name('capture_helpers.py'),P/'capture_helpers.py')
 save('provenance.json',environment(config))
 atoms=Atoms(symbols=point['symbols'],positions=point['positions'],cell=point['cell'],pbc=point['pbc']);calc=make_calculator(config);atoms.calc=calc
 model=calc.model
 assert model.graph_converter.atom_graph_cutoff==6 and model.graph_converter.bond_graph_cutoff==3
 captures={'graph_calls':0,'model_calls':0,'neighbor_calls':0};attempts={'graph':0,'model':0,'neighbor':0}
 def once(kind):
  attempts[kind]+=1;save('call-attempts.json',attempts)
  assert attempts[kind]==1, 'Duplicate actual call: '+kind
 params={k:v.detach().cpu().numpy() for k,v in model.state_dict().items()}
 save('model-tensor-hashes.json',array_record(params))
 check_hash_record(R,P,'model-tensor-hashes.json')
 def graph_before(module,args):
  once('graph')
  structure=args[0]
  inp={'atomic_numbers':atoms.numbers,'positions':atoms.positions,'cell':atoms.cell.array,'pbc':atoms.pbc,'frac_coords':structure.frac_coords,'lattice':structure.lattice.matrix}
  np.savez(P/'input-arrays.npz',**inp);save('input-array-hashes.json',array_record(inp))
  assert np.array_equal(inp['positions'],np.array(point['positions'],dtype=np.float64))
  assert np.array_equal(inp['cell'],np.array(point['cell'],dtype=np.float64))
  def capture_actual_neighbors(n):
   captures['neighbor_calls']+=1
   a=dict(zip(['center','neighbor','image','distance'],n));np.savez(P/'neighbors.npz',**a);save('neighbor-hashes.json',array_record(a))
   assert all(np.isfinite(x).all() for x in a.values())
  actual_neighbors=structure.get_neighbor_list
  def guarded_neighbors(*a,**kw):
   once('neighbor');value=actual_neighbors(*a,**kw);capture_actual_neighbors(value);return value
  structure.get_neighbor_list=guarded_neighbors
 def graph_after(module,args,result):
  captures['graph_calls']+=1
  a={k:v.detach().cpu().numpy().copy() for k,v in result.to_dict().items() if isinstance(v,torch.Tensor)}
  np.savez(P/'graph.npz',**a);save('graph-hashes.json',array_record(a))
  assert a and all(np.isfinite(x).all() for x in a.values())
  from native_gate import exact_npz
  exact_npz(P/'graph.npz',R/'evidence/g1-selected-gamma-20261024/result/R-CaTiO3__base/graph.npz')
 def prediction_hook(result):
  captures['model_calls']+=1
  a={}
  for k,v in result.items():
   if isinstance(v,torch.Tensor):a[k]=v.detach().cpu().numpy().copy()
   elif isinstance(v,(list,tuple)):
    for i,x in enumerate(v):
     if isinstance(x,torch.Tensor):a[k+'_'+str(i)]=x.detach().cpu().numpy().copy()
  np.savez(P/'model-output.npz',**a);save('model-output-hashes.json',array_record(a))
  check_model_finite(a)
 model.graph_converter.register_forward_pre_hook(graph_before)
 model.graph_converter.register_forward_hook(graph_after)
 from native_capture import NativeCapture
 native=NativeCapture(torch,model,P)
 native.install()
 from association_adapter import Adapter
 adapter=Adapter(model,torch,P,os.environ['ASSOCIATION_CONDITION'],Path(os.environ['ASSOCIATION_OUTPUT'])/'control')
 adapter.install()
 actual_forward=model.forward
 def guarded_forward(*a,**kw):
  from native_gate import forward_permission
  boundary_release=forward_permission(Path(__file__).parent,P)
  once('model')
  import guards as boundary_guards
  boundary_guards.freshness(boundary_release,boundary_guards.now())
  value=actual_forward(*a,**kw);native.live_forces=value['f'];prediction_hook(value);return value
 model.forward=guarded_forward
 runtime={'capture_stage':'inside evaluation before inference','condition':os.environ['MATTERLAB_CONDITION'],'cpu_capability':torch.backends.cpu.get_cpu_capability(),'torch_version':torch.__version__,'default_dtype':str(torch.get_default_dtype()),'parameter_dtypes':sorted({str(x.dtype) for x in model.parameters()}),'graph_algorithm':model.graph_converter.algorithm,'torch_num_threads':torch.get_num_threads(),'torch_num_interop_threads':torch.get_num_interop_threads(),'cpu_affinity':sorted(os.sched_getaffinity(0)),'deterministic_algorithms':torch.are_deterministic_algorithms_enabled(),'mkldnn_enabled':torch.backends.mkldnn.enabled,'float32_matmul_precision':torch.get_float32_matmul_precision(),'torch_build':torch.__config__.show(),'environment_controls':{k:os.environ.get(k) for k in ['ATEN_CPU_CAPABILITY','OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_CBWR']},'seed':config['seed'],'device':str(next(model.parameters()).device),'python':sys.version,'platform':platform.platform()}
 save('runtime.json',runtime)
 check_runtime(R,P,runtime)
 assert runtime['torch_num_threads']==1 and len(runtime['cpu_affinity'])==1
 start=time.monotonic();energy=float(atoms.get_potential_energy());forces=atoms.get_forces();stress=atoms.get_stress(voigt=False)
 assert np.isfinite(energy) and np.isfinite(forces).all() and np.isfinite(stress).all()
 from ase import units
 raw=np.load(P/'model-output.npz',allow_pickle=False)
 assert set(raw.files)=={'e','f_0','s_0','m_0','crystal_fea','atoms_per_graph'}
 assert np.array_equal(np.asarray(forces),raw['f_0'])
 assert energy==float(np.float32(raw['e'][0])*np.float32(len(atoms)))
 converted=raw['s_0']*units.GPa
 assert np.array_equal(stress,(converted+converted.T)/2)
 save('observations.json',{'energy_eV':energy,'forces_eV_A':forces.tolist(),'stress_eV_A3':stress.tolist(),'atoms':len(atoms),'relaxation_performed':False})
 save('capture-summary.json',dict(captures,inference_seconds=time.monotonic()-start))
 assert captures=={'graph_calls':1,'model_calls':1,'neighbor_calls':1},captures
 assert array_record({k:v.detach().cpu().numpy() for k,v in model.state_dict().items()})==json.loads((P/'model-tensor-hashes.json').read_text())
 from native_gate import exact_baseline
 exact_baseline(R,P)
 adapter.finish()
 native.query_rows()
 from native_gate import final_point_gate
 final_point_gate(R,P)
 print(json.dumps({'condition':runtime['condition'],'capability':runtime['cpu_capability'],'energy_eV':energy,'captures':captures}))
except Exception:
 import traceback
 (P/'failure.txt').write_text(traceback.format_exc());raise
finally:
 if 'adapter' in globals():adapter.restore()
 if 'native' in globals():native.restore()
 save('manifest.json',{'algorithm':'SHA256','files':{str(f.relative_to(P)):sha(f) for f in sorted(P.rglob('*')) if f.is_file() and f.name!='manifest.json'}})
