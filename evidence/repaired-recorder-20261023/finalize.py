import os,json,hashlib,shutil,subprocess,importlib.metadata as md
from pathlib import Path
from datetime import datetime,timezone
P=Path(os.environ['MATTERLAB_VALIDATION_OUTPUT']);R=Path(os.environ['MATTERLAB_ROOT'])
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
for name in ['baseline-001','baseline-002','replay']:
    for file in ['observations.json','code.json','config.json','input.cif']:
        dest=P/'references'/name/file;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(R/'evidence/restoration-20261023'/name/file,dest)
for package in ['chgnet','torch','numpy','scipy','ase','pymatgen']:
    d=md.distribution(package)
    for file in d.files or []:
        if any(word in str(file).upper().split('/')[-1] for word in ['LICENSE','COPYING','NOTICE']):
            target=P/'licenses'/package/str(file);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(d.locate_file(file),target)
import chgnet
C=Path(chgnet.__file__).parent
for name in json.loads((R/'evidence/restoration-20261023/runtime-hashes.json').read_text())['chgnet_python_sources']:
    target=P/'source_snapshot/chgnet'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(C/name,target)
manifest=json.loads((R/'publication/manifest.json').read_text())['files']
errors=[name for name,value in manifest.items() if sha(R/name)!=value]
status=subprocess.check_output(['git','-C',str(R),'status','--porcelain'],text=True)
remote=subprocess.check_output(['git','-C',str(R),'ls-remote','origin','refs/heads/main'],text=True).strip()
save('preservation-after.json',{'utc':datetime.now(timezone.utc).isoformat(),'publication_entries_reverified':len(manifest),'errors':errors,'git_status':status,'remote_main':remote.split()[0],'original_publication_manifest_sha256':sha(R/'publication/manifest.json'),'original_audit_sha256':sha(R/'publication/audit.json'),'physical_job_active':False,'scope':'Final local process check and recorded completed process; current public active_work remains empty.'})
assert not errors and not status and remote.split()[0]=='2c4a667a4c75488cb2ee2bb3e26a19cc6ab19ea1'
(P/'processes-after.txt').write_text(subprocess.check_output(['ps','-eo','pid,ppid,etime,comm,args'],text=True))
state=json.loads((R/'project/STATE.json').read_text())
state['updated_at_utc']=datetime.now(timezone.utc).isoformat()
state['cloud_migration']['cloud_resume_verified']=True
state['cloud_migration']['cloud_acceptance_complete']=False
state['cloud_migration']['status']='Independent isolated GitHub-backed checkpoint resume verified. One repaired-recorder evaluation captured all required arrays and exactly matched the restored result, but failed original baseline force/stress tolerances. Full migration remains incomplete; fallback retained.'
state['active_work']=[]
state['next_action']='Parent review of the additive R1 evidence export and unchanged numerical failure. No further inference under the completed one-evaluation protocol. Any later discriminating condition requires a separate declared protocol and fresh usage/ownership gates.'
state['repaired_recorder_validation']={'evidence':'evidence/repaired-recorder-20261023','evaluations':1,'capture_integrity':'passed','original_numerical_acceptance':'failed; unchanged','matches_restored_observations_exactly':True,'physical_job_active':False,'published':False}
save('proposed-STATE.json',state)
save('resume-checkpoint.json',{'public_source_commit':'2c4a667a4c75488cb2ee2bb3e26a19cc6ab19ea1','coordination_parent':'f1fdd7fbe07b05c60cb2c15f808ddaa6c13a06bb','github_backed_resume_verified':True,'recorder_capture_integrity':'passed','numerical_replay_acceptance':'failed','attempts':1,'active_physical_job':False,'fallback':'retained without overlap','original_public_evidence':'unchanged','next_action':state['next_action'],'publication':'parent review pending; no publication performed','schedule':'unchanged'})
print(json.dumps({'preservation_passed':True,'new_state_is_proposal_only':True}))
