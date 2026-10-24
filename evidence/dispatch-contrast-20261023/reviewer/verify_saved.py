"""Independent saved-data arithmetic/integrity review. Never constructs a model."""
from pathlib import Path
import hashlib
import json
import numpy as np

PRIVATE = Path(os.environ['MATTERLAB_CONTRAST_OUTPUT'])
R1 = Path('[R1_PUBLIC_EVIDENCE]/R1')
CHECKPOINT = Path(os.environ['MATTERLAB_ROOT'])
OUTPUT = Path('[INDEPENDENT_REVIEW]')
checks = []

def load(path):
    return json.loads(path.read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(name, value):
    checks.append({'name': name, 'passed': bool(value)})

def arrays(directory):
    result = {}
    for stem, metadata in [('input-arrays', 'input-array-hashes'), ('neighbors', 'neighbor-hashes'), ('graph', 'graph-hashes'), ('model-output', 'model-output-hashes')]:
        with np.load(directory / (stem + '.npz'), allow_pickle=False) as archive:
            values = {key: archive[key].copy() for key in archive.files}
        hashes = load(directory / (metadata + '.json'))
        check(f'{directory.name}/{stem}/keys', set(values) == set(hashes))
        for key, value in values.items():
            expected = hashes[key]
            check(f'{directory.name}/{stem}/{key}', value.size > 0 and np.isfinite(value).all() and str(value.dtype) == expected['dtype'] and list(value.shape) == expected['shape'] and hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest() == expected['data_sha256'])
        result[stem] = values
    return result

raw = {}
for name, directory in [('R1', R1), ('C0-control', PRIVATE / 'C0-control'), ('C1-default', PRIVATE / 'C1-default')]:
    manifest = load(directory / 'manifest.json')['files']
    actual_files = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name != 'manifest.json'}
    check(name + '/manifest-coverage', set(manifest) == actual_files)
    for relative, expected in manifest.items():
        check(name + '/manifest/' + relative, digest(directory / relative) == expected)
    raw[name] = arrays(directory)
    counts = load(directory / 'capture-summary.json')
    check(name + '/one-model-one-graph', counts['graph_calls'] == counts['model_calls'] == 1)
    check(name + '/model-output-keys', set(raw[name]['model-output']) == {'atoms_per_graph', 'm_0', 'crystal_fea', 'e', 'f_0', 's_0'})
    model = raw[name]['model-output']
    observation = load(directory / 'observations.json')
    gpa = load(R1.parent / 'model-ASE-consistency.json')['ASE_GPa_eV_A3']
    stress = model['s_0'] * gpa
    converted = {'energy_eV': model['e'][0] * 20, 'forces_eV_A': model['f_0'], 'stress_eV_A3': (stress + stress.T) / 2}
    check(name + '/independent-model-ASE-conversion', all(np.array_equal(value, observation[key]) for key, value in converted.items()))

for stem in raw['R1']:
    check('control-exact/' + stem, all(np.array_equal(value, raw['R1'][stem][key]) and value.dtype == raw['R1'][stem][key].dtype for key, value in raw['C0-control'][stem].items()))
    if stem != 'model-output':
        check('altered-invariant/' + stem, all(np.array_equal(value, raw['C0-control'][stem][key]) and value.dtype == raw['C0-control'][stem][key].dtype for key, value in raw['C1-default'][stem].items()))

