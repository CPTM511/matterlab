"""Saved-output diagnostics only. Never changes the frozen protocol, gate or runner."""
import os,json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal
P=Path(os.environ['MATTERLAB_CONTRAST_OUTPUT']);R=Path(os.environ['MATTERLAB_ROOT']);R1=Path(os.environ['MATTERLAB_R1_REFERENCE'])
def load(p):return json.loads(p.read_text())
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=load(P/'C0-control/runtime.json');b=load(P/'C1-default/runtime.json')
differences={k:{'control':a[k],'altered':b[k]} for k in a if a[k]!=b[k]}
na=dict(a);nb=dict(b)
for x in [na,nb]:
    x.pop('condition');x.pop('cpu_capability');x['environment_controls']=dict(x['environment_controls']);x['environment_controls'].pop('ATEN_CPU_CAPABILITY')
    x['torch_build']='\n'.join(line for line in x['torch_build'].splitlines() if not line.strip().startswith('- CPU capability usage:'))
save('runtime-comparison-diagnosis.json',{'classification':'Post-hoc explanation only; frozen gate remains failed and no repeat is authorized','raw_differences':differences,'all_other_fields_equal_after_removing_duplicate_capability_line':na==nb,'omitted_field':'torch_build line CPU capability usage: duplicates the intended observed capability change','frozen_gate_overridden':False,'C2_launched':False})
def flat(a):
    if isinstance(a,list):
        for item in a:yield from flat(item)
    else:yield a
scalar=[]
for cond in ['C0-control','C1-default']:
    obs=load(P/cond/'observations.json');records=load(P/(cond+'-comparisons.json'))['comparisons']
    for name,record in records.items():
        ref=R1 if name=='R1' else (P/name if name=='C0-control' else R/'evidence/restoration-20261023'/name)
        old=load(ref/'observations.json')
        for key,v in record['observables'].items():
            d=[float(Decimal.from_float(float(x))-Decimal.from_float(float(y))) for x,y in zip(flat(obs[key]),flat(old[key]),strict=True)]
            scalar.append({'condition':cond,'reference':name,'quantity':key,'components':len(d),'signed_components_match':d==list(flat(v['signed_difference'])),'maximum_matches':max(map(abs,d))==v['max_abs_difference'],'threshold_decision_matches':all(abs(x)<=v['atol'] for x in d)==v['passed']})
save('scalar-sanity-review.json',{'scope':'Independent standard-library Decimal/scalar implementation, same primary task, no inference','checks':scalar,'passed':all(x['signed_components_match'] and x['maximum_matches'] and x['threshold_decision_matches'] for x in scalar)})
gates={c:load(P/(c+'-gate.json')) for c in ['C0-control','C1-default']}
save('raw-capture-review.json',{'scope':'Separated saved-array capture checks from the frozen bundled gate; does not change that gate','conditions':{c:{'raw_capture_checks_passed':all(x['passed'] for x in g['checks'] if x['name']!='other_effective_runtime_settings'),'frozen_bundled_capture_integrity_passed':g['capture_integrity_passed'],'frozen_comparison_assumptions_passed':g['comparison_assumptions_passed'],'failed_checks':[x['name'] for x in g['checks'] if not x['passed']]} for c,g in gates.items()}})
execution=[load(P/(c+'-execution.json')) for c in ['C0-control','C1-default']]
save('decision.json',{'status':'Stopped after two evaluations at frozen C1 runtime-comparison gate','new_evaluations':2,'C0':'Capture/integrity and exact R1 comparison passed, including all six raw model-output tensors','C1':'Raw capture and input/graph/parameter invariants passed; frozen bundled gate failed on duplicate capability text in torch_build','C2':'Not run; frozen gate prohibits repeat','total_calculation_process_wall_seconds':sum(x['wall_seconds'] for x in execution),'observed_sensitivity':'Energy unchanged; finite force/stress changes under ATEN_CPU_CAPABILITY=default with identical input/graph/weights and only intended capability metadata changes. Single altered-process observation; altered repeatability untested.','original_numerical_acceptance':'Failed for both C0 and C1; unchanged thresholds and historical failures','historical_cause':'Not identified; no historical CPU/backend metadata inferred','next_research_decision':'The current derivative outputs are sensitive to supported ATen dispatch selection at invariant captured input/graph/weights. Do not search settings to fit historical baselines. Parent should first review whether confirming altered-process repeatability under a separately predeclared semantic runtime comparison is decision-relevant; no such inference is authorized by this completed protocol.','full_migration_complete':False,'fallback':'Retained without overlap','publication':'Not performed; review candidate only','physical_job_active':False})
preservation=load(P/'R1-preservation-before-private.json')
assert all(sha(Path(path))==h for path,h in preservation.items())
oldmanifest=load(R1.parent/'private-manifest.json')['files'];assert all(sha(R1.parent/name)==h for name,h in oldmanifest.items())
public_root=R1.parent.parent/'public-export/evidence/repaired-recorder-20261023';pm=load(public_root/'manifest.json')['files'];assert all(sha(public_root/name)==h for name,h in pm.items())
save('R1-preservation.json',{'original_export_archive_sha256':sha(R1.parent.parent/'repaired-recorder-additive-export.tar.gz'),'original_public_manifest_sha256':sha(public_root/'manifest.json'),'original_protocol_sha256':sha(R1.parent/'protocol.json'),'all_original_private_manifest_entries_verified':len(oldmanifest),'all_original_public_manifest_entries_verified':len(pm),'unchanged':True,'scope':'R1 private science/protocol and original 106-file export/archive retained unchanged'})
remote=subprocess.check_output(['git','-C',str(R),'ls-remote','origin','refs/heads/main'],text=True).split()[0]
assert remote=='2c4a667a4c75488cb2ee2bb3e26a19cc6ab19ea1'
assert not subprocess.check_output(['git','-C',str(R),'status','--porcelain'],text=True).strip()
assert not load(R/'project/STATE.json')['active_work']
source=load(R/'publication/manifest.json')['files'];assert all(sha(R/name)==h for name,h in source.items())
save('public-preservation.json',{'remote_main':remote,'verified_at_utc':datetime.now(timezone.utc).isoformat(),'public_entries_reverified':len(source),'clean_source_checkout':True,'coordination_active_work':[],'current_cloud_ownership':'Parent assignment; read-only reviewer has no physical job','publication_audit_code_sha256':sha(R/'tools/export_public.py')})
print(json.dumps({'stopped':True,'evaluations':2,'total_calculation_seconds':sum(x['wall_seconds'] for x in execution),'scalar_components':sum(x['components'] for x in scalar),'R1_preserved':True}))
