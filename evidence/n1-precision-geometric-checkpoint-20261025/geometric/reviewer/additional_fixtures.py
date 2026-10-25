import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,tempfile,itertools,datetime
from fractions import Fraction as F
import numpy as np
ROOT=Path('GEOMETRIC_AUDIT');sys.path.insert(0,str(ROOT));import audit as a
checks=[]
def ck(n,x):checks.append({'name':n,'passed':bool(x)})
def rejects(n,fn):
 try:fn();x=False
 except (ValueError,KeyError):x=True
 ck(n,x)
ck('touch_from_inside_preserved',a.classify(F(8),F(9),F(9))=='touching')
ck('touch_from_outside_preserved',a.classify(F(9),F(10),F(9))=='touching')
lo,hi,_,_=a.extrema(F(1),F(-1),F(9),F(1));ck('interior_vertex',lo==F(35,4) and hi==11)
I=[[F(int(i==j)) for j in range(3)] for i in range(3)];b=a.ranges([F(10),F(0),F(0)],0,I,h=F(0),r=F(1));actual=set(itertools.product(*(range(x,y+1) for x,y in b)));w=(-10,0,0);ck('missing_image_fixture_valid_witness',w in actual);actual.remove(w);ck('missing_image_detected_by_witness',w not in actual and sum((F(10 if k==0 else 0)+w[k])**2 for k in range(3))<=1)
with tempfile.TemporaryDirectory(dir=ROOT/'reviewer') as tmp:
 p=Path(tmp);f=p/'synthetic.npz';values={'positions':np.zeros((20,3),dtype=np.float64),'cell':np.eye(3,dtype=np.float64),'pbc':np.ones(3,dtype=bool),'atomic_numbers':np.ones(20,dtype=np.int64)};np.savez(f,**values);h=hashlib.sha256(f.read_bytes()).hexdigest();entry={'path':f.name,'sha256':h}
 z=a.load_inputs(p,[entry]*3);ck('synthetic_loader_exact_Fractions',all(isinstance(x,F) for row in z[0]['positions'] for x in row));rejects('changed_hash_rejected',lambda:a.load_inputs(p,[dict(entry,sha256='0'*64)]))
 values['positions']=np.zeros((20,3),dtype=np.float32);np.savez(f,**values);entry['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();rejects('wrong_dtype_rejected',lambda:a.load_inputs(p,[entry]))
 values['positions']=np.full((20,3),np.nan,dtype=np.float64);np.savez(f,**values);entry['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();rejects('nonfinite_input_rejected',lambda:a.load_inputs(p,[entry]))
ck('no_torch_import','torch' not in sys.modules)
v={'scope':'Synthetic fixtures only; audit.execute never called; no scientific inputs loaded or real pair audit','count':len(checks),'passed':all(c['passed'] for c in checks),'checks':checks,'audit_sha256':hashlib.sha256((ROOT/'audit.py').read_bytes()).hexdigest()};(ROOT/'reviewer/additional-fixtures.json').write_text(json.dumps(v,indent=2)+'\n');print({'count':len(checks),'passed':v['passed']})
