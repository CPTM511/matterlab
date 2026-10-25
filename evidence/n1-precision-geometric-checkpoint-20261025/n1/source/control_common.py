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
PUBLIC_COMMIT = 'c3c089ff893dda65d12713aea49d9a17a08991be'
PROTOCOL_ID = 'N1-native-reference-curvature-20261024'

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
    if sha(root / 'project/STATE.json') != 'c7263cda244600a591ef0f0921a02eafc89c12e0ba4629038471178768efffc7':
        raise ValueError('Public coordination state changed')
    state = read(root / 'project/STATE.json')
    if state.get('active_work') != [] or any(value.get('physical_job_active') is not False for value in state.values() if isinstance(value, dict) and 'physical_job_active' in value):
        raise ValueError('Public state records active or uncertain work')

def verify_bundle(bundle, freeze):
    if sha(bundle / 'protocol.json') != freeze['protocol_sha256'] or sha(bundle / 'implementation-manifest.json') != freeze['implementation_manifest_sha256']:
        raise ValueError('Frozen protocol/implementation manifest changed')
    declared=read(bundle / 'implementation-manifest.json')['files']
    actual={str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file()}
    if actual != set(declared)|{'protocol.json','implementation-manifest.json','freeze.json'}:
        raise ValueError('Unexpected or missing frozen bundle file')
    for name, digest in declared.items():
        file = (bundle / name).resolve()
        if not file.is_relative_to(bundle) or sha(file) != digest:
            raise ValueError('Implementation file changed: ' + name)
    if sha(bundle / 'PROTOCOL.md') != read(bundle / 'protocol.json')['protocol_markdown_sha256']:
        raise ValueError('Frozen English protocol changed')

def check_live_processes(output):
    snapshot = subprocess.check_output(['ps', '-eo', 'pid,ppid,stat,args'], text=True, timeout=10)
    (output / 'processes-private.txt').write_text(snapshot)
    terms = ['diagnostic_eval_proposed.py', 'guarded_recorder.py', 'matterlab run', 'torchrun', 'pw.x', 'gamma_worker.py', 'run_gamma.py', 'native_worker.py', 'run_native.py', 'native_child.py']
    for line in snapshot.splitlines()[1:]:
        fields = line.split(None, 3)
        if len(fields) == 4 and int(fields[0]) != os.getpid() and not fields[2].startswith('Z') and any(term in fields[3] for term in terms):
            raise ValueError('Potential overlapping calculation process; inspect instead of ignoring')

