"""Exact saved-geometry audit; never imports a model or invokes a neighbor backend."""
from fractions import Fraction as F
from pathlib import Path
import datetime, hashlib, itertools, json, math, sys, time
H=F(3,800)
TOL=F(1,100000000)
R=F(6)+TOL
CAP=100000

def inverse(a):
    if len(a)!=3 or any(len(x)!=3 for x in a): raise ValueError('cell shape')
    m=[list(row)+[F(int(i==j)) for j in range(3)] for i,row in enumerate(a)]
    for k in range(3):
        pivot=next((i for i in range(k,3) if m[i][k]),None)
        if pivot is None: raise ValueError('singular cell')
        m[k],m[pivot]=m[pivot],m[k]
        d=m[k][k];m[k]=[v/d for v in m[k]]
        for i in range(3):
            if i!=k:
                d=m[i][k];m[i]=[x-d*y for x,y in zip(m[i],m[k])]
    return [row[3:] for row in m]

def floor(x): return x.numerator//x.denominator

def ceil(x): return -floor(-x)

def ranges(d,sign,inv,h=H,r=R):
    out=[]
    for k in range(3):
        q=sum(d[j]*inv[j][k] for j in range(3));w=abs(sign*inv[2][k])*h
        budget=r*sum(abs(inv[j][k]) for j in range(3))
        out.append((ceil(-q-w-budget),floor(-q+w+budget)))
    return out

def extrema(a,b,c,h=H):
    pts=[-h,h]
    if a:
        v=-b/(2*a)
        if -h<=v<=h: pts.append(v)
    vals=[(a*t*t+b*t+c,t) for t in pts]
    lo=min(v for v,t in vals);hi=max(v for v,t in vals)
    return lo,hi,[t for v,t in vals if v==lo],[t for v,t in vals if v==hi]

def classify(lo,hi,t):
    if lo>hi: raise ValueError('reversed interval')
    if hi<t: return 'strictly_inside'
    if lo>t: return 'strictly_outside'
    if lo==hi==t: return 'boundary_all'
    if lo<t<hi: return 'crossing'
    return 'touching'

def rat(x):
    # Conversion preserves the exact stored IEEE value; no floating arithmetic.
    v=x.item() if hasattr(x,'item') else x
    if not isinstance(v,float) or not math.isfinite(v): raise ValueError('nonfinite or wrong float type')
    return F(*v.as_integer_ratio())

def load_inputs(base,entries):
    import numpy as np
    loaded=[]
    for entry in entries:
        p=base/entry['path'];raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=entry['sha256']: raise ValueError('input hash mismatch')
        with np.load(p,allow_pickle=False) as z:
            if z['positions'].shape!=(20,3) or z['positions'].dtype!=np.dtype('float64'): raise ValueError('positions schema')
            if z['cell'].shape!=(3,3) or z['cell'].dtype!=np.dtype('float64'): raise ValueError('cell schema')
            if z['pbc'].tolist()!=[True,True,True]: raise ValueError('nonperiodic cell')
            loaded.append({'positions':[[rat(x) for x in row] for row in z['positions']], 'cell':[[rat(x) for x in row] for row in z['cell']], 'species':z['atomic_numbers'].tolist()})
    if any(d['cell']!=loaded[0]['cell'] or d['species']!=loaded[0]['species'] for d in loaded[1:]): raise ValueError('endpoint invariant mismatch')
    return loaded

def enclosure(pos,cell,cap=CAP):
    inv=inverse(cell);items=[];count=0
    for i in range(len(pos)):
        for j in range(len(pos)):
            d=[pos[i][k]-pos[j][k] for k in range(3)];sign=int(i==16)-int(j==16)
            bounds=ranges(d,sign,inv);n=math.prod(max(0,b-a+1) for a,b in bounds)
            count+=n
            if count>cap: raise ValueError('pair/image record cap exceeded before enumeration')
            items.append((i,j,d,sign,bounds))
    return inv,items,count

