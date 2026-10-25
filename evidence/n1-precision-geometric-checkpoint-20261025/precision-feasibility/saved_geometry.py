"""Exact rational algebra on saved float32 graph values; no model/torch/AD."""
from pathlib import Path
from fractions import Fraction as Q
import numpy as np,json,hashlib,sys
R=Path('PRECISION_FEASIBILITY');P=Path('PUBLIC_CHECKOUT');B=P/'evidence/g1-selected-gamma-20261024/result';N=Path('N1_EVIDENCE/attempt/raw');inputs={}
def read_product(name):
 p=B/name/'graph.npz';inputs[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 with np.load(p,allow_pickle=False) as z:
  frac=z['atom_frac_coord'];lat=z['lattice'];assert frac.dtype==lat.dtype==np.float32
  return [sum((Q(float(frac[i,k]))*Q(float(lat[k,j])) for k in range(3)),Q(0)) for i in range(20) for j in range(3)]
x0=read_product('R-CaTiO3__base');xp=read_product('R-CaTiO3__j50_h0.00375_s1');xm=read_product('R-CaTiO3__j50_h0.00375_s-1');h=Q(0.00375);e=[Q(int(i==50)) for i in range(60)];dp=[a-b-h*c for a,b,c in zip(xp,x0,e)];dm=[a-b+h*c for a,b,c in zip(xm,x0,e)];l1p=sum(map(abs,dp));l1m=sum(map(abs,dm));factor=(l1p+l1m)/(2*h)
with np.load(N/'native-pre-normalization.npz',allow_pickle=False) as z:actual=[Q(float(x)) for x in z['positions'].reshape(-1)]
with np.load(N/'native-row-50.npz',allow_pickle=False) as z:row=[Q(float(x)) for x in z['row']]
base_shift=[a-b for a,b in zip(x0,actual)];linear=sum((a*(b-c)/(2*h) for a,b,c in zip(row,dp,dm)),Q(0))
def exact(q):return {'numerator':str(q.numerator),'denominator':str(q.denominator),'float_display':float(q)}
result={'scope':'Exact products of saved float32 graph operands using rational arithmetic; not actual float32/float64 backend endpoint captures','h_binary64_value':exact(h),'endpoint_plus_delta_L1_A':exact(l1p),'endpoint_minus_delta_L1_A':exact(l1m),'geometric_multiplier_for_uniform_gradient_Linf':exact(factor),'endpoint_only_sufficient_Linf_forcegradient_for_0.005':exact(Q(0.005)/factor),'exact_product_baseline_minus_N1_actual_L1_A':exact(sum(map(abs,base_shift))),'local_row_projection_diagnostic_eV_A2':exact(linear),'projection_is_not_a_nonlinear_bound':True,'missing':['actual displaced Cartesian tensor captures','certified supremum force-gradient along endpoint perturbation segments','certified derivative-variation bound for baseline shift'],'input_hashes':inputs,'N1_input_hashes':{f:hashlib.sha256((N/f).read_bytes()).hexdigest() for f in ['native-pre-normalization.npz','native-row-50.npz']},'torch_imported':'torch' in sys.modules}
(R/'saved-geometry.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['input_hashes','N1_input_hashes']},indent=2))
