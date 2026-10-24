"""Saved-data arithmetic only. No model imports or calls."""
import json,hashlib
from pathlib import Path
import numpy as np

def load(p): return json.loads(Path(p).read_text())
def save(p,x): Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arrays(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
def canonical(n):
 return sorted(tuple(row) for row in np.column_stack([n['center'],n['neighbor'],n['image']]).tolist())
def analyze(root,out,bundle):
 points=load(bundle/'points.json'); data={}; signed={}; summary={}
 for p in points:
  d=out/p['id']; m=load(d/'manifest.json')['files']
  assert set(m)=={str(f.relative_to(d)) for f in d.rglob('*') if f.is_file() and f.name!='manifest.json'}
  assert all(sha(d/n)==h for n,h in m.items())
  c=load(d/'capture-summary.json');assert c['graph_calls']==c['model_calls']==1
  a=arrays(d/'model-output.npz');g=arrays(d/'graph.npz');n=arrays(d/'neighbors.npz');inp=arrays(d/'input-arrays.npz');obs=load(d/'observations.json')
  assert np.array_equal(inp['positions'],np.array(p['positions']))
  assert np.array_equal(g['atom_frac_coord'],inp['frac_coords'].astype(np.float32))
  assert np.array_equal(g['lattice'],inp['lattice'].astype(np.float32))
  assert np.array_equal(g['atom_graph'],np.column_stack([n['center'],n['neighbor']]).astype(np.int32))
  assert np.array_equal(g['neighbor_image'],n['image'].astype(np.float32))
  assert np.array_equal(g['atomic_number'],inp['atomic_numbers'].astype(np.int32))
  assert all(np.isfinite(v).all() and v.size for v in [*a.values(),*g.values(),*n.values(),*inp.values()])
  data[p['id']]={'p':p,'a':a,'g':g,'n':n,'F':np.array(obs['forces_eV_A']).reshape(-1),'E':obs['energy_eV'],'S':np.array(obs['stress_eV_A3'])}
 for material in ['R-CaTiO3','C03-005']:
  rows=[d for d in data.values() if d['p']['material']==material];base=next(d for d in rows if d['p']['kind']=='baseline'); topology=[];columns={};rounding={}
  for d in rows:
   p=d['p'];stable=all(d['g'][k].dtype==base['g'][k].dtype and np.array_equal(d['g'][k],base['g'][k]) for k in ['atomic_number','atom_graph','neighbor_image','directed2undirected','undirected2directed','bond_graph','lattice'])
   topology.append({'id':p['id'],'ordered_graph_topology_equal_baseline':stable,'canonical_neighbor_multiset_equal':canonical(d['n'])==canonical(base['n'])})
  for h in [.015,.0075,.00375]:
   for j in [50,59]:
    pair=[next(d for d in rows if d['p']['kind']=='coordinate' and d['p']['coordinate']==j and d['p']['h_A']==h and d['p']['sign']==s and 'repeat_of' not in d['p']) for s in [1,-1]]
    fp,fm=pair;key=f'{h}:{j}';columns[key]=-(fp['F']-fm['F'])/(2*h)
    rounding[key]=(np.abs(np.spacing(fp['a']['f_0']))+np.abs(np.spacing(fm['a']['f_0']))).astype(float).reshape(-1)/(2*h)
  rep=next(d for d in rows if 'repeat_of' in d['p']);orig=data[rep['p']['repeat_of']]
  exact=all(rep['a'][k].dtype==orig['a'][k].dtype and rep['a'][k].shape==orig['a'][k].shape and rep['a'][k].tobytes()==orig['a'][k].tobytes() for k in orig['a'])
  assert exact,'Same-point tensor repeat differs; stop, no further evaluations'
  repeats={k:(rep['a'][k].astype(float)-orig['a'][k].astype(float)).tolist() for k in orig['a']}
  trans={str(d['p']['sign']):{'forces_eV_A':(d['F']-base['F']).tolist(),'energy_eV':d['E']-base['E'],'stress_eV_A3':(d['S']-base['S']).tolist()} for d in rows if d['p']['kind']=='translation'}
  asym={str(h):float(columns[f'{h}:59'][50]-columns[f'{h}:50'][59]) for h in [.015,.0075,.00375]}
  steps={f'{h}:{j}':(columns[f'{h}:'+str(j)]-columns[f'{h/2}:'+str(j)]).tolist() for h in [.015,.0075] for j in [50,59]}
  maxfine=max(np.max(np.abs(steps[f'0.0075:{j}'])) for j in [50,59]);maxcoarse=max(np.max(np.abs(steps[f'0.015:{j}'])) for j in [50,59]);stable=all(t['ordered_graph_topology_equal_baseline'] for t in topology)
  transok=all(max(abs(x) for x in t['forces_eV_A'])<=1e-6 and abs(t['energy_eV'])<=1e-5 and np.max(np.abs(t['stress_eV_A3']))<=1e-7 for t in trans.values())
  summary[material]={'graph_stable_all_sampled_points':stable,'pair_asymmetry_eV_A2':asym,'max_fine_step_column_difference_eV_A2':float(maxfine),'max_coarse_step_column_difference_eV_A2':float(maxcoarse),'coarse_to_fine_ratio':float(maxcoarse/maxfine) if maxfine else None,'ratio_interpretation':'Undefined when denominator zero; diagnostic pattern only, not causal proof','selected_local_quality_criteria_met':bool(stable and transok and maxfine<=.005 and max(abs(x) for x in asym.values())<=.005),'native_translation_criteria_met':transok,'repeat_exact':exact,'outcome':'graph_or_order_change_precludes_smooth_sampled_derivative_claim' if not stable else 'sampled_quality_criteria_met' if transok and maxfine<=.005 and max(abs(x) for x in asym.values())<=.005 else 'sampled_numerical_uncertainty_remains'}
  signed[material]={'columns_eV_A2':{k:v.tolist() for k,v in columns.items()},'pair_asymmetry_eV_A2':asym,'step_column_signed_differences_eV_A2':steps,'repeat_tensor_signed_differences':repeats,'translation_signed_differences':trans,'graph_comparisons':topology,'float32_output_ulp_proxy_eV_A2':{k:v.tolist() for k,v in rounding.items()},'ulp_proxy_caveat':'Representation scale only; not a bound on algorithmic error or internal cancellation.'}
  if material=='C03-005':
   signed[material]['historical_column_signed_differences_eV_A2']={}
   for h,suffix in [(.015,''),(.0075,'_half_step')]:
    z=arrays(root/f'runs/round-001-en/C03-005/gamma_forces{suffix}.npz');H=-(z['plus'].astype(float)-z['minus'].astype(float)).reshape(60,60).T/(2*h)
    for j in [50,59]:signed[material]['historical_column_signed_differences_eV_A2'][f'{h}:{j}']=(columns[f'{h}:{j}']-H[:,j]).tolist()
 save(out/'signed-comparisons.json',signed);save(out/'decision.json',{'materials':summary,'full_gamma_or_stability_acceptance':False,'original_replay_acceptance':'failed unchanged','migration_complete':False})
