"""Independent scalar recomputation of saved differences; no numerical model is imported."""
import os,json,hashlib
from pathlib import Path
from decimal import Decimal
P=Path(os.environ['MATTERLAB_VALIDATION_OUTPUT']);R=Path(os.environ['MATTERLAB_ROOT'])
def flat(x):
    if isinstance(x,list):
        for y in x:yield from flat(y)
    else:yield x
protocol=json.loads((P/'protocol.json').read_text());new=json.loads((P/'R1/observations.json').read_text())
reported=json.loads((P/'comparisons.json').read_text())['comparisons'];checks=[]
for name,ref in protocol['references'].items():
    old=json.loads((R/ref['path']).read_text())
    for key,tol in protocol['original_acceptance'].items():
        a=list(flat(new[key]));b=list(flat(old[key]));saved=list(flat(reported[name][key]['signed_difference']))
        differences=[float(Decimal.from_float(float(x))-Decimal.from_float(float(y))) for x,y in zip(a,b,strict=True)]
        checks.append({'reference':name,'quantity':key,'components':len(a),'all_signed_components_verified':differences==saved,'maximum_verified':max(map(abs,differences))==reported[name][key]['max_abs_difference'],'acceptance_verified':all(abs(x)<=tol['atol'] for x in differences)==reported[name][key]['passed']})
result={'scope':'Separate standard-library Decimal/scalar implementation checks NumPy comparison arithmetic. Same task, not an independent human or separately attested model review. No inference or graph regeneration.','checks':checks,'passed':all(c['all_signed_components_verified'] and c['maximum_verified'] and c['acceptance_verified'] for c in checks),'scientific_review':['Capture success does not imply numerical replay acceptance.','The same restored numerical result under the new recorder does not identify the historical cause.','No missing D1 values were reconstructed.','Original thresholds and historical records remain unchanged.','Only one new evaluation was launched.','GitHub-backed resume is verified for this isolated invocation; migration and recurring future resume remain incomplete.']}
(P/'sanity-review.json').write_text(json.dumps(result,indent=2)+'\n')
assert result['passed']
print(json.dumps({'sanity_passed':True,'scalar_components_checked':sum(c['components'] for c in checks)}))
