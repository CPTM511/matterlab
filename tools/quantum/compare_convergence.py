#!/usr/bin/env python3
"""Compare completed reference runs, without equating SCF with basis convergence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RY_EV = 13.605693122994
runs = []
unaccepted = []
for path in sorted((ROOT / 'runs/quantum').glob('catio3-cubic-*/summary.json')):
    s = json.loads(path.read_text())
    if s['job_done'] and s['scf_converged'] and s['returncode'] == 0:
        runs.append({'run': path.parent.name, **s})
    else:
        unaccepted.append({'run': path.parent.name, 'returncode': s['returncode'],
                           'scf_converged': s['scf_converged'], 'job_done': s['job_done']})
pairs = []
for a, b in zip(sorted(runs, key=lambda r: (r['settings']['ecut'], r['settings']['k'])), sorted(runs, key=lambda r: (r['settings']['ecut'], r['settings']['k']))[1:]):
    delta = abs(b['total_energy_Ry'] - a['total_energy_Ry']) * RY_EV * 1000 / 5
    pairs.append({'from': a['run'], 'to': b['run'], 'absolute_delta_meV_per_atom': delta,
                  'below_exploratory_1_meV_per_atom': delta < 1.0})
summary = {'runs': [{'run': r['run'], 'total_energy_Ry': r['total_energy_Ry'],
                     'wall_seconds': r['wall_seconds'], 'scf_iterations': r['scf_iterations'],
                     'settings': r['settings']} for r in runs],
           'adjacent_comparisons': pairs,
           'unaccepted_runs': unaccepted,
           'numerical_convergence_status': ('exploratory_comparisons_passed' if len({r['settings']['ecut'] for r in runs}) >= 2 and len({r['settings']['k'] for r in runs}) >= 2 and all(p['below_exploratory_1_meV_per_atom'] for p in pairs) else 'not_established'),
           'criterion': 'Exploratory absolute-energy change <1 meV/atom between adjacent settings; not a proof of complete basis/k convergence or force/stress convergence.',
           'scope': 'Identical ideal cubic CaTiO3 cell and pseudopotentials only; different compositions must not be compared by absolute total energy.'}
(ROOT / 'runs/quantum/convergence.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
