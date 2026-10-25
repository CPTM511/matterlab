"""Synthetic-only checks; never reads saved scientific input."""
from force_cells import *
import json
checks=[]
def ok(n,x):
    checks.append({'name':n,'passed':bool(x)})
    if not x:raise AssertionError(n)
def rejects(n,fn):
    try:fn()
    except (ValueError,SyntaxError,UnicodeError):ok(n,True)
    else:ok(n,False)
q=Q
ok('positive_zero',cell(0)==(-q(1,1<<150),q(1,1<<150)))
ok('negative_zero_conservative',cell(0x80000000)==cell(0))
ok('min_subnormal',cell(1)==(q(1,1<<150),q(3,1<<150)))
ok('negative_subnormal',cell(0x80000001)==(-q(3,1<<150),-q(1,1<<150)))
ok('one_power_boundary',cell(0x3f800000)==(1-q(1,1<<25),1+q(1,1<<24)))
ok('two_power_boundary',cell(0x40000000)==(2-q(1,1<<24),2+q(1,1<<23)))
ok('smallest_normal',cell(0x00800000)==(q(1,1<<126)-q(1,1<<150),q(1,1<<126)+q(1,1<<150)))
for b in [1,2,0x7ffffe,0x7fffff,0x800000,0x3f7fffff,0x3f800000,0x3f800001,0x7f7ffffd]:
    ok('adjacent_closed_midpoint_'+str(b),cell(b)[1]==cell(b+1)[0]);ok('negative_symmetry_'+str(b),cell(b|0x80000000)==(-cell(b)[1],-cell(b)[0]))
for b in [0x7f800000,0xff800000,0x7fc00001,0xffc00000,0x7f7fffff,0xff7fffff,-1,1<<32]:rejects('unsupported_'+str(b),lambda b=b:cell(b))
def npy(h,raw=b'\0'*240):
    header=repr(h).encode()+b'\n';return b'\x93NUMPY\x01\x00'+len(header).to_bytes(2,'little')+header+raw
h={'descr':'<f4','fortran_order':False,'shape':(20,3)}
ok('parser_valid',parse_npy(npy(h))==b'\0'*240)
for k,v in [('descr','>f4'),('descr','<f8'),('fortran_order',True),('shape',(60,))]:rejects('header_'+k+str(v),lambda k=k,v=v:parse_npy(npy(dict(h,**{k:v}))))
rejects('trailing_payload',lambda:parse_npy(npy(h,b'\0'*241)))
rejects('short_payload',lambda:parse_npy(npy(h,b'\0'*239)))
rejects('version',lambda:parse_npy(b'\x93NUMPY\x02\x00'+b'\0'*300))
rejects('archive_hash_mismatch',lambda:payload(b'bad',{'npz_sha256':'0'*64}))
z=analyze(b'\0'*240);ok('synthetic_zero_inconclusive',all(not s['zero_excluded'] for s in z['sums']))
a=analyze(struct.pack('<60I',*([0x3f800000]*60)));ok('synthetic_ones_exclusion',all(s['zero_excluded'] for s in a['sums']))
bits=[0x3f800000]*30+[0xbf800000]*30;ok('synthetic_balanced',all(not s['zero_excluded'] for s in analyze(struct.pack('<60I',*bits))['sums']))
rejects('analysis_nonfinite',lambda:analyze(struct.pack('<60I',*([0x7f800000]+[0]*59))))
print(json.dumps({'scope':'synthetic only; no real data read','checks':checks,'passed':True,'count':len(checks)},indent=2))
