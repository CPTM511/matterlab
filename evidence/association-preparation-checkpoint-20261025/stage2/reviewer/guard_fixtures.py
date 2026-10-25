import sys,importlib.util,json,tempfile,hashlib,copy,datetime
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent;source=ROOT/'candidate-v2/guards.py'
spec=importlib.util.spec_from_file_location('review_guards',source);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
checks=[]
def check(n,f,reject=False):
 try:v=f()
 except Exception as e:checks.append({'name':n,'pass':reject,'exception':type(e).__name__});return
 checks.append({'name':n,'pass':not reject and v is not False})
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='fixture-only-',dir=ROOT/'reviewer') as tmp:
 base=Path(tmp);bundle=base/'synthetic-bundle';bundle.mkdir();g.BUNDLE=bundle;g.ANCHOR=base/'fixture-only-marker.json'
 (bundle/'module.py').write_text('SYNTHETIC = True\n')
 manifest={'files':{'module.py':h(bundle/'module.py')}}
 def reset(status='reviewed_for_parent_release'):
  (bundle/'implementation-manifest.json').write_text(json.dumps(manifest));freeze={'status':status,'implementation_manifest_sha256':h(bundle/'implementation-manifest.json')};(bundle/'freeze.json').write_text(json.dumps(freeze));return freeze
 freeze=reset();check('synthetic_bundle_pass',g.verify_bundle)
 t=datetime.datetime(2030,1,1,tzinfo=datetime.timezone.utc)
 release={k:True for k in ['execution_released','ownership_confirmed','no_other_physical_job','fallback_nonoverlap','included_available','usage_unambiguous','all_displayed_windows_recorded']}
 release.update(extra_spending_allowed=False,head=g.HEAD,freeze_sha256=h(bundle/'freeze.json'),bundle=str(bundle),usage_observed_at=(t-datetime.timedelta(seconds=1)).isoformat(),ownership_observed_at=(t-datetime.timedelta(seconds=1)).isoformat(),included_windows_consumed_fraction=[0.1],investigation_start=(t-datetime.timedelta(seconds=1)).isoformat())
 check('synthetic_release_pass',lambda:g.release_gate(release,freeze,t))
 cases=[]
 for k in ['execution_released','ownership_confirmed','no_other_physical_job','fallback_nonoverlap','included_available','usage_unambiguous','all_displayed_windows_recorded']:cases.append((k,False))
 cases.extend([('extra_spending_allowed',True),('head','wrong'),('freeze_sha256','0'*64),('bundle','wrong')])
 for k in ['usage_observed_at','ownership_observed_at']:
  cases.extend([(k,(t-datetime.timedelta(seconds=901)).isoformat()),(k,(t+datetime.timedelta(seconds=1)).isoformat())])
 for w in [[],None,[True],[0.8],[-0.1],[float('nan')],[float('inf')],['0.1']]:cases.append(('included_windows_consumed_fraction',w))
 cases.extend([('investigation_start',(t-datetime.timedelta(seconds=600)).isoformat()),('investigation_start',(t+datetime.timedelta(seconds=1)).isoformat())])
 for i,(k,v) in enumerate(cases):
  bad=copy.deepcopy(release);bad[k]=v;check('release_reject_'+str(i)+'_'+k,lambda bad=bad:g.release_gate(bad,freeze,t),True)
 reset('preparation_only_execution_blocked');check('preparation_status_blocks',g.verify_bundle,True);reset()
 (bundle/'extra.py').write_text('');check('extra_source_blocks',g.verify_bundle,True);(bundle/'extra.py').unlink()
 (bundle/'cache.pyc').write_bytes(b'fixture');check('extra_bytecode_blocks',g.verify_bundle,True);(bundle/'cache.pyc').unlink()
 original=(bundle/'module.py').read_bytes();(bundle/'module.py').write_bytes(original+b'\n');check('changed_source_blocks',g.verify_bundle,True);(bundle/'module.py').write_bytes(original)
 (bundle/'module.py').unlink();check('missing_source_blocks',g.verify_bundle,True);(bundle/'module.py').write_bytes(original)
 # Expected confinement: do not accept an external source through a symlink.
 external=base/'external-fixture.py';external.write_bytes(original);(bundle/'module.py').unlink();(bundle/'module.py').symlink_to(external);check('external_symlink_blocks',g.verify_bundle,True);(bundle/'module.py').unlink();(bundle/'module.py').write_bytes(original)
 check('fixture_claim_once',lambda:g.claim(g.ANCHOR,{'fixture_only':True}));check('fixture_duplicate_claim_blocks',lambda:g.claim(g.ANCHOR,{'fixture_only':True}),True)
print(json.dumps({'source_sha256':h(source),'scope':'Synthetic metadata and fixture-only O_EXCL marker; no real anchor, entrypoint, source execution, scientific package or data','passed':sum(c['pass'] for c in checks),'total':len(checks),'checks':checks},indent=2))
