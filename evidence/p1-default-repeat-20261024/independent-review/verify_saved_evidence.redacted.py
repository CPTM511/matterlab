"""Independent read-only saved-evidence verification. No model/source execution."""
from pathlib import Path, PurePosixPath
from datetime import datetime
import hashlib
import json
import math
import re
import tarfile
import zipfile
import numpy as np
from ase import units

BASE = Path('[PRIVATE_P1_ORIGINALS_ROOT]')
RAW = BASE / 'raw'
DATA = RAW / 'P1'
EXPORT = BASE / 'review-package'
OUT = BASE / 'independent-review'
FROZEN = Path('[PRIVATE_FROZEN_BUNDLE]')
PUBLIC = Path('[VERIFIED_PUBLIC_CHECKOUT]')
TOKEN = FROZEN.parent / 'execution-guard/P1-default-repeat-20261024.attempt.json'
checks = []
counts = {'manifest_entries': {}, 'arrays_rehashed': 0, 'array_elements_rehashed': 0, 'signed_observable_components': 0, 'signed_array_components': 0, 'signed_array_comparisons': 0}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':'))

def check(name, passed):
    checks.append({'name': name, 'passed': bool(passed)})

def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def file_set(root):
    return {str(p.relative_to(root)): sha(p) for p in root.rglob('*') if p.is_file()}

preservation_before = {label: file_set(root) for label, root in [('raw', RAW), ('export', EXPORT), ('frozen', FROZEN)]}
preservation_before['external'] = {'archive': sha(BASE / 'P1-result-review.tar.gz'), 'attempt_token': sha(TOKEN)}
write('review-start-hashes.json', preservation_before)

def verify_manifest(root, name, label, complete=True):
    expected = read(root / name)['files']
    counts['manifest_entries'][label] = len(expected)
    if complete:
        actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p != root / name and '.git' not in p.relative_to(root).parts}
        check(label + ':complete-coverage', set(expected) == actual)
    for relative, digest in expected.items():
        p = (root / relative).resolve()
        check(label + ':' + relative, p.is_relative_to(root.resolve()) and p.is_file() and sha(p) == digest)

verify_manifest(RAW, 'manifest-private.json', 'raw')
verify_manifest(DATA, 'manifest.json', 'recorder')
verify_manifest(EXPORT, 'manifest.json', 'export')
verify_manifest(EXPORT / 'P1', 'manifest.json', 'export-recorder')
verify_manifest(PUBLIC, 'publication/manifest.json', 'public')
verify_manifest(FROZEN, 'implementation-manifest.json', 'implementation', complete=False)

freeze = read(FROZEN / 'freeze.json')
for name, field in [('protocol.json', 'protocol_sha256'), ('PROTOCOL.md', 'protocol_markdown_sha256'), ('implementation-manifest.json', 'implementation_manifest_sha256')]:
    check('freeze-binding:' + name, sha(FROZEN / name) == freeze[field])
check('freeze-envelope-identity', sha(FROZEN / 'freeze.json') == 'fd475de8179f83f4cb71ffe7a8449ec43f72e7db20d501fe50354b87515ce1b9')
for name in file_set(FROZEN):
    check('raw-implementation:' + name, (RAW / 'implementation' / name).read_bytes() == (FROZEN / name).read_bytes())
    check('export-implementation:' + name, (EXPORT / 'implementation' / name).read_bytes() == (FROZEN / name).read_bytes())
check('actual-recorder-source', (DATA / 'diagnostic_eval.py').read_bytes() == (FROZEN / 'guarded_recorder.py').read_bytes())
check('actual-helper-source', (DATA / 'capture_helpers.py').read_bytes() == (FROZEN / 'capture_helpers.py').read_bytes())
expected_source = read(DATA / 'expected-source-code.json')
check('physics-source-identity', expected_source['git_head'] == '3319dc595397f68c0e7a3326e64c2b27ae799027')
for name, digest in expected_source['sources_sha256'].items():
    check('public-physics:' + name, sha(PUBLIC / name) == digest)

