"""Future saved-array arithmetic only; rows j compared to FD column k at row j."""
import json
from pathlib import Path
def compare(root,out):
 import numpy as np
 base=root/'evidence/g1-selected-gamma-20261024/result';rows={j:np.load(out/f'native-row-{j}.npz',allow_pickle=False)['row'] for j in (50,59)};records=[]
 for h in ('0.015','0.0075','0.00375'):
  for k in (50,59):
   plus=json.loads((base/f'R-CaTiO3__j{k}_h{h}_s1/observations.json').read_text())
   minus=json.loads((base/f'R-CaTiO3__j{k}_h{h}_s-1/observations.json').read_text())
   column=-(np.asarray(plus['forces_eV_A'],dtype=np.float64).reshape(-1)-np.asarray(minus['forces_eV_A'],dtype=np.float64).reshape(-1))/(2*float(h))
   for j in (50,59):
    delta=float(rows[j][k])-float(column[j]);records.append({'row_j':j,'column_k':k,'h_A':float(h),'native_eV_A2':float(rows[j][k]),'finite_difference_eV_A2':float(column[j]),'native_minus_FD_eV_A2':delta,'within_0.005':abs(delta)<=0.005})
 reciprocity=float(rows[50][59])-float(rows[59][50]);result={'entries':records,'native_reciprocity_eV_A2':reciprocity,'reciprocity_within_0.005':abs(reciprocity)<=0.005,'original_replay_acceptance':'failed unchanged','G1_quality':'failed unchanged','execution_acceptance':'pending independent process and saved-evidence review'}
 (out/'signed-comparisons.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
