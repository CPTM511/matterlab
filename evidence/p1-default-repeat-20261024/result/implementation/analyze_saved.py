"""Saved-capture analysis only. Partial/corrupt evidence is retained and marked unavailable."""
import hashlib
import json
from pathlib import Path
import numpy as np
from ase import units
from runtime_compare import compare_runtime, typed_equal

TOLERANCES = {'energy_eV': 1e-5, 'forces_eV_A': 1e-6, 'stress_eV_A3': 1e-7}
ARCHIVES = {'input-arrays': 'input-array-hashes', 'neighbors': 'neighbor-hashes', 'graph': 'graph-hashes', 'model-output': 'model-output-hashes'}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def byte_equal(left, right):
    a, b = np.asarray(left), np.asarray(right)
    return a.dtype.str == b.dtype.str and a.shape == b.shape and np.ascontiguousarray(a).tobytes() == np.ascontiguousarray(b).tobytes()

def same_types(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(same_types(x, y) for x, y in zip(a, b, strict=True))
    if isinstance(a, dict):
        return set(a) == set(b) and all(same_types(a[k], b[k]) for k in a)
    return True

def array_record(array):
    return {'dtype': str(array.dtype), 'shape': list(array.shape), 'data_sha256': hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()}

def unavailable(reason):
    return {'comparable': False, 'reason': reason, 'signed_difference': None, 'max_abs_difference': None, 'exact_equal': False, 'passed': False}

def comparison(left, right, atol=0):
    try:
        a, b = np.asarray(left), np.asarray(right)
        if a.shape != b.shape or not a.size or not b.size or not np.isfinite(a).all() or not np.isfinite(b).all():
            return unavailable('Empty, nonfinite, unsupported or shape-mismatched array')
        with np.errstate(over='ignore', invalid='ignore'):
            difference = a.astype(np.float64) - b.astype(np.float64)
        if not np.isfinite(difference).all():
            return unavailable('Difference overflow/nonfinite; raw input retained')
        return {'comparable': True, 'shape': list(a.shape), 'dtype': a.dtype.str, 'reference_dtype': b.dtype.str, 'signed_difference': difference.tolist(), 'max_abs_difference': float(np.abs(difference).max()), 'exact_equal': byte_equal(a, b), 'numerical_equal': bool(np.array_equal(a, b)), 'atol': atol, 'rtol': 0, 'passed': bool((np.abs(difference) <= atol).all())}
    except (TypeError, ValueError, OverflowError) as error:
        return unavailable(type(error).__name__)

def model_to_ase(model):
    # Preserve float32 operation order; float(e[0])*20 and upcast stress are different.
    stress = model['s_0'] * units.GPa
    return {'energy_eV': float(model['e'][0] * 20), 'forces_eV_A': model['f_0'] * 1, 'stress_eV_A3': (stress + stress.T) / 2}

def analyze(root, output):
    root, output = Path(root), Path(output)
    data = output / 'P1'
    checks, errors, missing, raw = [], [], [], {}
    def ck(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})
    def problem(label, error):
        errors.append({'artifact': label, 'error': str(error)})
    def read_json(path, label):
        try:
            def reject_constant(value):
                raise ValueError('Nonfinite JSON constant: ' + value)
            value = json.loads(path.read_text(), parse_constant=reject_constant)
            if not isinstance(value, dict):
                raise ValueError('Expected JSON object')
            return value
        except (OSError, ValueError, TypeError) as error:
            missing.append(label)
            problem(label, error)
            return None
    def read_arrays(path, label):
        values = {}
        try:
            with np.load(path, allow_pickle=False) as archive:
                for key in archive.files:
                    try:
                        values[key] = archive[key].copy()
                    except Exception as error:
                        problem(label + ':' + key, error)
        except Exception as error:
            missing.append(label)
            problem(label, error)
        return values
    references = {'C1': root / 'evidence/dispatch-contrast-20261023/C1-default', 'C0': root / 'evidence/dispatch-contrast-20261023/C0-control', 'R1': root / 'evidence/repaired-recorder-20261023/R1'}
    references.update({name: root / 'evidence/restoration-20261023' / name for name in ['baseline-001', 'baseline-002', 'replay']})
    for stem, metadata in ARCHIVES.items():
        raw[stem] = read_arrays(data / (stem + '.npz'), stem)
        records = read_json(data / (metadata + '.json'), metadata)
        ck(stem + ':nonempty_record_set', bool(raw[stem]) and records is not None and set(raw[stem]) == set(records))
        for key, array in raw[stem].items():
            try:
                finite = array.size > 0 and np.isfinite(array).all()
            except (ValueError, TypeError):
                finite = False
            ck(stem + ':' + key + ':finite', finite)
            ck(stem + ':' + key + ':digest', records is not None and key in records and typed_equal(array_record(array), records[key]))
    manifest = read_json(data / 'manifest.json', 'recorder_manifest')
    if manifest is not None:
        if not isinstance(manifest.get('files'), dict) or not manifest['files']:
            ck('recorder_manifest_schema', False)
        else:
            actual_files = {str(f.relative_to(data)) for f in data.rglob('*') if f.is_file() and f.name != 'manifest.json'}
            ck('recorder_manifest_complete_coverage', set(manifest['files']) == actual_files)
            for name, digest in manifest['files'].items():
                file = (data / name).resolve()
                ck('manifest:' + name, file.is_relative_to(data.resolve()) and file.is_file() and sha(file) == digest)
    observations = read_json(data / 'observations.json', 'ASE_observations')
    comparisons = {}
    for name, directory in references.items():
        reference = read_json(directory / 'observations.json', 'reference:' + name)
        result = {'observables': {}, 'arrays': {}}
        for key, tolerance in TOLERANCES.items():
            if observations is None or reference is None or key not in observations or key not in reference:
                result['observables'][key] = unavailable('Missing observation/reference field')
                if name == 'C1':
                    ck('observation:' + key + ':present', False)
                continue
            if name == 'C1':
                ck('observation:' + key + ':JSON_types', same_types(observations[key], reference[key]))
            try:
                c = comparison(np.asarray(observations[key], dtype=np.float64), np.asarray(reference[key], dtype=np.float64), tolerance)
                c['exact_equal'] = bool(c['exact_equal'] and typed_equal(observations[key], reference[key]))
            except (ValueError, TypeError) as error:
                c = unavailable(type(error).__name__)
            result['observables'][key] = c
        for stem, values in raw.items():
            file = directory / (stem + '.npz')
            if not file.exists():
                continue
            old = read_arrays(file, 'reference:' + name + ':' + stem)
            result['arrays'][stem] = {key: comparison(array, old[key]) if key in old else unavailable('Missing reference array') for key, array in values.items()}
            if name == 'C1':
                ck(stem + ':C1_keys', bool(values) and set(values) == set(old))
                for key, array in values.items():
                    ck(stem + ':' + key + ':C1_structure', key in old and array.shape == old[key].shape and array.dtype.str == old[key].dtype.str)
                if stem != 'model-output':
                    ck(stem + ':C1_exact_invariant', bool(result['arrays'][stem]) and all(x['exact_equal'] for x in result['arrays'][stem].values()))
        comparisons[name] = result
    for name in ['input.cif', 'config-original.json']:
        file = data / name
        ck('raw:' + name, file.is_file() and file.read_bytes() == (references['C1'] / name).read_bytes())
    for recorded, implementation in [('diagnostic_eval.py', 'guarded_recorder.py'), ('capture_helpers.py', 'capture_helpers.py')]:
        file = data / recorded
        ck('recorder_implementation:' + recorded, file.is_file() and sha(file) == sha(Path(__file__).with_name(implementation)))
    captures = read_json(data / 'capture-summary.json', 'capture_summary')
    ck('one_forward_one_graph', captures is not None and type(captures.get('graph_calls')) is int and type(captures.get('model_calls')) is int and captures['graph_calls'] == captures['model_calls'] == 1)
    runtime = read_json(data / 'runtime.json', 'runtime')
    ref_runtime = read_json(references['C1'] / 'runtime.json', 'C1_runtime_reference')
    runtimes = {'primary_C1': compare_runtime(runtime, ref_runtime)}
    runtimes['secondary_C0'] = compare_runtime(runtime, read_json(references['C0'] / 'runtime.json', 'C0_runtime_reference'), dispatch_contrast=True)
    ck('primary_runtime_exact', runtimes['primary_C1']['passed'])
    guard = read_json(data / 'pre-inference-runtime-check.json', 'pre_inference_runtime_guard')
    ck('pre_inference_runtime_guard', guard is not None and guard.get('passed') is True)
    parameters = read_json(data / 'model-tensor-hashes.json', 'parameter_hashes')
    ck('model_parameters_exact', parameters is not None and typed_equal(parameters, read_json(references['C1'] / 'model-tensor-hashes.json', 'C1_parameter_reference')))
    conversion = {}
    try:
        converted = model_to_ase(raw['model-output'])
        for key, value in converted.items():
            conversion[key] = comparison(np.asarray(value, dtype=np.float64), np.asarray(observations[key], dtype=np.float64)) if observations is not None and key in observations else unavailable('Missing ASE field')
        ck('float32_model_ASE_conversion', all(x['exact_equal'] for x in conversion.values()))
    except (KeyError, ValueError, TypeError, IndexError) as error:
        problem('model_ASE_conversion', error)
        conversion = {key: unavailable('Incomplete/malformed model or ASE capture') for key in TOLERANCES}
        ck('float32_model_ASE_conversion', False)
    ck('20_atoms_no_relaxation', observations is not None and type(observations.get('atoms')) is int and observations['atoms'] == 20 and observations.get('relaxation_performed') is False)
    try:
        ck('ASE_shapes', observations is not None and np.asarray(observations['forces_eV_A']).shape == (20, 3) and np.asarray(observations['stress_eV_A3']).shape == (3, 3))
    except (KeyError, ValueError, TypeError):
        ck('ASE_shapes', False)
    try:
        n, g, inp = raw['neighbors'], raw['graph'], raw['input-arrays']
        ck('neighbors_match_graph', np.array_equal(g['atom_graph'], np.column_stack([n['center'], n['neighbor']])) and np.array_equal(g['neighbor_image'], n['image'].astype(np.float32)))
        ck('input_matches_graph', np.array_equal(inp['atomic_numbers'], g['atomic_number']) and np.array_equal(inp['frac_coords'].astype(np.float32), g['atom_frac_coord']) and np.array_equal(inp['lattice'].astype(np.float32), g['lattice']))
    except (KeyError, ValueError, TypeError):
        ck('captured_geometry_relationships', False)
    execution = read_json(output / 'execution.json', 'execution_record')
    ck('single_successful_execution', execution is not None and type(execution.get('attempts')) is int and execution['attempts'] == 1 and execution.get('completed') is True and type(execution.get('returncode')) is int and execution['returncode'] == 0)
    c1 = comparisons['C1']
    complete = not missing and not errors and all(c['passed'] for c in checks)
    exact = complete and all(x['exact_equal'] for x in c1['observables'].values()) and bool(c1['arrays'].get('model-output')) and all(x['exact_equal'] for x in c1['arrays']['model-output'].values())
    original_values = [x for name in ['baseline-001', 'baseline-002'] for x in comparisons[name]['observables'].values()]
    original = all(x['passed'] for x in original_values) if all(x['comparable'] for x in original_values) else None
    outcome = 'H1_exact_pairwise_repeat' if exact else ('H2_changed_output_with_recorded_invariants_passed' if complete else 'inconclusive_failed_capture_or_comparison_assumptions')
    save(output / 'comparisons.json', {'convention': 'P1 minus named public reference', 'comparisons': comparisons, 'runtime': runtimes, 'model_ASE_conversion': conversion, 'D1_numerical_comparison': None, 'D1_reason': 'No persisted historical observations; not reconstructed'})
    save(output / 'integrity.json', {'passed': bool(complete), 'checks': checks, 'missing': missing, 'errors': errors})
    save(output / 'decision.json', {'primary_repeat_passed': bool(exact), 'outcome': outcome, 'original_baseline_acceptance': original, 'old_C1_gate': 'FAILED; unchanged', 'old_C2': 'not run', 'further_inference': 'none under this single-use protocol', 'missing': missing, 'errors': errors, 'interpretation': 'Pairwise equality only; no statistical or historical-cause claim. Changed outputs cannot isolate new guard-instrumentation effects from other unrecorded effects.', 'full_migration_complete': False})
    return bool(exact)

