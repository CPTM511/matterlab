"""Exact binary32 cells. Standard library only; no real fixture access on import."""
import ast, hashlib, io, struct, zipfile
from fractions import Fraction as Q

def positive(m):
    if not 0 <= m < 0x7f800000: raise ValueError('nonfinite magnitude')
    e=m>>23; f=m&0x7fffff
    return Q(f,1<<149) if e==0 else Q((1<<23)+f)*Q(2)**(e-150)

def cell(bits):
    if type(bits) is not int or not 0<=bits<=0xffffffff: raise ValueError('invalid word')
    m=bits&0x7fffffff
    if m>=0x7f800000: raise ValueError('nonfinite')
    if m==0x7f7fffff: raise ValueError('maximum finite endpoint unsupported')
    if m==0: return -Q(1,1<<150), Q(1,1<<150)
    lo=(positive(m-1)+positive(m))/2;hi=(positive(m)+positive(m+1))/2
    return (-hi,-lo) if bits>>31 else (lo,hi)

def parse_npy(data):
    if data[:8]!=b'\x93NUMPY\x01\x00' or len(data)<10: raise ValueError('unsupported NPY version/magic')
    n=int.from_bytes(data[8:10],'little')
    if not 0<n<=4096 or 10+n>len(data): raise ValueError('header length')
    h=ast.literal_eval(data[10:10+n].decode('ascii'))
    if type(h) is not dict or set(h)!={'descr','fortran_order','shape'}: raise ValueError('header keys')
    if h['descr']!='<f4' or h['fortran_order'] is not False or type(h['shape']) is not tuple or any(type(v) is not int for v in h['shape']) or h['shape']!=(20,3): raise ValueError('representation')
    raw=data[10+n:]
    if len(raw)!=240: raise ValueError('payload length')
    return raw

def payload(archive,ids):
    if hashlib.sha256(archive).hexdigest()!=ids['npz_sha256']: raise ValueError('archive hash')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        names=z.namelist()
        if len(names)!=6 or set(names)!=set(ids['members']): raise ValueError('archive coverage')
        if any(i.file_size>1048576 or i.flag_bits&1 for i in z.infolist()): raise ValueError('archive bounds/encryption')
        b=z.read('f_0.npy')
    if hashlib.sha256(b).hexdigest()!=ids['member_sha256']: raise ValueError('member hash')
    raw=parse_npy(b)
    if hashlib.sha256(raw).hexdigest()!=ids['payload_sha256']: raise ValueError('payload hash')
    return raw

def rational(v):return {'numerator':v.numerator,'denominator':v.denominator}
def analyze(raw):
    if len(raw)!=240:raise ValueError('component cap')
    bits=struct.unpack('<60I',raw)
    if any((b&0x7fffffff)>=0x7f7fffff for b in bits): raise ValueError('nonfinite/unsupported endpoint')
    cells=[cell(b) for b in bits]
    rows=[]
    for a in range(3):
        lo=sum((cells[i][0] for i in range(a,60,3)),Q(0));hi=sum((cells[i][1] for i in range(a,60,3)),Q(0))
        excluded=lo>0 or hi<0;d=lo if lo>0 else -hi if hi<0 else Q(0)
        rows.append({'axis':'xyz'[a],'lower_eV_A':rational(lo),'upper_eV_A':rational(hi),'zero_excluded':excluded,'distance_to_zero_eV_A':rational(d),'conditional_some_component_distance_from_cell_lower_bound_eV_A':rational(d/20) if excluded else None,'interpretation':'incompatible_with_joint_premise' if excluded else 'inconclusive'})
    return {'schema':1,'components':60,'axis_sums':3,'units':'eV/Angstrom','cells':[{'atom':i//3,'axis':'xyz'[i%3],'bits_hex':f'{b:08x}','lower':rational(cells[i][0]),'upper':rational(cells[i][1])} for i,b in enumerate(bits)],'sums':rows,'criterion':'exact zero exclusion from closed conservative rounding-cell sums','ties':'both midpoint endpoints included; signed zeros use common symmetric conservative cell','not_replay_acceptance':True}
