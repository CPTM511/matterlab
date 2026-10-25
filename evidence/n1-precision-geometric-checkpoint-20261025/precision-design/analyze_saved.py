"""Saved-array arithmetic only. No torch, model construction, forward or AD."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
P=Path('PUBLIC_CHECKOUT');B=P/'evidence/g1-selected-gamma-20261024/result';N=Path('N1_EVIDENCE/attempt/raw');O=Path(__file__).parent
hfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[];geometry=[];sources={}
def half_ulp(x):
 x=np.float32(x);return max(abs(float(np.nextafter(x,np.float32(np.inf)))-float(x)),abs(float(x)-float(np.nextafter(x,np.float32(-np.inf)))))/2
for h in ['0.015','0.0075','0.00375']:
 for k in [50,59]:
  points=[B/f'R-CaTiO3__j{k}_h{h}_s{s}' for s in [1,-1]]
  fs=[]
  for p in points:
   sources[str(p.relative_to(P)/'model-output.npz')]=hfile(p/'model-output.npz')
   with np.load(p/'model-output.npz',allow_pickle=False) as z:fs.append(z['f_0'].reshape(-1).copy())
  for j in [50,59]:
   with np.load(N/f'native-row-{j}.npz',allow_pickle=False) as z:a=float(z['row'][k])
   fd=-(float(fs[0][j])-float(fs[1][j]))/(2*float(h));bound=(half_ulp(fs[0][j])+half_ulp(fs[1][j]))/(2*float(h))+half_ulp(a)
   records.append({'j':j,'k':k,'h':float(h),'native':a,'FD':fd,'FD_minus_native':fd-a,'last_store_round_to_nearest_bound':bound,'residual_over_bound':abs(fd-a)/bound})
for p in [B/'R-CaTiO3__base']+[B/f'R-CaTiO3__j{k}_h{h}_s{s}' for k in [50,59] for h in ['0.015','0.0075','0.00375'] for s in [1,-1]]:
 with np.load(p/'graph.npz',allow_pickle=False) as g:
  pos=g['atom_frac_coord'].astype(np.float64)@g['lattice'].astype(np.float64);ag=g['atom_graph'];v=pos[ag[:,0]]-pos[ag[:,1]]-g['neighbor_image'].astype(np.float64)@g['lattice'].astype(np.float64);length=np.linalg.norm(v,axis=1);unit=v/length[:,None];bg=g['bond_graph'];cos=np.sum(unit[bg[:,2]]*unit[bg[:,4]],axis=1);gap=1-np.abs(cos)
 with np.load(p/'neighbors.npz',allow_pickle=False) as z:d=z['distance'].astype(np.float64)
 geometry.append({'point':p.name,'min_bond_length_A':float(length.min()),'min_abs_distance_to_3A':float(np.min(abs(d-3))),'min_abs_distance_to_6A':float(np.min(abs(d-6))),'angle_rows':len(gap),'one_minus_abs_cos_min':float(gap.min()),'near_collinear_gap_lt_1e6':int(np.sum(gap<1e-6)),'near_collinear_gap_lt_1e4':int(np.sum(gap<1e-4))})
ratios=[]
for j in [50,59]:
 for k in [50,59]:
  rows=sorted([v for v in records if v['j']==j and v['k']==k],key=lambda v:-v['h']);e=[v['FD_minus_native'] for v in rows];ratios.append({'j':j,'k':k,'coarse_error_ratio':e[0]/e[1],'fine_error_ratio':e[1]/e[2],'leading_smooth_h_squared_prediction':4.0,'fine_Richardson_residual':(4*rows[2]['FD']-rows[1]['FD'])/3-rows[2]['native']})
assert 'torch' not in sys.modules
result={'scope':'Saved output-rounding bound and source-guided float64 geometry proxies; not native intermediate captures, model inference or AD','rounding_assumption':'Hypothetical rounding only at final float32 force/AD storage, round-to-nearest; excludes all propagated arithmetic/input/feature errors','records':records,'h_squared_diagnostics':ratios,'geometry_proxies':geometry,'input_hashes':sources,'no_torch_import':True}
(O/'saved-diagnostics.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'min_residual_over_final_rounding_bound':min(v['residual_over_bound'] for v in records),'max_final_rounding_bound':max(v['last_store_round_to_nearest_bound'] for v in records),'ratios':ratios,'baseline_geometry':geometry[0]},indent=2))
