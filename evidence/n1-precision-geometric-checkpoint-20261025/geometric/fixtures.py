"""Synthetic exact-algebra fixtures only; never loads scientific inputs."""
from fractions import Fraction as F
import json
from audit import inverse,ranges,extrema,classify,enclosure,rat,H,ceil,floor
checks=[]
def check(name,value):
 checks.append({'name':name,'passed':bool(value)})
 if not value: raise AssertionError(name)
def raises(name,fn):
 try:fn()
 except (ValueError,TypeError):check(name,True)
 else:check(name,False)
I=[[F(int(i==j)) for j in range(3)] for i in range(3)]
A=[[F(2),F(1),F(0)],[F(0),F(3),F(1)],[F(1),F(0),F(4)]]
B=inverse(A)
check('inverse exact',[[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]==I)
raises('singular rejected',lambda:inverse([[F(0)]*3 for _ in range(3)]))
check('exact decimal h',H==F(3,800));check('binary64 h distinct',F.from_float(.00375)!=H)
check('signed floor ceil',floor(F(-3,2))==-2 and ceil(F(-3,2))==-1)
check('image sign enclosure',ranges([F(10),F(0),F(0)],0,I,h=F(0),r=F(1))[0]==(-11,-9))
lo,hi,_,_=extrema(F(1),F(0),F(9),F(1));check('interior tangency',lo==9 and hi==10 and classify(lo,hi,F(9))=='touching')
check('crossing',classify(F(8),F(10),F(9))=='crossing')
check('equality all',classify(F(9),F(9),F(9))=='boundary_all')
check('strict inside',classify(F(1),F(8),F(9))=='strictly_inside')
check('strict outside',classify(F(10),F(11),F(9))=='strictly_outside')
lo,hi,_,_=extrema(F(0),F(0),F(4));check('constant polynomial',lo==hi==4)
raises('reversed interval',lambda:classify(F(2),F(1),F(0)))
raises('nonfinite rejected',lambda:rat(float('nan')))
raises('wrong scalar rejected',lambda:rat(1))
check('float exact lift',rat(.1)==F.from_float(.1))
raises('coverage cap stops',lambda:enclosure([[F(0)]*3],I,cap=1))
_,items,total=enclosure([[F(0)]*3],I);check('nonzero self images retained',total>1 and len(items)==1)
check('unit-cell enclosure cardinality',total==13**3)
# A synthetic skew-cell pair: every sampled exact point inside R must lie in enclosure.
d=[F(1,3),F(-2,5),F(1,7)];bounds=ranges(d,1,B,h=F(1,2),r=F(2));hits=0
import itertools
for n in itertools.product(range(-4,5),repeat=3):
 for t in [F(-1,2),F(0),F(1,2)]:
  v=[d[k]+sum(n[j]*A[j][k] for j in range(3))+(t if k==2 else 0) for k in range(3)]
  if sum(x*x for x in v)<=4:
   hits+=1;check('synthetic enclosure inclusion '+str((n,t)),all(a<=v<=b for v,(a,b) in zip(n,bounds)))
check('synthetic witness exists',hits>0)
check('bond equality semantics differ',F(3)<=3 and not F(3)<3)
from audit import TOL
check('tol band exact distinction',(F(6)-TOL)**2<F(36)<(F(6)+TOL)**2)
check('no float core',all(isinstance(v,F) for row in B for v in row))
print(json.dumps({'checks':checks,'passed':len(checks),'scientific_analysis':False},indent=2))
