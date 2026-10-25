"""Exact rational differences of decoded values. No array import until future loading."""
from fractions import Fraction
import math,json
from pathlib import Path
THRESHOLDS={'energy':Fraction(1,100000),'force':Fraction(1,1000000),'stress':Fraction(1,10000000),'curvature':Fraction(1,200)}
def rational(x):
 if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):raise ValueError('Unsupported/nonfinite scalar')
 return Fraction(x)
def differences(control,altered):
 if len(control)!=len(altered) or not control:raise ValueError('Missing/mismatched values')
 return [rational(b)-rational(a) for a,b in zip(control,altered)]
def encode(x):return {'numerator':x.numerator,'denominator':x.denominator}
def metric(values,threshold):return {'signed_differences':[encode(x) for x in values],'maximum_absolute':encode(max(map(abs,values))),'threshold':encode(threshold),'exceeds':max(map(abs,values))>threshold}
def main(root):
 import numpy as np
 root=Path(root);c=root/'control';a=root/'altered'
 def read(p):return json.loads(p.read_text())
 for d,label in [(c,'control'),(a,'altered')]:
  if read(d/'point-complete.json')!={'passed':True,'condition':label}:raise ValueError('Point incomplete')
 C=read(c/'observations.json');A=read(a/'observations.json')
 flat=lambda x:[v for row in x for v in row]
 result={'energy':metric(differences([C['energy_eV']],[A['energy_eV']]),THRESHOLDS['energy']),'force':metric(differences(flat(C['forces_eV_A']),flat(A['forces_eV_A'])),THRESHOLDS['force']),'stress':metric(differences(flat(C['stress_eV_A3']),flat(A['stress_eV_A3'])),THRESHOLDS['stress'])}
 with np.load(c/'native-row-50.npz',allow_pickle=False) as x,np.load(a/'native-row-50.npz',allow_pickle=False) as y:
  if x['row'].shape!=(60,) or y['row'].shape!=(60,) or x['row'].dtype!=y['row'].dtype:raise ValueError('Row shape/dtype')
  row=differences(x['row'].tolist(),y['row'].tolist());result['row50']=[encode(d) for d in row];result['primary_A50_50']=metric([row[50]],THRESHOLDS['curvature'])
 result['model_tensor_differences']={}
 with np.load(c/'model-output.npz',allow_pickle=False) as x,np.load(a/'model-output.npz',allow_pickle=False) as y:
  if set(x.files)!=set(y.files):raise ValueError('Tensor keys')
  for k in x.files:
   if x[k].shape!=y[k].shape or x[k].dtype!=y[k].dtype:raise ValueError('Tensor shape/dtype')
   result['model_tensor_differences'][k]=[encode(d) for d in differences(x[k].reshape(-1).tolist(),y[k].reshape(-1).tolist())]
 result['interpretation']='Unreplicated same-point association sensitivity only; terminal independent review pending. No historical-cause, accuracy or migration acceptance.'
 (root/'signed-comparisons.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 return result
