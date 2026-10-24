"""Future single-evaluation controller. Import is inert; no execution is authorized now."""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import time
import traceback
from contextlib import contextmanager

PUBLIC_URL = 'https://github.com/CPTM511/matterlab.git'
PUBLIC_COMMIT = '91147ff73336ce205717117b2ab7de3e62c5fdb1'
PROTOCOL_ID = 'P1-default-repeat-20261024'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def parse_utc(value):
    stamp = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if stamp.utcoffset() != dt.timedelta(0):
        raise ValueError('Expected explicit UTC timestamp')
    return stamp

def verify_release(release, freeze, now):
    required_true = ['parent_released_exact_protocol', 'ordinary_included_use_allowed', 'all_displayed_windows_recorded', 'usage_unambiguous', 'current_cloud_ownership', 'no_other_physical_job', 'fallback_nonoverlap_verified', 'single_existing_schedule_verified']
    if any(release.get(key) is not True for key in required_true):
        raise ValueError('Missing explicit release, usage or ownership attestation')
    if release.get('protocol_sha256') != freeze['protocol_sha256'] or release.get('implementation_manifest_sha256') != freeze['implementation_manifest_sha256']:
        raise ValueError('Release is not for this exact reviewed protocol/implementation')
    if release.get('remote_head') != PUBLIC_COMMIT:
        raise ValueError('Release coordination head differs')
    for key in ['usage_observed_at_utc', 'ownership_checked_at_utc']:
        age = (now - parse_utc(release[key])).total_seconds()
        if not 0 <= age <= 900:
            raise ValueError('Usage/ownership observation is not within15minutes')
    windows = release.get('included_windows_consumed_fraction')
    if not isinstance(windows, list) or not windows:
        raise ValueError('No included windows supplied')
    if any(type(x) not in (int, float) or not 0 <= x < 0.8 for x in windows):
        raise ValueError('Included window unavailable/ambiguous/at reserve')
    if release.get('extra_spending_allowed') is not False:
        raise ValueError('Zero-extra-spend restriction absent')
    start = parse_utc(release['investigation_started_at_utc'])
    if not 0 <= (now - start).total_seconds() < 1800:
        raise ValueError('Investigation budget expired or invalid')
    return start

def claim_attempt(path, evidence):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(evidence, stream, indent=2)

def finalize_decision(decision, calculation, analysis_record):
    """Keep numerical analysis separate from final process/resource eligibility."""
    result = dict(decision)
    def bounded_number(value, maximum):
        return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= maximum
    execution_ok = (calculation.get('completed') is True
                    and type(calculation.get('attempts')) is int and calculation['attempts'] == 1
                    and type(calculation.get('returncode')) is int
                    and calculation['returncode'] == 0
                    and calculation.get('investigation_limit_respected') is True
                    and bounded_number(calculation.get('wall_seconds'), 600)
                    and bounded_number(calculation.get('investigation_elapsed_seconds'), 1800)
                    and 'failure_type' not in calculation
                    and type(analysis_record.get('returncode')) is int
                    and analysis_record['returncode'] == 0
                    and 'failure_type' not in analysis_record)
    result['execution_and_resource_gate_passed'] = execution_ok
    if not execution_ok:
        result.update(primary_repeat_passed=False, outcome='inconclusive_execution_analysis_or_resource_gate_failed',
                      reason='The saved numerical analysis is retained separately; incomplete execution, analysis, or elapsed-time limits cannot yield protocol acceptance.')
    return result

def kill_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    proc.wait(timeout=5)

class TerminationRequested(BaseException):
    pass

@contextmanager
def termination_handlers():
    def stop(signum, _frame):
        raise TerminationRequested('Termination signal ' + str(signum))
    previous = {sig: signal.signal(sig, stop) for sig in [signal.SIGTERM, signal.SIGHUP, signal.SIGINT]}
    try:
        yield
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)

def run_bounded(command, *, seconds, env, cwd, log, record=None):
    if seconds <= 0:
        raise TimeoutError('No process budget remains')
    start = time.monotonic()
    status = record if record is not None else {}
    status.update(started_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(), requested_timeout_seconds=seconds)
    proc = None
    try:
        with termination_handlers():
            proc = subprocess.Popen(command, env=env, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = proc.wait(timeout=max(0, seconds - (time.monotonic() - start)))
                try:
                    os.killpg(proc.pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    kill_group(proc)
                    raise RuntimeError('Unexpected surviving process group after leader exit')
                status['returncode'] = code
            except BaseException:
                blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM, signal.SIGHUP, signal.SIGINT})
                try:
                    kill_group(proc)
                finally:
                    signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
                raise
    except BaseException as error:
        status.update(failure_type=type(error).__name__, timeout=isinstance(error, subprocess.TimeoutExpired))
        raise
    finally:
        status.update(wall_seconds=time.monotonic() - start, ended_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(), returncode=proc.returncode if proc else None)
    return status