summary = {}
for name in ['C0-control', 'C1-default']:
    directory = PRIVATE / name
    observations = load(directory / 'observations.json')
    recorded = load(PRIVATE / (name + '-comparisons.json'))['comparisons']
    summary[name] = {}
    for reference_name, saved in recorded.items():
        reference = R1 if reference_name == 'R1' else PRIVATE / reference_name if reference_name == 'C0-control' else CHECKPOINT / 'evidence/restoration-20261023' / reference_name
        other = load(reference / 'observations.json')
        summary[name][reference_name] = {}
        for key, comparison in saved['observables'].items():
            check(f'{name}/{reference_name}/{key}/unchanged-tolerance', comparison['atol'] == {'energy_eV': 1e-5, 'forces_eV_A': 1e-6, 'stress_eV_A3': 1e-7}[key])
            new, old = np.asarray(observations[key], dtype=np.float64), np.asarray(other[key], dtype=np.float64)
            difference = new - old
            maximum = float(np.abs(difference).max())
            exact = np.array_equal(new, old)
            passed = np.isfinite(difference).all() and (np.abs(difference) <= comparison['atol']).all()
            check(f'{name}/{reference_name}/{key}/signed-difference', np.array_equal(difference, np.asarray(comparison['signed_difference'])))
            check(f'{name}/{reference_name}/{key}/max-equality-tolerance', maximum == comparison['max_abs_difference'] and exact == comparison['exact_equal'] and bool(passed) == comparison['passed'] and comparison['rtol'] == 0)
            summary[name][reference_name][key] = {'max_abs_difference': maximum, 'exact_equal': bool(exact), 'passed': bool(passed), 'components': new.size}
        if 'arrays' in saved:
            for stem, values in saved['arrays'].items():
                check(f'{name}/{reference_name}/{stem}/keysets', set(values) == set(raw[name][stem]) == set(raw[reference_name][stem]))
                for key, comparison in values.items():
                    new, old = raw[name][stem][key], raw[reference_name][stem][key]
                    difference = new.astype(np.float64) - old.astype(np.float64)
                    check(f'{name}/{reference_name}/{stem}/{key}/difference', np.array_equal(difference, np.asarray(comparison['signed_difference'])) and float(np.abs(difference).max()) == comparison['max_abs_difference'] and np.array_equal(new, old) == comparison['exact_equal'] and str(new.dtype) == comparison['dtype'] and str(old.dtype) == comparison['reference_dtype'])
            check(f'{name}/{reference_name}/parameter-hash-equality', load(directory / 'model-tensor-hashes.json') == load(reference / 'model-tensor-hashes.json'))

runtime0 = load(PRIVATE / 'C0-control/runtime.json')
runtime1 = load(PRIVATE / 'C1-default/runtime.json')
differences = {key: {'control': runtime0[key], 'altered': runtime1[key]} for key in runtime0 if runtime0[key] != runtime1[key]}
normalized = []
for original in [runtime0, runtime1]:
    current = dict(original)
    for key in ['condition', 'cpu_capability']:
        current.pop(key)
    current['environment_controls'] = dict(current['environment_controls'])
    current['environment_controls'].pop('ATEN_CPU_CAPABILITY')
    current['torch_build'] = '\n'.join(line for line in current['torch_build'].splitlines() if not line.strip().startswith('- CPU capability usage:'))
    normalized.append(current)
check('posthoc-only/remaining-reported-runtime-exact', normalized[0] == normalized[1])
check('frozen-C1-gate-retained-failed', load(PRIVATE / 'C1-default-gate.json')['comparison_assumptions_passed'] is False)
check('no-C2-attempt', not (PRIVATE / 'C2-default-repeat-ATTEMPT.json').exists())

preservation = load(OUTPUT / 'R1-review-start-hashes.json')['files']
r1_parent = R1.parent
current = {str(p.relative_to(r1_parent)): digest(p) for p in r1_parent.rglob('*') if p.is_file()}
check('completed-R1-106-files-unchanged', current == preservation)

report = {'scope': 'Independent saved-array and scalar arithmetic/integrity checks only; no inference or model imports', 'passed': all(item['passed'] for item in checks), 'checks_count': len(checks), 'checks': checks, 'numerical_summary': summary, 'runtime_differing_fields': list(differences), 'posthoc_runtime_explanation': 'The sole additional differing field after intended exceptions is torch_build; its only differing line duplicates CPU capability usage. Removing that line is explanatory only and does not override the frozen failed gate.', 'C2_performed': False}
(OUTPUT / 'saved-data-review.json').write_text(json.dumps(report, indent=2) + '\n')
(OUTPUT / 'runtime-difference-review.json').write_text(json.dumps(differences, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'checks': len(checks), 'failed': [item for item in checks if not item['passed']], 'summary': summary}))
