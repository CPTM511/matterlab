"""Future metadata/hash preflight. No model construction, forward, or physical evaluation."""
import hashlib
import importlib
import importlib.metadata as md
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

COMMIT = 'a3e3f1d8927448a2b821752fc5f8f796d1224745'
MANIFEST_SHA = '34f883ed34ead633e3e0640db78b6a9293e5881338ce2cc2de58df5956446ad2'
AUDIT_SHA = 'b2156375b9ce3fb5f5af6ae45768a6198e4e15c5c4c6bfb460e858eaaf92a661'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def load(path):
    return json.loads(path.read_text())

def cpu_identity(text):
    values = dict(line.split(':', 1) for line in text.splitlines() if ':' in line)
    names = ['Architecture', 'Vendor ID', 'Model name', 'CPU family', 'Model', 'Stepping', 'Byte Order', 'Address sizes', 'Flags']
    result = {name: values[name].strip() for name in names}
    result['Flags'] = sorted(set(result['Flags'].split()))
    return result

def main(root, output):
    checks = []
    def check(name, actual, expected):
        passed = type(actual) is type(expected) and actual == expected
        checks.append({'name': name, 'passed': passed})
        (output / 'preflight.json').write_text(json.dumps({'passed': all(c['passed'] for c in checks), 'checks': checks}, indent=2) + '\n')
        if not passed:
            raise ValueError('Preflight mismatch: ' + name)
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True, timeout=30).strip()
    check('root_commit', git('rev-parse', 'HEAD'), COMMIT)
    check('clean_source_checkout', git('status', '--porcelain'), '')
    check('public_manifest_digest', sha(root / 'publication/manifest.json'), MANIFEST_SHA)
    check('public_audit_digest', sha(root / 'publication/audit.json'), AUDIT_SHA)
    manifest = load(root / 'publication/manifest.json')['files']
    check('public_manifest_coverage', set(git('ls-files').splitlines()), set(manifest) | {'publication/manifest.json'})
    for name, digest in manifest.items():
        file = (root / name).resolve()
        check('confined:' + name, file.is_relative_to(root), True)
        check('public:' + name, sha(file), digest)
    state = load(root / 'project/STATE.json')
    check('active_work', state['active_work'], [])
    for value in state.values():
        if isinstance(value, dict) and 'physical_job_active' in value:
            check('physical_job_active', value['physical_job_active'], False)
    config = load(root / 'configs/round-001.json')
    check('seed', config['seed'], 20261024)
    check('threads', config['threads'], 1)
    check('device', config['device'], 'cpu')
    check('raw_input', sha(root / 'runs/round-001-en/generated/R-CaTiO3.cif'), sha(root / 'evidence/dispatch-contrast-20261023/C1-default/input.cif'))
    check('raw_config', sha(root / 'configs/round-001.json'), sha(root / 'evidence/dispatch-contrast-20261023/C1-default/config-original.json'))
    old = load(root / 'evidence/dispatch-contrast-20261023/environment.json')
    packages = {d.metadata['Name']: d.version for d in md.distributions()}
    check('all_dependency_versions', packages, old['packages'])
    check('python_version', sys.version, old['python'])
    check('platform', platform.platform(), old['platform'])
    prior = load(root / 'evidence/restoration-20261023/runtime-hashes.json')
    check('python_executable_digest', sha(Path(sys.executable).resolve()), prior['python_executable_sha256'])
    # Locate installed distributions without loading a model.
    chgnet = Path(md.distribution('chgnet').locate_file('chgnet'))
    for name, digest in prior['chgnet_python_sources'].items():
        check('CHGNet_source:' + name, sha(chgnet / name), digest)
    environment = load(root / 'evidence/restoration-20261023/environment-current.json')
    for name, digest in environment['model_checkpoints'].items():
        check('cached_model:' + name, sha(chgnet / name), digest)
    native = load(root / 'evidence/dispatch-contrast-20261023/installed-record-verification.json')['native_library_sha256']
    for name, digest in native.items():
        package, path = name.split(':', 1)
        check('native:' + name, sha(Path(md.distribution(package).locate_file(path))), digest)
    sources = load(root / 'evidence/restoration-20261023/replay/code.json')['sources_sha256']
    for name, digest in sources.items():
        check('matterlab_source:' + name, sha(root / name), digest)
    sys.path.insert(0, str(root / 'src'))
    import matterlab
    check('loaded_root', Path(matterlab.__file__).resolve(), (root / 'src/matterlab/__init__.py').resolve())
    for name in sources:
        if name.endswith('__main__.py'):
            continue
        module = importlib.import_module(name.removeprefix('src/').removesuffix('.py').replace('/', '.'))
        check('loaded:' + name, Path(module.__file__).resolve(), (root / name).resolve())
    check('required_cpu_available', 0 in os.sched_getaffinity(0), True)
    hardware = subprocess.check_output(['lscpu'], text=True, timeout=10)
    (output / 'cpu-private.txt').write_text(hardware)
    check('hardware_fields', cpu_identity(hardware), cpu_identity((root / 'evidence/dispatch-contrast-20261023/cpu.txt').read_text()))
    check('old_C1_gate_preserved_failed', load(root / 'evidence/dispatch-contrast-20261023/C1-default-gate.json')['comparison_assumptions_passed'], False)
    check('old_C2_absent', bool(list((root / 'evidence/dispatch-contrast-20261023').glob('C2*'))), False)
    print(json.dumps({'preflight_passed': True, 'checks': len(checks), 'model_inference_performed': False}))

if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