def remote_head(root, timeout):
    if timeout <= 0:
        raise TimeoutError('No budget for coordination check')
    line = subprocess.check_output(['git', '-C', str(root), 'ls-remote', PUBLIC_URL, 'refs/heads/main'], text=True, timeout=min(30, timeout)).strip()
    if len(line.split()) != 2 or line.split()[0] != PUBLIC_COMMIT:
        raise ValueError('Remote advanced or cannot establish current ownership')

def local_coordination(root, timeout):
    if timeout <= 0:
        raise TimeoutError('No budget for local coordination check')
    def git(*arguments):
        return subprocess.check_output(['git', '-C', str(root), *arguments], text=True, timeout=min(10, timeout)).strip()
    if git('rev-parse', 'HEAD') != PUBLIC_COMMIT or git('status', '--porcelain'):
        raise ValueError('Local public checkout changed or is dirty')
    if sha(root / 'project/STATE.json') != '53efd602837a504fe080db51d2313d10de67951cbeff96cdda2bfe5cc25601f4':
        raise ValueError('Public coordination state changed')
    state = read(root / 'project/STATE.json')
    if state.get('active_work') != [] or any(value.get('physical_job_active') is not False for value in state.values() if isinstance(value, dict) and 'physical_job_active' in value):
        raise ValueError('Public state records active or uncertain work')

def verify_bundle(bundle, freeze):
    if sha(bundle / 'protocol.json') != freeze['protocol_sha256'] or sha(bundle / 'implementation-manifest.json') != freeze['implementation_manifest_sha256']:
        raise ValueError('Frozen protocol/implementation manifest changed')
    for name, digest in read(bundle / 'implementation-manifest.json')['files'].items():
        file = (bundle / name).resolve()
        if not file.is_relative_to(bundle) or sha(file) != digest:
            raise ValueError('Implementation file changed: ' + name)
    if sha(bundle / 'PROTOCOL.md') != read(bundle / 'protocol.json')['protocol_markdown_sha256']:
        raise ValueError('Frozen English protocol changed')

