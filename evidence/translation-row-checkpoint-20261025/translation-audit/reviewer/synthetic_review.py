import sys,importlib.util,hashlib,json,io,struct,zipfile,tempfile,contextlib
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('reviewed_audit',ROOT/'audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
checks=[]
def check(n,c):checks.append({'name':n,'pass':bool(c)})
def reject(n,f):
 try:f()
 except Exception as e:checks.append({'name':n,'pass':True,'exception_type':type(e).__name__})
 else:check(n,False)
def blob(bits,shape=(60,),descr='<f4',order=False):
 h=repr({'descr':descr,'fortran_order':order,'shape':shape}).encode()+b'\n'
 b=b'\x93NUMPY\x01\x00'+struct.pack('<H',len(h))+h+struct.pack('<'+'I'*len(bits),*bits)
 s=io.BytesIO()
 with zipfile.ZipFile(s,'w') as z:z.writestr('row.npy',b)
 return s.getvalue()
# Analytic values, including negative numeric ordering and unequal spacing.
for bits,expected in [(0x40000000,(Q(2),Q(2)-Q(1,2**24),Q(2)+Q(1,2**23))),(0xc0000000,(-Q(2),-Q(2)-Q(1,2**23),-Q(2)+Q(1,2**24))),(0x00800000,(Q(1,2**126),Q(1,2**126)-Q(1,2**150),Q(1,2**126)+Q(1,2**150))),(0x80800000,(-Q(1,2**126),-Q(1,2**126)-Q(1,2**150),-Q(1,2**126)+Q(1,2**150)))]:check('exact_cell_'+hex(bits),a.cell(bits)==expected)
for b in [0,1,2,0x007fffff,0x00800000,0x3f7fffff,0x3f800000,0x3f800001,0x40000000,0x7f7ffffe]:
 x,lo,hi=a.cell(b);nx,nlo,nhi=a.cell(b|0x80000000);check('reflection_'+hex(b),(nx,nlo,nhi)==(-x,-hi,-lo))
reject('float_shape_rejected',lambda:a.parse(blob([0]*60,shape=(60.0,))))
reject('integer_fortran_rejected',lambda:a.parse(blob([0]*60,order=0)))
reject('big_endian_rejected',lambda:a.parse(blob([0]*60,descr='>f4')))
reject('object_dtype_rejected',lambda:a.parse(blob([0]*60,descr='|O')))
reject('nonzip_rejected',lambda:a.parse(b'not a zip'))
reject('oversized_member_rejected',lambda:a.parse(blob([0]*1100)))
check('closed_cell_zero_inclusion',a.group([1,0x80000001]+[0]*18)['zero_in_closed_interval'])
g=a.group([0x3f800000]*20);un=lambda v:Q(v['numerator'],v['denominator'])
check('positive_distance',un(g['distance_to_zero'])==20*(Q(1)-Q(1,2**25)))
check('positive_d_over20',un(g['conditional_component_distance_lower_bound'])==Q(1)-Q(1,2**25))
check('negative_distance',un(a.group([0xbf800000]*20)['distance_to_zero'])==un(g['distance_to_zero']))
# Only constructed fixture inputs, inside reviewer directory.
with tempfile.TemporaryDirectory(prefix='synthetic-',dir=ROOT/'reviewer') as td:
 t=Path(td);src=t/'source';src.mkdir();(src/'native-row-50.npz').write_bytes(blob([0]*60))
 reject('pinned_hash_rejected_before_parse',lambda:a.main(src,t/'bad-hash-out'))
 old=a.INPUTS
 try:
  bp=blob([0x3f800000,0,0xbf800000]*20);bm=blob([0,0,0]*20)
  (src/'native-row-50.npz').write_bytes(bp);(src/'native-row-59.npz').write_bytes(bm)
  a.INPUTS={50:('native-row-50.npz',hashlib.sha256(bp).hexdigest()),59:('native-row-59.npz',hashlib.sha256(bm).hexdigest())}
  with contextlib.redirect_stdout(io.StringIO()):a.main(src,t/'synthetic-out')
  records=[json.loads(x) for x in (t/'synthetic-out/classifications.jsonl').read_text().splitlines()]
  check('all_six_fixed_groups',[(x['row_j'],x['axis']) for x in records]==[(50,'x'),(50,'y'),(50,'z'),(59,'x'),(59,'y'),(59,'z')])
  check('axis_slices_and_signed_sums',[un(x['signed_sum']) for x in records]==[20,0,-20,0,0,0])
  check('exact120_components',sum(x['components'] for x in records)==120)
  check('two_synthetic_exclusions',json.loads((t/'synthetic-out/result.json').read_text())['excluded_groups']==2)
 finally:a.INPUTS=old
result={'audit_sha256':hashlib.sha256((ROOT/'audit.py').read_bytes()).hexdigest(),'real_inputs_read':False,'checks':checks,'passed':sum(x['pass'] for x in checks),'total':len(checks)}
print(json.dumps(result,indent=2))