ARCHIVES = {'input-arrays': 'input-array-hashes', 'neighbors': 'neighbor-hashes', 'graph': 'graph-hashes', 'model-output': 'model-output-hashes'}

def arrays(directory, label):
    result = {}
    for stem, record_name in ARCHIVES.items():
        with np.load(directory / (stem + '.npz'), allow_pickle=False) as archive:
            result[stem] = {key: archive[key].copy() for key in archive.files}
        records = read(directory / (record_name + '.json'))
        check(label + '/' + stem + ':keys', set(result[stem]) == set(records))
        for key, array in result[stem].items():
            counts['arrays_rehashed'] += 1
            counts['array_elements_rehashed'] += int(array.size)
            metadata = records[key]
            check(label + '/' + stem + '/' + key + ':data', array.size > 0 and np.isfinite(array).all() and list(array.shape) == metadata['shape'] and str(array.dtype) == metadata['dtype'] and hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest() == metadata['data_sha256'])
    return result

def byte_equal(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return a.dtype.str == b.dtype.str and a.shape == b.shape and np.ascontiguousarray(a).tobytes() == np.ascontiguousarray(b).tobytes()

references = {'C1': PUBLIC / 'evidence/dispatch-contrast-20261023/C1-default', 'C0': PUBLIC / 'evidence/dispatch-contrast-20261023/C0-control', 'R1': PUBLIC / 'evidence/repaired-recorder-20261023/R1'}
references.update({name: PUBLIC / 'evidence/restoration-20261023' / name for name in ['baseline-001', 'baseline-002', 'replay']})
all_arrays = {'P1': arrays(DATA, 'P1')}
for name in ['C1', 'C0', 'R1']:
    all_arrays[name] = arrays(references[name], name)
raw = all_arrays['P1']
for stem, values in raw.items():
    for key, value in values.items():
        check('primary-byte-equality:' + stem + '/' + key, byte_equal(value, all_arrays['C1'][stem][key]))
for name in ['input.cif', 'config-original.json', 'model-tensor-hashes.json']:
    check('primary-file-equality:' + name, (DATA / name).read_bytes() == (references['C1'] / name).read_bytes())
check('six-model-tensor-keys', set(raw['model-output']) == {'atoms_per_graph', 'm_0', 'crystal_fea', 'e', 'f_0', 's_0'})

runtime = read(DATA / 'runtime.json')
runtime_ref = read(references['C1'] / 'runtime.json')
different_runtime_fields = [key for key in runtime if canonical(runtime[key]) != canonical(runtime_ref[key])]
check('runtime-only-condition-differs', set(runtime) == set(runtime_ref) and different_runtime_fields == ['condition'])
check('runtime-default-capability', runtime['cpu_capability'] == 'NO AVX' and runtime['environment_controls']['ATEN_CPU_CAPABILITY'] == 'default')
capability_lines = [line for line in runtime['torch_build'].splitlines() if 'CPU capability usage:' in line]
check('runtime-one-canonical-capability', capability_lines == ['  - CPU capability usage: NO AVX'])
check('runtime-threads-seed-affinity', runtime['torch_num_threads'] == runtime['torch_num_interop_threads'] == 1 and runtime['seed'] == 20261024 and runtime['cpu_affinity'] == [0] and runtime['device'] == 'cpu')
check('preinference-runtime-guard', read(DATA / 'pre-inference-runtime-check.json')['passed'] is True)

observations = read(DATA / 'observations.json')
check('primary-observations-exact-typed-JSON', canonical(observations) == canonical(read(references['C1'] / 'observations.json')))
model = raw['model-output']
stress = model['s_0'] * units.GPa
converted = {'energy_eV': float(model['e'][0] * 20), 'forces_eV_A': model['f_0'] * 1, 'stress_eV_A3': (stress + stress.T) / 2}
check('float32-conversion-dtypes', (model['e'][0] * 20).dtype == np.dtype('float32') and stress.dtype == np.dtype('float32') and converted['stress_eV_A3'].dtype == np.dtype('float32'))
for key, value in converted.items():
    check('model-to-ASE:' + key, byte_equal(np.asarray(value, dtype=np.float64), np.asarray(observations[key], dtype=np.float64)))
check('ASE-shapes', np.asarray(observations['forces_eV_A']).shape == (20, 3) and np.asarray(observations['stress_eV_A3']).shape == (3, 3) and observations['atoms'] == 20 and observations['relaxation_performed'] is False)
n, g, inp = raw['neighbors'], raw['graph'], raw['input-arrays']
check('consumed-neighbor-graph', byte_equal(g['atom_graph'], np.column_stack([n['center'], n['neighbor']])) and byte_equal(g['neighbor_image'], n['image'].astype(np.float32)))
check('graph-input-arrays', np.array_equal(inp['atomic_numbers'], g['atomic_number']) and byte_equal(inp['frac_coords'].astype(np.float32), g['atom_frac_coord']) and byte_equal(inp['lattice'].astype(np.float32), g['lattice']))

saved = read(RAW / 'comparisons.json')
tolerances = {'energy_eV': 1e-5, 'forces_eV_A': 1e-6, 'stress_eV_A3': 1e-7}
summary = {}
def verify_comparison(label, new, old, reported, tolerance):
    new, old = np.asarray(new), np.asarray(old)
    difference = new.astype(np.float64) - old.astype(np.float64)
    exact = byte_equal(new, old)
    check(label + ':signed-components', byte_equal(difference, np.asarray(reported['signed_difference'], dtype=np.float64)))
    check(label + ':metadata-decisions', reported['comparable'] is True and reported['shape'] == list(new.shape) and reported['dtype'] == new.dtype.str and reported['reference_dtype'] == old.dtype.str and reported['max_abs_difference'] == float(np.abs(difference).max()) and reported['exact_equal'] == exact and reported['numerical_equal'] == bool(np.array_equal(new, old)) and reported['atol'] == tolerance and reported['rtol'] == 0 and reported['passed'] == bool((np.abs(difference) <= tolerance).all()))
    return int(new.size)

check('complete-comparison-reference-set', set(saved['comparisons']) == set(references))
for name, directory in references.items():
    reference_obs = read(directory / 'observations.json')
    comparison = saved['comparisons'][name]
    check('observables-keyset:' + name, set(comparison['observables']) == set(tolerances))
    summary[name] = {}
    for key, tolerance in tolerances.items():
        new, old = np.asarray(observations[key], dtype=np.float64), np.asarray(reference_obs[key], dtype=np.float64)
        counts['signed_observable_components'] += verify_comparison(name + '/' + key, new, old, comparison['observables'][key], tolerance)
        summary[name][key] = {'max_abs_difference': float(np.abs(new - old).max()), 'exact_equal': byte_equal(new, old), 'passed': bool((np.abs(new - old) <= tolerance).all())}
    expected_stems = set(ARCHIVES) if name in ['C1', 'C0', 'R1'] else set()
    check('array-comparison-archive-set:' + name, set(comparison['arrays']) == expected_stems)
    for stem, values in comparison['arrays'].items():
        check(name + '/' + stem + ':comparison-keys', set(values) == set(raw[stem]) == set(all_arrays[name][stem]))
        for key, item in values.items():
            counts['signed_array_comparisons'] += 1
            counts['signed_array_components'] += verify_comparison(name + '/' + stem + '/' + key, raw[stem][key], all_arrays[name][stem][key], item, 0)
for key, value in converted.items():
    verify_comparison('saved-conversion/' + key, np.asarray(value, dtype=np.float64), np.asarray(observations[key], dtype=np.float64), saved['model_ASE_conversion'][key], 0)
check('D1-unavailable-preserved', saved['D1_numerical_comparison'] is None)

# Independent secondary runtime normalization, permitted only for the descriptive contrast.
normalized = []
for item in [runtime, read(references['C0'] / 'runtime.json')]:
    item = json.loads(json.dumps(item))
    lines = [line for line in item['torch_build'].splitlines() if 'CPU capability usage:' in line]
    check('secondary-capability-validation:' + item['condition'], len(lines) == 1 and lines[0] == '  - CPU capability usage: ' + item['cpu_capability'])
    item.pop('condition')
    item.pop('cpu_capability')
    item['environment_controls'].pop('ATEN_CPU_CAPABILITY')
    item['torch_build'] = item['torch_build'].replace(lines[0] + '\n', '', 1)
    normalized.append(item)
check('secondary-runtime-normalized-equality', canonical(normalized[0]) == canonical(normalized[1]))
check('saved-runtime-comparisons', saved['runtime']['primary_C1']['passed'] is True and saved['runtime']['secondary_C0']['passed'] is True)

execution = read(RAW / 'execution.json')
analysis = read(RAW / 'analysis-execution.json')
preflight = read(RAW / 'preflight-execution.json')
capture = read(DATA / 'capture-summary.json')
check('one-recorded-graph-forward', capture['graph_calls'] == capture['model_calls'] == 1)
token = read(TOKEN)
check('protocol-token-identity', token['protocol_sha256'] == freeze['protocol_sha256'] and token['maximum_evaluations'] == 1 and Path(token['output_private']).resolve() == RAW.resolve())
check('inference-token-one', read(RAW / 'INFERENCE-ATTEMPT.json') == {'maximum_evaluations': 1})
check('one-recorded-attempt', execution['attempts'] == 1 and execution['completed'] is True and execution['returncode'] == 0 and execution['timeout'] is False and 'failure_type' not in execution)
check('process-resource-limits', 0 < execution['wall_seconds'] <= execution['requested_timeout_seconds'] <= 600 and 0 <= execution['investigation_elapsed_seconds'] <= 1800 and execution['investigation_limit_respected'] is True)
check('metadata-processes-success', all(item['returncode'] == 0 and 'failure_type' not in item and 0 < item['wall_seconds'] <= item['requested_timeout_seconds'] for item in [preflight, analysis]))
for name, record in [('preflight', preflight), ('calculation', execution), ('analysis', analysis)]:
    check(name + ':timestamps-ordered', datetime.fromisoformat(record['ended_at_utc']) > datetime.fromisoformat(record['started_at_utc']))
check('process-phases-ordered', preflight['ended_at_utc'] < execution['started_at_utc'] < execution['ended_at_utc'] < analysis['started_at_utc'])
complete = read(EXPORT / 'completion.json')
elapsed_reporting = (datetime.fromisoformat(complete['completed_at_utc']) - datetime.fromisoformat(complete['investigation_started_at_utc'])).total_seconds()
check('reporting-within-investigation-limit', elapsed_reporting == complete['elapsed_through_reporting_seconds'] and elapsed_reporting < 1800)
recorded_integrity = read(RAW / 'integrity.json')
check('recorded-integrity-120-pass', recorded_integrity['passed'] is True and len(recorded_integrity['checks']) == 120 and all(item['passed'] for item in recorded_integrity['checks']) and not recorded_integrity['errors'] and not recorded_integrity['missing'])
check('recorded-preflight-1498-pass', read(RAW / 'preflight.json')['passed'] is True and len(read(RAW / 'preflight.json')['checks']) == 1498 and all(item['passed'] for item in read(RAW / 'preflight.json')['checks']))
analysis_decision = read(RAW / 'analysis-decision.json')
final = dict(analysis_decision)
gate = execution['completed'] is True and type(execution['attempts']) is int and execution['attempts'] == 1 and type(execution['returncode']) is int and execution['returncode'] == 0 and execution['investigation_limit_respected'] is True and type(execution['wall_seconds']) in (int, float) and math.isfinite(execution['wall_seconds']) and 0 <= execution['wall_seconds'] <= 600 and math.isfinite(execution['investigation_elapsed_seconds']) and 0 <= execution['investigation_elapsed_seconds'] <= 1800 and 'failure_type' not in execution and type(analysis['returncode']) is int and analysis['returncode'] == 0 and 'failure_type' not in analysis
final['execution_and_resource_gate_passed'] = gate
check('independent-final-decision-reconstruction', gate and canonical(final) == canonical(read(RAW / 'decision.json')))
check('H1-and-historical-failure-separate', final['primary_repeat_passed'] is True and final['outcome'] == 'H1_exact_pairwise_repeat' and final['original_baseline_acceptance'] is False and final['old_C1_gate'] == 'FAILED; unchanged' and final['old_C2'] == 'not run' and final['full_migration_complete'] is False)
check('old-C1-gate-unchanged', read(PUBLIC / 'evidence/dispatch-contrast-20261023/C1-default-gate.json')['comparison_assumptions_passed'] is False)
check('old-C2-remains-absent', not list((PUBLIC / 'evidence/dispatch-contrast-20261023').glob('C2*')))
check('no-recorder-controller-failure-record', not (RAW / 'failure-private.txt').exists() and not (DATA / 'failure.txt').exists() and not (RAW / 'analysis-failure-private.txt').exists())

ledger = read(EXPORT / 'transformation-ledger.json')['entries']
ledger_actions = {}
mapped = set()
for item in ledger:
    action = item['action']
    ledger_actions[action] = ledger_actions.get(action, 0) + 1
    if action == 'excluded_private_record':
        check('excluded-private:' + item['source_relative'], not (EXPORT / item['source_relative']).exists())
        continue
    source = RAW / item['source_relative']
    if not source.exists():
        source = BASE / item['source_relative']
    destination = EXPORT / item['derivative_relative']
    mapped.add(item['derivative_relative'])
    check('ledger-hashes:' + item['derivative_relative'], sha(source) == item['source_sha256'] and sha(destination) == item['derivative_sha256'])
    if action == 'byte_identical_copy':
        check('ledger-byte-identical:' + item['derivative_relative'], source.read_bytes() == destination.read_bytes())
    elif action == 'path_redaction':
        sanitized = source.read_text().replace('[PRIVATE_RUNTIME_HOME]', '[RUNTIME_HOME]')
        sanitized = re.sub(r'/tmp/matplotlib-[A-Za-z0-9_-]+', '[TEMP_MATPLOTLIB_CACHE]', sanitized)
        check('ledger-exact-path-redaction:' + item['derivative_relative'], sanitized == destination.read_text())
check('ledger-generated-file-boundary', set(file_set(EXPORT)) - mapped == {'REPORT.md', 'entry-gates-summary.json', 'completion.json', 'transformation-ledger.json', 'manifest.json'})
archive = BASE / 'P1-result-review.tar.gz'
with tarfile.open(archive, 'r:gz') as tar:
    members = tar.getmembers()
    check('archive-55-complete-members', len(members) == 55 and {m.name for m in members} == set(file_set(EXPORT)))
    for member in members:
        name = PurePosixPath(member.name)
        check('archive-member:' + member.name, member.isfile() and not name.is_absolute() and '..' not in name.parts and not any([member.uid, member.gid, member.uname, member.gname, member.mtime]) and tar.extractfile(member).read() == (EXPORT / member.name).read_bytes())

patterns = {
    'private-path': rb'/(?:home|Users|workspace)/',
    'temporary-cache-path': rb'/tmp/matplotlib-',
    'private-environment-id': rb'ccarenv_',
    'credential-like': rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)',
    'recorded-account-window-values': rb'"included_windows_consumed_fraction"\s*:\s*\[',
}
sanitation_findings = []
npz_members = 0
for relative in file_set(EXPORT):
    path = EXPORT / relative
    payloads = [(relative, path.read_bytes())]
    if path.suffix == '.npz':
        with zipfile.ZipFile(path) as zipped:
            for member in zipped.infolist():
                npz_members += 1
                check('npz-safe-member:' + member.filename, '/' not in member.filename and '\\' not in member.filename and not member.comment)
                payloads.append((relative + ':' + member.filename, zipped.read(member)))
    for name, payload in payloads:
        for label, pattern in patterns.items():
            if re.search(pattern, payload):
                sanitation_findings.append({'file': name, 'pattern': label})
        try:
            text = payload.decode('utf-8')
        except UnicodeDecodeError:
            continue
        if re.search(r'[\u3400-\u4dbf\u4e00-\u9fff]', text):
            sanitation_findings.append({'file': name, 'pattern': 'Han-text'})
