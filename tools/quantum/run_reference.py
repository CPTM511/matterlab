#!/usr/bin/env python3
"""Real QE/PBE fixed-cell SCF; Python stdlib only. No ML substitution."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import time

ROOT = Path(__file__).resolve().parents[2]
RY_EV = 13.605693122994


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ecut', type=int, default=60, help='wavefunction cutoff, Ry')
    ap.add_argument('--rho', type=int, default=600, help='density cutoff, Ry')
    ap.add_argument('--k', type=int, default=4)
    ap.add_argument('--threads', type=int, default=2)
    ap.add_argument('--timeout', type=int, default=1800)
    ap.add_argument('--mixing', type=float, default=0.1)
    ap.add_argument('--mixing-ndim', type=int, default=12)
    ap.add_argument('--diagonalization', choices=['david', 'cg'], default='david')
    ap.add_argument('--solver', choices=['mpich', 'openmpi'], default='openmpi')
    ap.add_argument('--warm-start', help='Previous same-cell run directory containing QE scratch files')
    args = ap.parse_args()
    name = f'catio3-cubic-e{args.ecut}-r{args.rho}-k{args.k}-m{args.mixing:g}-n{args.mixing_ndim}-{args.diagonalization}-{args.solver}'
    run = ROOT / 'runs/quantum' / name
    run.mkdir(parents=True, exist_ok=True)
    if (run / 'output.out').exists():
        raise SystemExit(f'Refusing to overwrite existing evidence: {run}')
    start_settings = ''
    if args.warm_start:
        previous = Path(args.warm_start).resolve()
        previous_summary = json.loads((previous / 'summary.json').read_text())
        if previous_summary['structure'] != 'ideal cubic CaTiO3, 5 atoms, fixed a=3.89 Angstrom; not claimed stable or novel':
            raise SystemExit('Warm-start is restricted to the identical reference geometry')
        for filename, expected in previous_summary['pseudopotentials'].items():
            if hashlib.sha256((ROOT / '.tools/pseudo' / filename).read_bytes()).hexdigest() != expected:
                raise SystemExit('Warm-start pseudopotential mismatch')
        shutil.copytree(previous / 'scratch', run / 'scratch', dirs_exist_ok=True)
        (run / 'scratch/catio3.EXIT').unlink(missing_ok=True)
        with tarfile.open(run / 'initial-density.tar.gz', 'w:gz') as archive:
            for filename in ['charge-density.hdf5', 'paw.txt', 'data-file-schema.xml']:
                source = previous / 'scratch/catio3.save' / filename
                if source.exists():
                    archive.add(source, arcname=f'scratch/catio3.save/{filename}')
        start_settings = "startingpot='file', startingwfc='atomic+random',"
    pseudo = ROOT / '.tools/pseudo'
    inp = f"""&CONTROL
 calculation='scf', prefix='catio3', pseudo_dir='{pseudo}',
 outdir='./scratch', tprnfor=.true., tstress=.true., disk_io='low'
/
&SYSTEM
 ibrav=1, A=3.89, nat=5, ntyp=3,
 ecutwfc={args.ecut}, ecutrho={args.rho}, occupations='fixed', input_dft='PBE'
/
&ELECTRONS
 conv_thr=1.0d-9, electron_maxstep=100, mixing_beta={args.mixing}, mixing_ndim={args.mixing_ndim},
 diagonalization='{args.diagonalization}', {start_settings}
/
ATOMIC_SPECIES
Ca 40.078 Ca.pbe-spn-kjpaw_psl.1.0.0.UPF
Ti 47.867 Ti.pbe-spn-kjpaw_psl.1.0.0.UPF
O 15.999 O.pbe-n-kjpaw_psl.1.0.0.UPF
ATOMIC_POSITIONS crystal
Ca 0.0 0.0 0.0
Ti 0.5 0.5 0.5
O 0.5 0.5 0.0
O 0.5 0.0 0.5
O 0.0 0.5 0.5
K_POINTS automatic
{args.k} {args.k} {args.k} 0 0 0
"""
    (run / 'input.in').write_text(inp)
    env = dict(os.environ, OMP_NUM_THREADS=str(args.threads), OPENBLAS_NUM_THREADS='1')
    solver_dir = 'qe' if args.solver == 'mpich' else 'qe-openmpi'
    cmd = [str(ROOT / '.tools' / solver_dir / 'bin/pw.x'), '-in', 'input.in']
    start = time.time()
    timed_out = False
    with (run / 'output.out').open('w') as out:
        try:
            result = subprocess.run(cmd, cwd=run, env=env, stdout=out, stderr=subprocess.STDOUT, timeout=args.timeout)
            code = result.returncode
        except subprocess.TimeoutExpired:
            timed_out, code = True, None
    output = (run / 'output.out').read_text()
    schema = run / 'scratch/catio3.save/data-file-schema.xml'
    if schema.exists():
        shutil.copyfile(schema, run / 'data-file-schema.xml')
    energies = re.findall(r'!\s+total energy\s+=\s+([-\d.]+)\s+Ry', output)
    scf = re.findall(r'convergence has been achieved in\s+(\d+) iterations', output)
    version = re.search(r'Program PWSCF\s+v\.(\S+)', output)
    pressure = re.findall(r'P=\s*([-\d.]+)', output)
    forces = re.findall(r'Total force\s*=\s*([-\d.]+)', output)
    summary = {
        'calculation': 'actual plane-wave PBE PAW density-functional theory SCF',
        'structure': 'ideal cubic CaTiO3, 5 atoms, fixed a=3.89 Angstrom; not claimed stable or novel',
        'settings': vars(args), 'command': cmd, 'returncode': code,
        'started_utc': datetime.fromtimestamp(start, timezone.utc).isoformat(),
        'solver_version': version.group(1) if version else None,
        'solver_sha256': hashlib.sha256(Path(cmd[0]).read_bytes()).hexdigest(),
        'timed_out': timed_out, 'wall_seconds': time.time() - start,
        'job_done': 'JOB DONE.' in output, 'scf_converged': bool(scf),
        'scf_iterations': int(scf[-1]) if scf else None,
        'total_energy_Ry': float(energies[-1]) if energies else None,
        'pressure_kbar': float(pressure[-1]) if pressure else None,
        'total_force_Ry_per_bohr': float(forces[-1]) if forces else None,
        'pseudopotentials': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(pseudo.glob('*.UPF'))},
        'input_sha256': hashlib.sha256(inp.encode()).hexdigest(),
        'output_sha256': hashlib.sha256(output.encode()).hexdigest(),
        'runtime_warnings': [line.strip() for line in output.splitlines() if 'floating-point exceptions' in line],
        'limitations': 'No ionic/cell relaxation, phonons, competing-phase hull, band-gap validation, or novelty proof. Compare cutoffs and k meshes before using numerical energies.'
    }
    (run / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    if not (code == 0 and summary['job_done'] and summary['scf_converged']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
