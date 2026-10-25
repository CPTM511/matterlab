"""Synthetic format and exact-arithmetic checks; no real input files read."""
import io,struct,zipfile,json
from fractions import Fraction as Q
from audit import cell,value,parse,group
checks=[]
def check(name,v):
 if not v:raise AssertionError(name)
 checks.append(name)
def reject(name,fn):
 try:fn()
 except (ValueError,KeyError,SyntaxError,UnicodeError,zipfile.BadZipFile):checks.append(name);return
 raise AssertionError(name)
def blob(bits,descr='<f4',shape=(60,),extra=False,order=False,version=b'\x01\x00'):
 h=repr({'descr':descr,'fortran_order':order,'shape':shape}).encode('ascii')+b'\n'
 b=b'\x93NUMPY'+version+struct.pack('<H',len(h))+h+struct.pack('<'+'I'*len(bits),*bits)
 out=io.BytesIO()
 with zipfile.ZipFile(out,'w') as z:
  z.writestr('row.npy',b)
  if extra:z.writestr('extra',b'')
 return out.getvalue()
check('plus_zero',cell(0)==(Q(0),-Q(1,2**150),Q(1,2**150)))
check('minus_zero',cell(0x80000000)==cell(0))
check('min_subnormal',cell(1)==(Q(1,2**149),Q(1,2**150),Q(3,2**150)))
check('negative_subnormal',cell(0x80000001)==(-Q(1,2**149),-Q(3,2**150),-Q(1,2**150)))
check('one_asymmetric',cell(0x3f800000)==(Q(1),Q(1)-Q(1,2**25),Q(1)+Q(1,2**24)))
check('negative_one_asymmetric',cell(0xbf800000)==(-Q(1),-Q(1)-Q(1,2**24),-Q(1)+Q(1,2**25)))
check('normal_subnormal_boundary',cell(0x800000)[1]==Q(1,2**126)-Q(1,2**150))
check('adjacent_closed_ties',cell(0x3f800000)[2]==cell(0x3f800001)[1])
for b in [0x7f800000,0xff800000,0x7fc00000,0xffc00000,0x7f7fffff,0xff7fffff]:reject('unsupported_'+hex(b),lambda b=b:cell(b))
for b in [-1,2**32,True]:reject('invalid_bits_'+str(b),lambda b=b:value(b))
check('valid_row',parse(blob([0]*60))==[0]*60)
reject('wrong_dtype',lambda:parse(blob([0]*60,descr='<f8')))
reject('wrong_shape',lambda:parse(blob([0]*60,shape=(20,3))))
reject('float_shape',lambda:parse(blob([0]*60,shape=(60.0,))))
reject('wrong_order',lambda:parse(blob([0]*60,order=True)))
reject('extra_member',lambda:parse(blob([0]*60,extra=True)))
reject('short_payload',lambda:parse(blob([0]*59)))
reject('extra_payload',lambda:parse(blob([0]*61)))
reject('wrong_version',lambda:parse(blob([0]*60,version=b'\x02\x00')))
reject('incomplete_group',lambda:group([0]*19))
check('zero_identity',group([0]*20)['zero_in_closed_interval'])
check('balanced_identity',group([0x3f800000,0xbf800000]+[0]*18)['zero_in_closed_interval'])
check('positive_violation',not group([0x3f800000]*20)['zero_in_closed_interval'])
check('negative_violation',not group([0xbf800000]*20)['zero_in_closed_interval'])
check('bound_positive',group([0x3f800000]*20)['bound_exceeds_0.005'])
print(json.dumps({'passed':len(checks),'checks':checks},indent=2))
