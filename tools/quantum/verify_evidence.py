#!/usr/bin/env python3
"""Verify recorded bytes and successful-run claims; failures remain failures."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument('--write-manifest', action='store_true', help='Create/update release manifest after finalizing evidence')
args = ap.parse_args()
errors = []
records = []
for path in sorted((ROOT / 'runs/quantum').glob('catio3-cubic-*/summary.json')):
    s = json.loads(path.read_text())
    for name, key in [('input.in', 'input_sha256'), ('output.out', 'output_sha256')]:
        p = path.parent / name
        if hashlib.sha256(p.read_bytes()).hexdigest() != s[key]:
            errors.append(f'{p}: SHA256 differs')
    output = (path.parent / 'output.out').read_text()
    raw_scf = bool(re.search(r'convergence has been achieved in\s+\d+ iterations', output))
    if raw_scf != s['scf_converged'] or ('JOB DONE.' in output) != s['job_done']:
        errors.append(f'{path}: status disagrees with raw output')
    accepted = s['returncode'] == 0 and s['job_done'] and s['scf_converged']
    if accepted:
        energy = re.findall(r'!\s+total energy\s+=\s+([-\d.]+)\s+Ry', output)
        if not energy or float(energy[-1]) != s['total_energy_Ry']:
            errors.append(f'{path}: energy disagrees with raw output')
        if not math.isfinite(s['total_energy_Ry']):
            errors.append(f'{path}: non-finite energy')
        schema = path.parent / 'data-file-schema.xml'
        if schema.exists():
            xml = ET.parse(schema).getroot()
            etot = xml.find('.//total_energy/etot')
            converged = xml.find('.//scf_conv/convergence_achieved')
            if etot is None or abs(2 * float(etot.text) - s['total_energy_Ry']) > 1e-7:
                errors.append(f'{path}: XML Hartree energy disagrees with raw Rydberg energy')
            if converged is None or converged.text.strip() != 'true':
                errors.append(f'{path}: XML does not confirm SCF convergence')
    for name, expected in s['pseudopotentials'].items():
        if hashlib.sha256((ROOT / '.tools/pseudo' / name).read_bytes()).hexdigest() != expected:
            errors.append(f'{path}: {name} SHA256 differs')
    records.append({'run': path.parent.name, 'execution_and_scf_success': accepted,
                    'returncode': s['returncode'], 'scf_converged': s['scf_converged'],
                    'runtime_warnings': [line.strip() for line in output.splitlines() if 'floating-point exceptions' in line]})
result = {'recorded_runs': len(records), 'successful_runs': sum(r['execution_and_scf_success'] for r in records),
          'records': records, 'integrity_errors': errors,
          'scope': 'Verifies stored evidence integrity, not physical convergence, stability, novelty, or experimental properties.'}
(ROOT / 'runs/quantum/evidence-verification.json').write_text(json.dumps(result, indent=2) + '\n')
if args.write_manifest and not errors:
    files = [p for p in (ROOT / 'runs/quantum').rglob('*')
             if p.is_file() and 'scratch' not in p.relative_to(ROOT).parts and p.name != 'manifest.sha256']
    files += [p for p in (ROOT / 'tools/quantum').iterdir() if p.is_file()]
    files += [ROOT / 'docs/quantum-validation.md']
    manifest = ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n'
                       for p in sorted(files))
    (ROOT / 'runs/quantum/manifest.sha256').write_text(manifest)
print(json.dumps(result, indent=2))
raise SystemExit(bool(errors) or not records)
