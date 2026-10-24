"""Bounded contrast runner and saved-data verifier. One invocation per predeclared condition."""
import os,sys,json,hashlib,time,subprocess
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from ase import units
P=Path(os.environ['MATTERLAB_CONTRAST_OUTPUT']);R=Path(os.environ['MATTERLAB_ROOT']);R1=Path(os.environ['MATTERLAB_R1_REFERENCE'])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def arrays(p):
    result={}
    for stem in ['input-arrays','neighbors','graph','model-output']:
        with np.load(p/(stem+'.npz'),allow_pickle=False) as f:result[stem]={k:f[k].copy() for k in f.files}
    return result
def compare(a,b,atol=0):
    a=np.asarray(a);b=np.asarray(b)
    if a.shape!=b.shape:return {'comparable':False,'shape':list(a.shape),'reference_shape':list(b.shape),'signed_difference':None,'passed':False,'exact_equal':False}
    d=a.astype(np.float64)-b.astype(np.float64)
    return {'comparable':True,'shape':list(a.shape),'dtype':str(a.dtype),'reference_dtype':str(b.dtype),'finite':bool(np.isfinite(a).all() and np.isfinite(b).all()),'signed_difference':d.tolist(),'max_abs_difference':float(np.abs(d).max()),'exact_equal':bool(np.array_equal(a,b)),'atol':atol,'rtol':0,'passed':bool(np.isfinite(d).all() and (np.abs(d)<=atol).all())}
