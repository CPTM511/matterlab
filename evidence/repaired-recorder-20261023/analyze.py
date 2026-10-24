"""Read-only numerical/integrity analysis of the single completed evaluation; no model construction."""
import json,hashlib,os
from pathlib import Path
import numpy as np
from ase import units
P=Path(os.environ['MATTERLAB_VALIDATION_OUTPUT']);R=Path(os.environ['MATTERLAB_ROOT']);D=P/'R1'
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
protocol=json.loads((P/'protocol.json').read_text());obs=json.loads((D/'observations.json').read_text())
ck('frozen_protocol',sha(P/'protocol.json')==json.loads((P/'protocol-freeze.json').read_text())['sha256'])
ck('calculation_exited_successfully',json.loads((P/'execution.json').read_text())['returncode']==0)
raw={}
for archive,metadata in [('input-arrays','input-array-hashes'),('neighbors','neighbor-hashes'),('graph','graph-hashes'),('model-output','model-output-hashes')]:
    with np.load(D/(archive+'.npz'),allow_pickle=False) as f:raw[archive]={k:f[k].copy() for k in f.files}
    hashes=json.loads((D/(metadata+'.json')).read_text())
    ck(archive+':keys',set(raw[archive])==set(hashes))
    for key,a in raw[archive].items():
        h=hashes[key]
        ck(archive+':'+key, bool(a.size and np.isfinite(a).all() and h['shape']==list(a.shape) and h['dtype']==str(a.dtype) and h['data_sha256']==hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()))
