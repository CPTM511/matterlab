import os, sys, json, hashlib, subprocess, importlib.metadata as md, importlib, platform
from pathlib import Path
from datetime import datetime, timezone
R=Path(os.environ['MATTERLAB_ROOT'])
P=Path(os.environ['MATTERLAB_CONTRAST_OUTPUT'])
sys.path.insert(0,str(R/'src'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
checks=[]
def check(n,actual,expected):
    checks.append(dict(name=n,actual=actual,expected=expected,passed=actual==expected))
    save('preflight.json',dict(checks=checks,passed=all(x['passed'] for x in checks)))
    assert actual==expected,n
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True).strip()
check('checkpoint',git('rev-parse','HEAD'),'2c4a667a4c75488cb2ee2bb3e26a19cc6ab19ea1')
check('coordination_parent',git('rev-parse','HEAD^'),'f1fdd7fbe07b05c60cb2c15f808ddaa6c13a06bb')
check('remote_main',git('ls-remote','origin','refs/heads/main').split()[0],git('rev-parse','HEAD'))
check('clean_checkout',git('status','--porcelain'),'')
check('active_work',json.loads((R/'project/STATE.json').read_text())['active_work'],[])
check('publication_manifest',sha(R/'publication/manifest.json'),'dc15e4f699346755bb2c12cfb8bb4d36c648827fee23c8f509528636263e808c')
check('publication_audit',sha(R/'publication/audit.json'),'2736cf96d41380a71ac08ef40ff2eb13a4a2aaa6df391895c3e0f499df114bcd')
manifest=json.loads((R/'publication/manifest.json').read_text())['files']
for name,value in manifest.items():check('public:'+name,sha(R/name),value)
tracked=set(git('ls-files').splitlines())
check('complete_manifest_coverage',sorted(tracked-set(manifest)),['publication/manifest.json'])
code=json.loads((R/'evidence/restoration-20261023/replay/code.json').read_text())
check('physics_commit',code['git_head'],'3319dc595397f68c0e7a3326e64c2b27ae799027')
for name,value in code['sources_sha256'].items():
    check('source:'+name,sha(R/name),value)
    check('physics_git_blob:'+name,hashlib.sha256(subprocess.check_output(['git','-C',str(R),'show',code['git_head']+':'+name])).hexdigest(),value)
runtime=json.loads((R/'evidence/restoration-20261023/runtime-hashes.json').read_text())
check('python_binary',sha(Path(sys.executable).resolve()),runtime['python_executable_sha256'])
expected=json.loads((R/'evidence/restoration-20261023/environment-current.json').read_text())
packages={d.metadata['Name']:d.version for d in md.distributions()}
check('all_dependency_versions',packages,expected['packages'])
import chgnet
C=Path(chgnet.__file__).parent
for name,value in runtime['chgnet_python_sources'].items():check('chgnet_source:'+name,sha(C/name),value)
for name,value in expected['model_checkpoints'].items():check('checkpoint:'+name,sha(C/name),value)
for name in code['sources_sha256']:
    mod=importlib.import_module(name.replace('src/','').replace('/','.').removesuffix('.py')) if not name.endswith('__main__.py') else None
    if mod:check('loaded:'+name,str(Path(mod.__file__).resolve()),str((R/name).resolve()))
check('input',sha(R/'runs/round-001-en/generated/R-CaTiO3.cif'),'1fe444e55772222e8f09e8b333901a94efdc701ef96909a4c22462087185cdd0')
check('config_raw',sha(R/'configs/round-001.json'),'e270d736f658e73a5491ed75a5aaa7269ecb53fd923615e066ea807d3ec70601')
config=json.loads((R/'configs/round-001.json').read_text())
check('config_semantic',config,json.loads((R/'evidence/restoration-20261023/replay/config.json').read_text()))
# Installed RECORD hashes provide an additional local integrity check, not external supply-chain attestation.
record_counts={};native={}
import base64
for pkg in ['chgnet','torch','numpy','scipy','ase','pymatgen']:
    dist=md.distribution(pkg); count=0
    for f in dist.files or []:
        if f.hash and f.hash.mode=='sha256':
            path=dist.locate_file(f)
            actual=sha(path)
            expected_hash=base64.urlsafe_b64decode(f.hash.value+'===').hex()
            if actual!=expected_hash:check('RECORD:'+pkg+':'+str(f),actual,expected_hash)
            count+=1
            if '.so' in str(f):native[pkg+':'+str(f)]=actual
    record_counts[pkg]=count
save('installed-record-verification.json',dict(counts=record_counts,passed=True,native_library_sha256=native,scope='Local installed RECORD consistency; no historical native-library digest reference.'))
save('environment.json',dict(utc=datetime.now(timezone.utc).isoformat(),python=sys.version,executable=str(Path(sys.executable).resolve()),platform=platform.platform(),packages=packages,affinity_available=sorted(os.sched_getaffinity(0))))
(P/'processes-before.txt').write_text(subprocess.check_output(['ps','-eo','pid,ppid,etime,comm,args'],text=True))
(P/'cpu.txt').write_text(subprocess.check_output(['lscpu'],text=True))
print(json.dumps(dict(passed=True,checks=len(checks),manifest_entries=len(manifest),record_files=sum(record_counts.values()))))