check('bounded-sanitation-scan', not sanitation_findings)

log = (RAW / 'calculation.log').read_text()
log_findings = {'handled_runtime_home_permission_message': 'Read-only file system' in log, 'temporary_Matplotlib_fallback_logged': 'Matplotlib created a temporary cache directory' in log, 'Fontconfig_error_message_logged': 'Fontconfig error: No writable cache directories' in log, 'traceback_logged': 'Traceback (most recent call last)' in log, 'recorder_controller_exception_files_present': (RAW / 'failure-private.txt').exists() or (DATA / 'failure.txt').exists()}
check('handled-cache-messages-not-recorder-exception', all(log_findings[key] for key in ['handled_runtime_home_permission_message', 'temporary_Matplotlib_fallback_logged', 'Fontconfig_error_message_logged']) and not log_findings['traceback_logged'] and not log_findings['recorder_controller_exception_files_present'])
preservation_after = {label: file_set(root) for label, root in [('raw', RAW), ('export', EXPORT), ('frozen', FROZEN)]}
preservation_after['external'] = {'archive': sha(archive), 'attempt_token': sha(TOKEN)}
check('all-originals-preserved-during-review', preservation_before == preservation_after)

report = {'scope': 'Independent saved-evidence arithmetic and integrity only; no frozen source execution, model construction, model inference, installation, account/remote access, publication or scheduling', 'passed': all(item['passed'] for item in checks), 'check_count': len(checks), 'checks': checks, 'counts': counts, 'numerical_summary': summary, 'model_tensor_keys': sorted(model), 'model_parameter_records': len(read(DATA / 'model-tensor-hashes.json')), 'runtime_fields_differing_from_C1': different_runtime_fields, 'execution': execution, 'capture_summary': capture, 'reporting_elapsed_seconds': elapsed_reporting, 'ledger_actions': ledger_actions, 'archive_members': len(members), 'NPZ_members_inspected': npz_members, 'sanitation_findings': sanitation_findings, 'log_findings': log_findings, 'identities': {name: sha(FROZEN / name) for name in ['PROTOCOL.md', 'protocol.json', 'implementation-manifest.json', 'control.py', 'guarded_recorder.py', 'freeze.json']}, 'artifact_identities': {'REPORT.md': {'bytes': len((EXPORT / 'REPORT.md').read_bytes()), 'characters': len((EXPORT / 'REPORT.md').read_text()), 'sha256': sha(EXPORT / 'REPORT.md')}, 'export_manifest_sha256': sha(EXPORT / 'manifest.json'), 'archive_sha256': sha(archive), 'raw_manifest_sha256': sha(RAW / 'manifest-private.json'), 'decision_sha256': sha(RAW / 'decision.json')}, 'limitations': ['One retained token and recorded forward establish one recorded authorized invocation, not a universal proof about all historical machine activity', 'Private release/account records were digest-checked through the raw manifest but their account fields were not inspected or independently verified', 'Stored parameter hashes were compared; full parameter tensors were not present for independent rehashing', 'Sanitation is bounded pattern/archive/ledger inspection of this review derivative, not publication authorization or a full new integrated release audit']}
write('verification.json', report)
print(json.dumps({key: report[key] for key in ['passed', 'check_count', 'counts', 'ledger_actions', 'archive_members', 'NPZ_members_inspected', 'sanitation_findings', 'log_findings', 'artifact_identities']}))
