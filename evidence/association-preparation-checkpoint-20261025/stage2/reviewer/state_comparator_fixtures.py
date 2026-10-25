import sys,builtins,json,math,hashlib
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parent.parent;c=root/'candidate-v2';sys.path.insert(0,str(c))
original=builtins.__import__
def guarded(name,*a,**kw):
 if name.split('.')[0] in {'numpy','torch','ase','pymatgen','chgnet'}:raise RuntimeError('Forbidden scientific import')
 return original(name,*a,**kw)
builtins.__import__=guarded
import controller,comparator,native_capture
checks=[]
def test(n,f,reject=False):
 try:v=f()
 except Exception as e:checks.append({'name':n,'pass':reject,'exception':type(e).__name__});return
 checks.append({'name':n,'pass':not reject and v is not False})
def fresh():s=controller.Sequence();s.before('control',500);return s
def complete():
 s=fresh();s.after('control',1.,True);s.before('altered',400);s.after('altered',1.,True);return s
s=complete();test('control_then_altered',lambda:s.completed==['control','altered'] and s.seconds==2)
test('altered_first',lambda:controller.Sequence().before('altered',500),True)
test('before_without_previous_completion',lambda:fresh().before('altered',500),True)
test('after_without_launch',lambda:controller.Sequence().after('control',1.,True),True)
test('wrong_completion_condition',lambda:fresh().after('altered',1.,True),True)
test('third_launch',lambda:complete().before('control',300),True)
for v in [-1.,61.,float('nan'),float('inf'),True]:test('elapsed_reject_'+str(v),lambda v=v:fresh().after('control',v,True),True)
for v in [False,None,1,'yes']:test('ok_exact_true_'+str(v),lambda v=v:fresh().after('control',1.,v),True)
for v in [0.,-1.,float('nan'),float('inf'),True]:test('remaining_reject_'+str(v),lambda v=v:controller.Sequence().before('control',v),True)
s=fresh();test('failure_latches',lambda:s.after('control',1.,False),True);test('no_retry_after_failure',lambda:s.before('control',300),True)
s=controller.Sequence();test('remaining_bounds_timeout',lambda:s.before('control',2.5)==2.5)
test('exact_binary_decode',lambda:comparator.rational(1.25)==Q(5,4))
test('signed_differences',lambda:comparator.differences([1.25,-2.],[1.5,-3.])==[Q(1,4),Q(-1)])
for v in [True,None,'1',float('nan'),float('inf')]:test('scalar_reject_'+str(v),lambda v=v:comparator.rational(v),True)
test('empty_differences',lambda:comparator.differences([],[]),True);test('length_mismatch',lambda:comparator.differences([1],[1,2]),True)
for label,q in comparator.THRESHOLDS.items():
 test(label+'_strict_equality_not_positive',lambda q=q:not comparator.metric([q],q)['exceeds'])
 test(label+'_positive_over_threshold',lambda q=q:comparator.metric([q+Q(1,2**100)],q)['exceeds'])
 test(label+'_negative_over_threshold',lambda q=q:comparator.metric([-q-Q(1,2**100)],q)['exceeds'])
for kind in ['force','stress','added']:
 b=native_capture.Budget();b.claim(kind);test(kind+'_second_claim_blocks',lambda b=b,kind=kind:b.claim(kind),True);test(kind+'_failed_latch_blocks_any',lambda b=b:b.claim('force'),True)
for name,expected in [('energy',Q(1,100000)),('force',Q(1,1000000)),('stress',Q(1,10000000)),('curvature',Q(1,200))]:test('threshold_'+name,lambda name=name,expected=expected:comparator.THRESHOLDS[name]==expected)
result={'scope':'Pure synthetic state and rational values; no real saved arrays, controller main, child, launcher or scientific imports','source_hashes':{n:hashlib.sha256((c/n).read_bytes()).hexdigest() for n in ['controller.py','comparator.py','native_capture.py']},'passed':sum(x['pass'] for x in checks),'total':len(checks),'checks':checks}
print(json.dumps(result,indent=2))
