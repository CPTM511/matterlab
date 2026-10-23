"""One CPU single-point evaluation; never a relaxation or research campaign."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import numpy as np
from ase.io import read
root = Path(__import__('os').environ['MATTERLAB_ROOT']).resolve()
sys.path.insert(0, str(root / 'src'))
import matterlab
assert Path(matterlab.__file__).resolve().is_relative_to(root / 'src'), 'Imported source mismatch'
from matterlab.evidence import snapshot, sha256, write_json, manifest
expected = json.loads(Path(__file__).with_name('code.json').read_text())['sources_sha256']
assert all(sha256(root / name) == value for name, value in expected.items()), 'Source hash mismatch'
from matterlab.simulate import make_calculator

root = Path(__import__('os').environ['MATTERLAB_ROOT']).resolve()
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=False)
config = json.loads((root / 'configs/round-001.json').read_text())
write_json(out / 'config.json', config)
shutil.copy2(__file__, out / 'evaluate.py')
source = root / 'runs/round-001-en/generated/R-CaTiO3.cif'
if not source.is_file():
    candidates = sorted((root / 'runs/round-001-en/generated').glob('*CaTi*.cif'))
    if len(candidates) != 1:
        raise RuntimeError(f'Expected one CaTiO3 input, found {candidates}')
    source = candidates[0]
shutil.copy2(source, out / 'input.cif')
snapshot(out, config)
write_json(out / 'code.json', {
    'git_head': subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
    'sources_sha256': {str(p.relative_to(root)): sha256(p) for p in sorted((root / 'src/matterlab').glob('*.py'))},
    'scope': 'Bounded CPU CHGNet single-point runtime check, not DFT or migration acceptance',
})
try:
    atoms = read(out / 'input.cif')
    atoms.calc = make_calculator(config)
    energy = float(atoms.get_potential_energy())
    forces = atoms.get_forces()
    stress = atoms.get_stress(voigt=False)
    assert np.isfinite(energy) and np.isfinite(forces).all() and np.isfinite(stress).all()
    write_json(out / 'observations.json', {'energy_eV': energy, 'forces_eV_A': forces.tolist(), 'stress_eV_A3': stress.tolist(), 'atoms': len(atoms), 'relaxation_performed': False})
    write_json(out / 'checkpoint.json', {'status': 'single_point_complete', 'next_step': 'Verify manifest and replay evaluate.py into a new directory. Do not resume historical campaigns across environments.', 'input_sha256': sha256(out / 'input.cif')})
except Exception:
    import traceback
    (out / 'failure.txt').write_text(traceback.format_exc())
    raise
finally:
    manifest(out)
print(json.dumps({'output': str(out), 'energy_eV': energy, 'atoms': len(atoms)}))
