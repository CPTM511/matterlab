"""Inert metadata guards; never imports a scientific package."""
import json,hashlib,os,subprocess,datetime as dt
from pathlib import Path
HEAD='b2895ba36bbab3e93e409a0c3975d0250c8134f6'
BUNDLE=Path(__file__).resolve().parent
ANCHOR=Path('PRIVATE_PATH_ALIAS_2')
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return dt.datetime.now(dt.timezone.utc)
def claim(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(v,f)
def verify_bundle():
 f=read(BUNDLE/'freeze.json')
 if f['status']!='reviewed_for_parent_release':raise ValueError('Preparation is not execution-ready')
 m=read(BUNDLE/'implementation-manifest.json')
 if sha(BUNDLE/'implementation-manifest.json')!=f['implementation_manifest_sha256']:raise ValueError('Manifest changed')
 paths=list(BUNDLE.rglob('*'))
 if any(p.is_symlink() for p in paths):raise ValueError('Bundle symlink forbidden')
 actual={str(p.relative_to(BUNDLE)) for p in paths if p.is_file()}
 if actual!=set(m['files'])|{'implementation-manifest.json','freeze.json'}:raise ValueError('Unexpected/missing bundle file')
 for n,h in m['files'].items():
  if Path(n).is_absolute() or '..' in Path(n).parts or not (BUNDLE/n).resolve().is_relative_to(BUNDLE.resolve()):raise ValueError('Unconfined source path')
  if sha(BUNDLE/n)!=h:raise ValueError('Frozen source/reference changed')
 return f

def release_gate(release,freeze,t):
 for k in ['execution_released','ownership_confirmed','no_other_physical_job','fallback_nonoverlap','included_available','usage_unambiguous','all_displayed_windows_recorded']:
  if release.get(k) is not True:raise ValueError('Missing release/ownership/usage field: '+k)
 if release.get('extra_spending_allowed') is not False:raise ValueError('Spending permission invalid')
 if release.get('head')!=HEAD or release.get('freeze_sha256')!=sha(BUNDLE/'freeze.json'):raise ValueError('Wrong release binding')
 if release.get('bundle')!=str(BUNDLE):raise ValueError('Wrong bundle')
 for k in ['usage_observed_at','ownership_observed_at']:
  age=(t-dt.datetime.fromisoformat(release[k])).total_seconds()
  if not 0<=age<=900:raise ValueError('Stale/future gate')
 windows=release.get('included_windows_consumed_fraction')
 if not isinstance(windows,list) or not windows or any(type(x) not in (int,float) or not 0<=x<.8 for x in windows):raise ValueError('Usage unavailable/at reserve')
 start=dt.datetime.fromisoformat(release['investigation_start'])
 if not 0<=(t-start).total_seconds()<600:raise ValueError('Investigation clock invalid/expired')
 return start

def context():
 f=verify_bundle();r=read(os.environ['ASSOCIATION_RELEASE']);release_gate(r,f,now())
 a=read(ANCHOR)
 if a['release_sha256']!=sha(os.environ['ASSOCIATION_RELEASE']) or a['freeze_sha256']!=sha(BUNDLE/'freeze.json'):raise ValueError('Release/freeze changed after admission')
 if a['investigation_start']!=r['investigation_start'] or a['controller_pid']!=int(os.environ['ASSOCIATION_CONTROLLER_PID']) or os.getppid()!=a['controller_pid']:raise ValueError('Parent/attempt mismatch')
 if a['supervisor_pid']!=int(os.environ['ASSOCIATION_SUPERVISOR_PID']):raise ValueError('Supervisor binding changed')
 return freshness(r,now())

def coordination(root):
 root=Path(root)
 def git(*args):return subprocess.check_output(['git','-C',str(root),*args],text=True,timeout=15).strip()
 if git('rev-parse','HEAD')!=HEAD or git('status','--porcelain'):raise ValueError('Dirty/wrong public checkout')
 if git('ls-remote','https://github.com/CPTM511/matterlab.git','refs/heads/main').split()[0]!=HEAD:raise ValueError('Remote changed')
 state=read(root/'project/STATE.json')
 if state['active_work'] or any(isinstance(v,dict) and ('physical_job_active' in v and v['physical_job_active'] is not False) for v in state.values()):raise ValueError('Public active work')
 allowed={os.getpid(),os.getppid(),int(os.environ.get('ASSOCIATION_CONTROLLER_PID','0')),int(os.environ.get('ASSOCIATION_SUPERVISOR_PID','0'))}
 for p in Path('/proc').iterdir():
  if p.name.isdigit() and int(p.name) not in allowed:
   try:
    if (p/'comm').read_text().strip().startswith(('python','matterlab')):raise ValueError('Other Python/scientific process')
   except FileNotFoundError:pass

def paths_gate(root,out,bundle):
 root,out,bundle=map(lambda p:Path(p).resolve(),(root,out,bundle))
 if any(a.is_relative_to(b) or b.is_relative_to(a) for a,b in [(out,root),(out,bundle)]):raise ValueError('Output overlaps source/freeze')
 if out.exists():raise ValueError('Output already exists')
 return root,out,bundle

def freshness(release,t):
 for k in ('usage_observed_at','ownership_observed_at'):
  age=(t-dt.datetime.fromisoformat(release[k])).total_seconds()
  if not 0<=age<=900:raise ValueError('Boundary freshness expired')
 elapsed=(t-dt.datetime.fromisoformat(release['investigation_start'])).total_seconds()
 if not 0<=elapsed<600:raise ValueError('Boundary investigation expired')
 return release