def analyze(condition):
    D=P/condition;checks=[]
    def ck(name,passed):checks.append({'name':name,'passed':bool(passed)})
    protocol=load(P/'protocol.json');obs=load(D/'observations.json');raw=arrays(D)
    ck('execution',load(P/(condition+'-execution.json'))['returncode']==0)
    for name,value in load(D/'manifest.json')['files'].items():ck('manifest:'+name,sha(D/name)==value)
    for stem,meta in [('input-arrays','input-array-hashes'),('neighbors','neighbor-hashes'),('graph','graph-hashes'),('model-output','model-output-hashes')]:
        records=load(D/(meta+'.json'));ck(stem+':keys',set(records)==set(raw[stem]))
        for k,a in raw[stem].items():
            h=records[k];ck(stem+':'+k,a.size and np.isfinite(a).all() and str(a.dtype)==h['dtype'] and list(a.shape)==h['shape'] and hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()==h['data_sha256'])
    count=load(D/'capture-summary.json');runtime=load(D/'runtime.json')
    ck('one_graph_one_model',count['graph_calls']==count['model_calls']==1)
    ck('cpu_threads_seed',runtime['device']=='cpu' and runtime['torch_num_threads']==runtime['torch_num_interop_threads']==1 and runtime['cpu_affinity']==[0] and runtime['seed']==20261024)
    ck('shapes',np.asarray(obs['forces_eV_A']).shape==(20,3) and np.asarray(obs['stress_eV_A3']).shape==(3,3) and obs['atoms']==20 and not obs['relaxation_performed'])
    ck('graph_keys',set(raw['graph'])=={'atomic_number','atom_frac_coord','atom_graph','neighbor_image','directed2undirected','undirected2directed','bond_graph','lattice'})
    ck('model_keys',set(raw['model-output'])=={'atoms_per_graph','m_0','crystal_fea','e','f_0','s_0'})
    n=raw['neighbors'];g=raw['graph'];m=raw['model-output']
    ck('consumed_neighbors',np.array_equal(g['atom_graph'],np.column_stack([n['center'],n['neighbor']])) and np.array_equal(g['neighbor_image'],n['image'].astype(np.float32)))
    converted={'energy_eV':m['e'][0]*20,'forces_eV_A':m['f_0'],'stress_eV_A3':m['s_0']*units.GPa}
    converted['stress_eV_A3']=(converted['stress_eV_A3']+converted['stress_eV_A3'].T)/2
    conversion={k:compare(v,obs[k]) for k,v in converted.items()}
    ck('model_ASE_conversion',all(v['exact_equal'] for v in conversion.values()))
    refs={'R1':R1}
    if condition!='C0-control':refs['C0-control']=P/'C0-control'
    if condition=='C2-default-repeat':refs['C1-default']=P/'C1-default'
    comparisons={};all_invariants=True;all_outputs={};all_models={};runtimes={}
    for name,ref in refs.items():
        rraw=arrays(ref);robs=load(ref/'observations.json')
        c={'observables':{k:compare(obs[k],robs[k],v['atol']) for k,v in protocol['original_acceptance'].items()},'arrays':{}}
        same=True
        for stem,values in raw.items():
            assert set(values)==set(rraw[stem]), 'Reference array key mismatch'
            c['arrays'][stem]={k:compare(v,rraw[stem][k]) for k,v in values.items()}
            if stem!='model-output':same=bool(same and all(x['exact_equal'] and x['dtype']==x['reference_dtype'] for x in c['arrays'][stem].values()))
        c['model_parameter_hashes_equal']=load(D/'model-tensor-hashes.json')==load(ref/'model-tensor-hashes.json')
        same=bool(same and c['model_parameter_hashes_equal'] and (D/'input.cif').read_bytes()==(ref/'input.cif').read_bytes() and (D/'config-original.json').read_bytes()==(ref/'config-original.json').read_bytes())
        c['input_graph_parameter_invariants']=same;all_invariants=bool(all_invariants and same)
        all_outputs[name]=all(v['exact_equal'] for v in c['observables'].values())
        all_models[name]=all(v['exact_equal'] and v['dtype']==v['reference_dtype'] for v in c['arrays']['model-output'].values())
        comparisons[name]=c
        rr=load(ref/'runtime.json');a=dict(runtime);b=dict(rr)
        for x in [a,b]:
            x.pop('condition');x.pop('cpu_capability');x['environment_controls']=dict(x['environment_controls']);x['environment_controls'].pop('ATEN_CPU_CAPABILITY')
        runtimes[name]={'other_effective_settings_exact_equal':a==b}
    for name in ['baseline-001','baseline-002','replay']:
        robs=load(R/'evidence/restoration-20261023'/name/'observations.json')
        comparisons[name]={'observables':{k:compare(obs[k],robs[k],v['atol']) for k,v in protocol['original_acceptance'].items()}}
    ck('input_graph_parameter_invariants',all_invariants)
    ck('other_effective_runtime_settings',all(x['other_effective_settings_exact_equal'] for x in runtimes.values()))
    expected_cap='AVX512' if condition=='C0-control' else 'NO AVX'
    expected_env=None if condition=='C0-control' else 'default'
    ck('effective_intervention',runtime['cpu_capability']==expected_cap and runtime['environment_controls']['ATEN_CPU_CAPABILITY']==expected_env)
    capture_pass=all(x['passed'] for x in checks)
    if condition=='C0-control':gate=bool(capture_pass and all_outputs['R1'] and all_models['R1'])
    elif condition=='C1-default':gate=bool(capture_pass)
    else:gate=bool(capture_pass and all_outputs['C1-default'] and all_models['C1-default'])
    result={'condition':condition,'capture_integrity_passed':capture_pass,'comparison_assumptions_passed':gate,'checks':checks,'observables_exact_equal':all_outputs,'model_outputs_exact_equal':all_models,'runtime_comparison':runtimes,'changed_scientific_observable_vs_control':condition!='C0-control' and not all_outputs.get('C0-control',True),'original_baseline_acceptance':all(v['passed'] for name in ['baseline-001','baseline-002'] for v in comparisons[name]['observables'].values()),'comparisons_file':condition+'-comparisons.json'}
    save(condition+'-comparisons.json',{'convention':'condition minus named reference','comparisons':comparisons,'model_ASE_conversion':conversion,'D1_numerical_comparison':None})
    save(condition+'-gate.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in {'checks','runtime_comparison'}}))
    return result
def run(condition):
    protocol=load(P/'protocol.json');assert sha(P/'protocol.json')==load(P/'protocol-freeze.json')['sha256']
    assert sha(Path(__file__))==protocol['runner_sha256']
    start=load(P/'investigation-start.json')['started_at_utc'];investigation_elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(start)).total_seconds();assert investigation_elapsed<1800
    assert load(P/'preflight.json')['passed']
    assert sha(R1/'manifest.json')==protocol['reference_R1_manifest_sha256']
    for name,value in load(R1/'manifest.json')['files'].items():assert sha(R1/name)==value
    assert sha(R/'evidence/diagnosis-20261023/capture_helpers.py')==protocol['capture_helpers_sha256']
    assert subprocess.check_output(['git','-C',str(R),'ls-remote','origin','refs/heads/main'],text=True).split()[0]==protocol['public_commit']
    assert not load(R/'project/STATE.json')['active_work']
    if condition=='C1-default':assert load(P/'C0-control-gate.json')['comparison_assumptions_passed']
    if condition=='C2-default-repeat':
        gate=load(P/'C1-default-gate.json');assert gate['comparison_assumptions_passed'] and gate['changed_scientific_observable_vs_control']
    assert condition in ['C0-control','C1-default','C2-default-repeat']
    for old in P.glob('*-execution.json'):assert load(old)['returncode']==0
    elapsed=sum(load(old)['wall_seconds'] for old in P.glob('*-execution.json'))
    assert elapsed<600
    with (P/(condition+'-ATTEMPT.json')).open('x') as f:json.dump({'started_at_utc':datetime.now(timezone.utc).isoformat(),'condition':condition},f)
    recorder=R/'evidence/diagnosis-20261023/diagnostic_eval_proposed.py'
    assert sha(recorder)==protocol['recorder_sha256']
    for rel,h in load(R/'evidence/restoration-20261023/replay/code.json')['sources_sha256'].items():assert sha(R/rel)==h
    env=dict(os.environ)
    for key in ['ATEN_CPU_CAPABILITY','MKL_CBWR']:env.pop(key,None)
    if condition!='C0-control':env['ATEN_CPU_CAPABILITY']='default'
    for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS']:env[key]='1'
    env.update(MATTERLAB_ROOT=str(R),MATTERLAB_EXPECTED_CODE=str(R/'evidence/restoration-20261023/replay/code.json'),MATTERLAB_CONDITION=condition,PYTHONHASHSEED='20261024',PYTHONPATH=str(R/'src'),PYTHONDONTWRITEBYTECODE='1')
    bootstrap="import os,sys,random,runpy; os.sched_setaffinity(0,{0}); random.seed(20261024); import numpy as np; np.random.seed(20261024); sys.path.insert(0,"+repr(str(recorder.parent))+"); sys.argv=["+repr(str(recorder))+","+repr(str(P/condition))+"]; runpy.run_path(sys.argv[0],run_name='__main__')"
    remaining_investigation=1800-(datetime.now(timezone.utc)-datetime.fromisoformat(start)).total_seconds();assert remaining_investigation>0
    begin=time.monotonic();result={'condition':condition,'started_at_utc':datetime.now(timezone.utc).isoformat(),'timeout':False,'maximum_remaining_wall_seconds':min(600-elapsed,remaining_investigation),'protocol_sha256':sha(P/'protocol.json')}
    with (P/(condition+'.log')).open('wb') as log:
        try:result['returncode']=subprocess.run([sys.executable,'-c',bootstrap],env=env,cwd=P,stdout=log,stderr=subprocess.STDOUT,timeout=min(600-elapsed,remaining_investigation)).returncode
        except subprocess.TimeoutExpired:result.update(returncode=None,timeout=True)
        except Exception as e:result.update(returncode=None,exception=repr(e))
    result.update(wall_seconds=time.monotonic()-begin,ended_at_utc=datetime.now(timezone.utc).isoformat());save(condition+'-execution.json',result)
    if result['returncode']!=0:print(json.dumps(result));return
    analyze(condition)
if __name__=='__main__':
    if sys.argv[1]=='run':run(sys.argv[2])
    else:analyze(sys.argv[2])
