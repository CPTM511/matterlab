"""Exact saved binary32 translation-row audit. Standard library only."""
import ast, hashlib, io, json, struct, sys, zipfile
from fractions import Fraction as Q
from pathlib import Path
INPUTS={50:('native-row-50.npz','9f266858e0d1c5c1164241a8425099ebec0c9c8305f7ea5803cb0f9c4369e328'),59:('native-row-59.npz','fe30ec0c926385cd412cdd39bb5e316e5445398046c68e342de842b1c910854f')}

def value(bits):
 if type(bits) is not int or not 0<=bits<2**32: raise ValueError('Invalid binary32 bits')
 sign=-1 if bits>>31 else 1; exponent=(bits>>23)&255; fraction=bits&0x7fffff
 if exponent==255: raise ValueError('Nonfinite binary32')
 mantissa=fraction if exponent==0 else (1<<23)+fraction
 power=-149 if exponent==0 else exponent-150
 return sign*Q(mantissa)*(Q(2)**power)

def cell(bits):
 x=value(bits)
 if (bits&0x7fffffff)==0:
  # Closed union of either signed-zero rounding cell is conservative.
  half=Q(1,2**150); return x,-half,half
 if (bits&0x7fffffff)==0x7f7fffff: raise ValueError('Extreme finite endpoint unsupported')
 prev=bits+1 if bits>>31 else bits-1
 nxt=bits-1 if bits>>31 else bits+1
 lo=(value(prev)+x)/2;hi=(x+value(nxt))/2
 if not lo<x<hi: raise ValueError('Nonmonotone cell')
 return x,lo,hi

def parse(blob):
 with zipfile.ZipFile(io.BytesIO(blob)) as z:
  if z.namelist()!=['row.npy']: raise ValueError('Unexpected NPZ members')
  info=z.getinfo('row.npy')
  if info.file_size>4096: raise ValueError('Oversize NPY')
  b=z.read('row.npy')
 if b[:8]!=b'\x93NUMPY\x01\x00' or len(b)<10: raise ValueError('Unsupported NPY version')
 length=struct.unpack('<H',b[8:10])[0]
 if not 0<length<=2048 or 10+length>len(b): raise ValueError('Bad NPY header length')
 header=ast.literal_eval(b[10:10+length].decode('ascii').strip())
 if type(header) is not dict or set(header)!={'descr','fortran_order','shape'}: raise ValueError('Invalid NPY header')
 if header['descr']!='<f4' or header['fortran_order'] is not False or type(header['shape']) is not tuple or len(header['shape'])!=1 or type(header['shape'][0]) is not int or header['shape'][0]!=60: raise ValueError('Unsupported dtype/order/shape')
 payload=b[10+length:]
 if len(payload)!=240: raise ValueError('Incomplete or excess row data')
 return list(struct.unpack('<60I',payload))

def rat(x): return {'numerator':x.numerator,'denominator':x.denominator}

def group(bits):
 if len(bits)!=20: raise ValueError('Wrong group size')
 cells=[cell(b) for b in bits]
 s=sum((c[0] for c in cells),Q(0));lo=sum((c[1] for c in cells),Q(0));hi=sum((c[2] for c in cells),Q(0))
 d=max(lo,-hi,Q(0))
 return {'signed_sum':rat(s),'sum_interval_lower':rat(lo),'sum_interval_upper':rat(hi),'zero_in_closed_interval':lo<=0<=hi,'distance_to_zero':rat(d),'conditional_component_distance_lower_bound':rat(d/20),'bound_exceeds_0.005':d/20>Q(1,200)}

def main(source,out):
 out=Path(out);out.mkdir(exist_ok=False)
 rows={};identities={}
 for j,(name,expected) in INPUTS.items():
  b=(Path(source)/name).read_bytes();h=hashlib.sha256(b).hexdigest()
  if h!=expected: raise ValueError('Pinned input mismatch')
  bits=parse(b)
  for v in bits:cell(v)
  rows[j]=bits;identities[str(j)]={'file':name,'bytes':len(b),'sha256':h,'dtype':'<f4','shape':[60]}
 (out/'input-identities.json').write_text(json.dumps(identities,indent=2)+'\n')
 records=[]
 with (out/'classifications.jsonl').open('x') as f:
  for j in (50,59):
   for alpha in range(3):
    bits=rows[j][alpha::3]
    record={'row_j':j,'axis':('x','y','z')[alpha],'components':20,'bits_hex':[f'{b:08x}' for b in bits],'cells':[{'value':rat(x),'lower':rat(lo),'upper':rat(hi)} for x,lo,hi in map(cell,bits)],**group(bits)}
    f.write(json.dumps(record,sort_keys=True)+'\n');f.flush();records.append(record)
 result={'components':120,'groups':6,'excluded_groups':sum(not r['zero_in_closed_interval'] for r in records),'any_bound_exceeds_0.005':any(r['bound_exceeds_0.005'] for r in records),'units':'eV/Angstrom^2','interpretation':'Exclusion rejects final-correct-rounding plus smooth translation-invariant exact-row premises jointly; inclusion inconclusive. No cause attribution or acceptance change.'}
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result))
if __name__=='__main__':main(*sys.argv[1:])