for name,value in json.loads((D/'manifest.json').read_text())['files'].items():ck('manifest:'+name,sha(D/name)==value)
summary=json.loads((D/'capture-summary.json').read_text());runtime=json.loads((D/'runtime.json').read_text())
ck('capture_calls',summary['graph_calls']==summary['model_calls']==1)
ck('thread_device_affinity',runtime['torch_num_threads']==runtime['torch_num_interop_threads']==1 and runtime['cpu_affinity']==protocol['resource_limits']['cpu_affinity'] and runtime['device']=='cpu')
ck('seed',runtime['seed']==20261024)
ck('numerical_library_thread_controls',all(runtime['environment_controls'][k]=='1' for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']))
ck('20_atoms_no_relaxation',obs['atoms']==20 and obs['relaxation_performed'] is False)
ck('observable_shapes',np.asarray(obs['forces_eV_A']).shape==(20,3) and np.asarray(obs['stress_eV_A3']).shape==(3,3))
graph=raw['graph'];neighbors=raw['neighbors'];model=raw['model-output'];inp=raw['input-arrays']
expected_graph={'atomic_number','atom_frac_coord','atom_graph','neighbor_image','directed2undirected','undirected2directed','bond_graph','lattice'}
ck('eight_graph_arrays',set(graph)==expected_graph)
ck('required_model_arrays',{'e','f_0','s_0','atoms_per_graph'}<=set(model))
ck('neighbor_keys',set(neighbors)=={'center','neighbor','image','distance'})
n=len(neighbors['center'])
ck('neighbor_shapes',n>0 and neighbors['neighbor'].shape==(n,) and neighbors['image'].shape==(n,3) and neighbors['distance'].shape==(n,))
ck('graph_consumed_neighbor_indices',np.array_equal(graph['atom_graph'],np.column_stack([neighbors['center'],neighbors['neighbor']])))
ck('graph_consumed_neighbor_images',np.array_equal(graph['neighbor_image'],neighbors['image'].astype(np.float32)))
ck('input_graph_consistency',np.array_equal(inp['atomic_numbers'],graph['atomic_number']) and np.array_equal(inp['frac_coords'].astype(np.float32),graph['atom_frac_coord']) and np.array_equal(inp['lattice'].astype(np.float32),graph['lattice']))
vector=inp['positions'][neighbors['neighbor']]+neighbors['image']@inp['cell']-inp['positions'][neighbors['center']]
distance_residual=np.linalg.norm(vector,axis=1)-neighbors['distance']
save('neighbor-geometry-sanity.json',{'scope':'Arithmetic check only; no new neighbor query or inference','signed_distance_residual_A':distance_residual.tolist(),'maximum_absolute_residual_A':float(np.abs(distance_residual).max())})
# Match CHGNet's float32 scalar/array arithmetic, including ASE stress symmetrization.
converted={'energy_eV':float(model['e'][0]*20),'forces_eV_A':model['f_0']*1,'stress_eV_A3':model['s_0']*units.GPa}
converted['stress_eV_A3']=(converted['stress_eV_A3']+converted['stress_eV_A3'].T)/2
conversion={}
for key,a in converted.items():
    b=np.asarray(obs[key]);diff=np.asarray(a,dtype=np.float64)-b
    conversion[key]={'signed_difference_model_conversion_minus_ASE':diff.tolist(),'max_abs_difference':float(np.abs(diff).max()),'exact_equal':bool(np.array_equal(a,b))}
    ck('model_ASE_conversion:'+key,np.array_equal(a,b))
save('model-ASE-consistency.json',{'ASE_GPa_eV_A3':units.GPa,'checks':conversion})
comparisons={}
for name,ref in protocol['references'].items():
    path=R/ref['path'];ck('reference_hash:'+name,sha(path)==ref['sha256'])
    reference=json.loads(path.read_text());comparisons[name]={}
    for key,tol in protocol['original_acceptance'].items():
        new=np.asarray(obs[key],dtype=np.float64);old=np.asarray(reference[key],dtype=np.float64)
        assert new.shape==old.shape
        difference=new-old
        comparisons[name][key]={'shape':list(new.shape),'finite':bool(np.isfinite(new).all() and np.isfinite(old).all()),'signed_difference':difference.tolist(),'max_abs_difference':float(np.abs(difference).max()),'exact_equal':bool(np.array_equal(new,old)),**tol,'passed':bool(np.isfinite(difference).all() and (np.abs(difference)<=tol['atol']).all())}
save('comparisons.json',{'convention':'new minus reference','comparisons':comparisons,'historical_D1_numerical_comparison':None,'historical_D1_reason':'No persisted observations; not reconstructed.'})
diagnostic={}
old=R/'evidence/diagnosis-20261023/D1-control'
for archive in ['input-arrays','neighbors','graph']:
    with np.load(old/(archive+'.npz'),allow_pickle=False) as f:
        diagnostic[archive]={k:{'exact_equal':bool(np.array_equal(a,f[k])),'shape':list(a.shape),'signed_difference':(a.astype(np.float64)-f[k].astype(np.float64)).tolist()} for k,a in raw[archive].items()}
diagnostic['model_parameter_hashes_exact_equal']=json.loads((D/'model-tensor-hashes.json').read_text())==json.loads((old/'model-tensor-hashes.json').read_text())
diagnostic['scope']='D1 recorded input/graph/weights only. Its neighbor list came from an additional query; this run intercepted the consumed query. No historical baseline graphs or D1 numerical outputs exist.'
save('D1-capture-comparison.json',diagnostic)
capture_passed=all(c['passed'] for c in checks)
numerical_passed=all(v['passed'] for name in ['baseline-001','baseline-002'] for v in comparisons[name].values())
save('integrity.json',{'passed':capture_passed,'checks':checks})
save('decision.json',{'GitHub_checkpoint_resume':'verified','recorder_capture_integrity':'passed' if capture_passed else 'failed','numerical_replay_acceptance':'passed' if numerical_passed else 'failed','historical_restoration_acceptance':'failed; unchanged','D1_status':'instrumentation failure; missing numerical outputs unchanged','evaluations':1,'next_inference':'none authorized by this protocol','stopped':True,'stop_reason':'Comparison mismatch' if not numerical_passed else ('Integrity mismatch' if not capture_passed else 'One-evaluation protocol complete'),'full_migration_complete':False,'local_fallback':'retained without overlap','publication':'not performed; additive export for parent review only'})
print(json.dumps({'capture_integrity':capture_passed,'numerical_acceptance':numerical_passed,'failed_integrity_checks':[x for x in checks if not x['passed']],'max_abs_differences':{name:{k:v['max_abs_difference'] for k,v in c.items()} for name,c in comparisons.items()}}))