def check_live_processes(output):
    snapshot = subprocess.check_output(['ps', '-eo', 'pid,ppid,stat,args'], text=True, timeout=10)
    (output / 'processes-private.txt').write_text(snapshot)
    terms = ['diagnostic_eval_proposed.py', 'guarded_recorder.py', 'matterlab run', 'torchrun', 'pw.x']
    for line in snapshot.splitlines()[1:]:
        fields = line.split(None, 3)
        if len(fields) == 4 and int(fields[0]) != os.getpid() and not fields[2].startswith('Z') and any(term in fields[3] for term in terms):
            raise ValueError('Potential overlapping calculation process; inspect instead of ignoring')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--execute-once', action='store_true', required=True)
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    freeze = read(bundle / 'freeze.json')
    if freeze['status'] != 'reviewed_for_parent_release' or freeze['execution_release_required'] is not True:
        raise ValueError('Not a reviewed executable freeze')
    verify_bundle(bundle, freeze)
    release = read(args.release)
    started = verify_release(release, freeze, dt.datetime.now(dt.timezone.utc))
    root, output = args.root.resolve(), args.output.resolve()
    if output == root or output.is_relative_to(root) or output.is_relative_to(bundle):
        raise ValueError('Output must be new and outside source/frozen implementation')
    guard = bundle.parent / 'execution-guard' / (PROTOCOL_ID + '.attempt.json')
    claim_attempt(guard, {'protocol_sha256': freeze['protocol_sha256'], 'started_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'output_private': str(output), 'maximum_evaluations': 1})
    output.mkdir(parents=True, exist_ok=False)
    save(output / 'release-private.json', release)
    save(output / 'freeze.json', freeze)
    implementation = output / 'implementation'
    implementation.mkdir()
    for name in set(read(bundle / 'implementation-manifest.json')['files']) | {'PROTOCOL.md', 'protocol.json', 'implementation-manifest.json', 'freeze.json'}:
        target = implementation / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bundle / name, target)
    environment = dict(os.environ)
    for name in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS']:
        environment[name] = '1'
    environment.pop('MKL_CBWR', None)
    environment.update(ATEN_CPU_CAPABILITY='default', PYTHONHASHSEED='20261024', PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(root / 'src'), MATTERLAB_ROOT=str(root), MATTERLAB_EXPECTED_CODE=str(root / 'evidence/restoration-20261023/replay/code.json'), MATTERLAB_CONDITION=PROTOCOL_ID)
    calculation = {'attempts': 0, 'completed': False, 'timeout': False}
    pre = {}
    def remaining():
        return 1800 - (dt.datetime.now(dt.timezone.utc) - started).total_seconds()
    try:
        remote_head(root, remaining())
        local_coordination(root, remaining())
        check_live_processes(output)
        with (output / 'preflight.log').open('wb') as log:
            run_bounded([sys.executable, str(bundle / 'child_entry.py'), str(os.getpid()), 'preflight', str(root), str(output)], seconds=max(0, remaining() - 6), env=environment, cwd=output, log=log, record=pre)
        save(output / 'preflight-execution.json', pre)
        if pre['returncode'] != 0:
            raise ValueError('Preflight failed; no inference')
        remote_head(root, remaining())
        local_coordination(root, remaining())
        check_live_processes(output)
        verify_bundle(bundle, freeze)
        launch_release = read(args.release)
        verify_release(launch_release, freeze, dt.datetime.now(dt.timezone.utc))
        if launch_release['investigation_started_at_utc'] != release['investigation_started_at_utc']:
            raise ValueError('Investigation start cannot be reset by a refreshed gate')
        save(output / 'launch-release-private.json', launch_release)
        # Independent fixed token inside the only allowed output prevents an accidental second child launch.
        claim_attempt(output / 'INFERENCE-ATTEMPT.json', {'maximum_evaluations': 1})
        command = [sys.executable, str(bundle / 'child_entry.py'), str(os.getpid()), 'inference', str(root), str(output)]
        budget = min(600, remaining()) - 6
        if budget <= 0:
            raise TimeoutError('No launch margin remains')
        calculation.update(attempts=1, started_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(), requested_timeout_seconds=budget)
        with (output / 'calculation.log').open('wb') as log:
            result = run_bounded(command, seconds=budget, env=environment, cwd=output, log=log, record=calculation)
        calculation.update(result, completed=True)
        if result['returncode'] != 0:
            raise RuntimeError('Recorder stopped; no retry')
    except BaseException as error:
        calculation.update(timeout=isinstance(error, (TimeoutError, subprocess.TimeoutExpired)), failure_type=type(error).__name__)
        (output / 'failure-private.txt').write_text(traceback.format_exc())
    finally:
        calculation['ended_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        calculation['investigation_elapsed_seconds'] = (dt.datetime.now(dt.timezone.utc) - started).total_seconds()
        save(output / 'preflight-execution.json', pre)
        save(output / 'execution.json', calculation)
        # Saved-data analysis is a separate bounded metadata process, never another inference.
        try:
            analysis_record = {}
            with (output / 'analysis.log').open('wb') as log:
                run_bounded([sys.executable, str(bundle / 'child_entry.py'), str(os.getpid()), 'analyze', str(root), str(output)], seconds=max(0, remaining() - 1), env=environment, cwd=output, log=log, record=analysis_record)
        except BaseException:
            (output / 'analysis-failure-private.txt').write_text(traceback.format_exc())
        finally:
            save(output / 'analysis-execution.json', analysis_record)
            if not (output / 'decision.json').exists():
                save(output / 'decision.json', {'primary_repeat_passed': False, 'outcome': 'inconclusive_analysis_unavailable', 'reason': 'Analysis exception or exhausted investigation budget; raw artifacts retained, missing comparisons not reconstructed', 'original_baseline_acceptance': None, 'old_C1_gate': 'FAILED; unchanged', 'old_C2': 'not run'})
            calculation['investigation_elapsed_seconds'] = (dt.datetime.now(dt.timezone.utc) - started).total_seconds()
            calculation['investigation_limit_respected'] = calculation['investigation_elapsed_seconds'] <= 1800
            save(output / 'execution.json', calculation)
            analyzed = read(output / 'decision.json')
            save(output / 'analysis-decision.json', analyzed)
            save(output / 'decision.json', finalize_decision(analyzed, calculation, analysis_record))
        save(output / 'manifest-private.json', {'algorithm': 'SHA256', 'files': {str(f.relative_to(output)): sha(f) for f in sorted(output.rglob('*')) if f.is_file() and f.name != 'manifest-private.json'}})
    decision = read(output / 'decision.json') if (output / 'decision.json').exists() else {}
    return 0 if calculation['completed'] and calculation.get('returncode') == 0 and calculation.get('investigation_limit_respected') and decision.get('primary_repeat_passed') else 1

if __name__ == '__main__':
    raise SystemExit(main())