def write_json(p,obj): p.write_text(json.dumps(obj,indent=2,default=str)+'\n')

def execute(protocol_path,out):
    protocol=json.loads(protocol_path.read_text());out.mkdir(exist_ok=False)
    begin=time.monotonic();deadline=datetime.datetime.fromisoformat(protocol['stage_deadline_utc'])
    def guard():
        if time.monotonic()-begin>=55: raise TimeoutError('55 second internal analysis stop')
        if datetime.datetime.now(datetime.timezone.utc)>=deadline: raise TimeoutError('all-role deadline')
    count=0
    try:
        guard();data=load_inputs(Path(protocol['public_checkout']),protocol['inputs']);p=data[0]['positions'];cell=data[0]['cell']
        inv,items,total=enclosure(p,cell)
        write_json(out/'enclosure.json',{'inverse':inv,'total_records_including_zero_self':total,'pair_bounds':[{'i':i,'j':j,'bounds':b} for i,j,d,s,b in items], 'image_convention':'ri-rj+nL; not pymatgen signed image identity','proof':'If ||d(t)+nL||2<=R then |((d(t)+nL)L^-1)_k|<=R*||inverse_column_k||2<=R*L1norm(inverse_column_k). Exact ceil/floor bounds include every possible integer image.'})
        offsets=[]
        for endpoint,sign in zip(data[1:],[1,-1]):
            offsets.append([[endpoint['positions'][i][k]-(p[i][k]+(sign*H if i==16 and k==2 else 0)) for k in range(3)] for i in range(20)])
        write_json(out/'endpoint-offsets.json',{'interpretation':'saved endpoint minus exact nominal endpoint, Angstrom; not a force-error bound','h':H,'offsets_plus_minus':offsets})
        thresholds={'bond3':F(9),'atom6':F(36),'atom6_minus_documented_tol':(F(6)-TOL)**2,'atom6_plus_documented_tol':R**2,'self_distance_tol':TOL**2}
        summary={k:{} for k in thresholds};excluded=0
        with (out/'classifications.jsonl').open('x') as f:
            for i,j,d,sign,bounds in items:
                for n in itertools.product(*(range(a,b+1) for a,b in bounds)):
                    guard();count+=1
                    if i==j and n==(0,0,0):
                        excluded+=1;f.write(json.dumps({'i':i,'j':j,'image':n,'excluded':'true_zero_self_pair'})+'\n');continue
                    v=[d[k]+sum(n[z]*cell[z][k] for z in range(3)) for k in range(3)]
                    a=F(sign*sign);b=2*sign*v[2];c=sum(x*x for x in v);lo,hi,arglo,arghi=extrema(a,b,c)
                    classes={k:classify(lo,hi,t) for k,t in thresholds.items()}
                    for k,value in classes.items():summary[k][value]=summary[k].get(value,0)+1
                    f.write(json.dumps({'i':i,'j':j,'image':n,'self_image':i==j,'quadratic':[a,b,c],'min_d2':lo,'max_d2':hi,'argmin':arglo,'argmax':arghi,'margins_d2':{k:[lo-t,hi-t] for k,t in thresholds.items()},'classification':classes},default=str)+'\n')
        if count!=total: raise ValueError('coverage count mismatch')
        guard();result={'status':'completed_geometric_only','records':count,'excluded_zero_self':excluded,'classified_records':count-excluded,'class_counts':summary,'seconds':time.monotonic()-begin,'native_backend_certified':False,'model_forward_AD':0}
        write_json(out/'result.json',result);return result
    except BaseException as e:
        write_json(out/'failure.json',{'exception':type(e).__name__,'message':str(e),'records_written':count,'seconds':time.monotonic()-begin});raise

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('audit.py PROTOCOL OUTPUT')
    print(json.dumps(execute(Path(sys.argv[1]),Path(sys.argv[2]))))
