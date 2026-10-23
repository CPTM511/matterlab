#!/usr/bin/env python3
"""Create or audit a clean, English public tree. Never publishes or changes Git."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '__pycache__', '.pytest_cache', '.cache', '.venv', '.tools', 'scratch'}
HAN = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\U00020000-\U000323af]')
PRIVATE_PATH = re.compile(rb'/(?:Users|home)/[A-Za-z0-9_.-]+')
SECRET = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
MANIFEST = Path('publication/manifest.json')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n')


def confined(root: Path, relative: str) -> Path:
    name = PurePosixPath(relative)
    if name.is_absolute() or '..' in name.parts or not name.parts:
        raise ValueError('Unsafe relative path')
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path escapes the project')
    return path


def files(root: Path, strict: bool = False):
    if not root.is_dir():
        raise ValueError(f'Required source directory is missing: {root.name}')
    for path in sorted(root.rglob('*')):
        parts = path.relative_to(root).parts
        if '.git' in parts:
            continue
        excluded = any(part in EXCLUDED or part.endswith('.egg-info') for part in parts)
        excluded = excluded or path.suffix in {'.pyc', '.tmp'}
        if excluded:
            if strict:
                raise ValueError(f'Unreviewed excluded content in public tree: {path.relative_to(root)}')
            continue
        if path.is_symlink():
            raise ValueError(f'Symbolic link is not allowed: {path.relative_to(root)}')
        if path.is_file() and path.suffix not in {'.pyc', '.tmp'}:
            yield path


def check_content(data: bytes, name: str) -> None:
    if PRIVATE_PATH.search(data) or SECRET.search(data):
        raise ValueError(f'Private path or credential-like content: {name}')
    try:
        decoded = data.decode('utf-8')
    except UnicodeDecodeError:
        return
    if HAN.search(decoded):
        raise ValueError(f'Non-English Han text in public content: {name}')


def evidence_hashes(root: Path) -> int:
    config = json.loads((root / 'configs/publication.json').read_text())
    expected = set(config['campaigns'] + config['reproductions'])
    actual = {p.name for p in (root / 'runs').iterdir() if p.is_dir() and p.name != 'quantum'}
    if actual != expected:
        raise ValueError('Required evidence directory coverage differs from publication config')
    checked = 0
    for name in sorted(expected):
        run = confined(root / 'runs', name)
        required_record = 'summary.json' if name in config['campaigns'] else 'reproduction.json'
        if not (run / required_record).is_file():
            raise ValueError(f'Required evidence record is missing: {name}/{required_record}')
        manifest = run / 'manifest.json'
        for name, expected in json.loads(manifest.read_text())['files'].items():
            path = confined(manifest.parent, name)
            if sha(path.read_bytes()) != expected:
                raise ValueError(f'Evidence hash mismatch: {manifest.parent.name}/{name}')
            checked += 1
    quantum = root / 'runs/quantum/manifest.sha256'
    for line in quantum.read_text().splitlines():
        expected, name = line.split('  ', 1)
        if sha(confined(root, name).read_bytes()) != expected:
            raise ValueError(f'Quantum hash mismatch: {name}')
        checked += 1
    return checked


def audit(root: Path, check_manifest: bool = True) -> dict:
    root = root.resolve()
    count = archive_members = 0
    actual = {}
    for path in files(root, strict=True):
        name = path.relative_to(root).as_posix()
        data = path.read_bytes()
        check_content(name.encode(), name)
        check_content(data, name)
        if name.endswith('.tar.gz'):
            with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
                for member in archive.getmembers():
                    member_path = PurePosixPath(member.name)
                    if not member.isfile() or member_path.is_absolute() or '..' in member_path.parts:
                        raise ValueError(f'Unsafe archive member: {name}')
                    if member.uid or member.gid or member.uname or member.gname or member.mtime:
                        raise ValueError(f'Unnormalized archive metadata: {name}')
                    check_content(member.name.encode(), name)
                    check_content(archive.extractfile(member).read(), name + ':' + member.name)
                    archive_members += 1
        if Path(name) != MANIFEST:
            actual[name] = sha(data)
        count += 1
    evidence_checks = evidence_hashes(root)
    if check_manifest:
        expected = json.loads((root / MANIFEST).read_text())['files']
        if actual != expected:
            raise ValueError('Publication manifest differs from the complete public file set')
    return {'passed': True, 'files_checked': count, 'archive_members_checked': archive_members,
            'evidence_hashes_checked': evidence_checks,
            'checks': ['English Han-text guard', 'home-path and credential-pattern scan',
                       'archive metadata and payload inspection', 'saved evidence hash verification'],
            'scope': 'Release integrity and bounded pattern checks; human review remains required.'}


def copy(source: Path, target: Path) -> None:
    if source.is_symlink():
        raise ValueError('Source symbolic links are not allowed')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def export(output: Path) -> dict:
    from export_quantum_public import export as quantum_export
    output = output.resolve()
    if output.exists() or ROOT.is_relative_to(output) or output.is_relative_to(ROOT / 'runs'):
        raise ValueError('Use a new staging directory outside original evidence')
    config = json.loads((ROOT / 'configs/publication.json').read_text())
    output.mkdir(parents=True)
    for name in config['files']:
        copy(confined(ROOT, name), confined(output, name))
    for name in config['directories']:
        base = confined(ROOT, name)
        for path in files(base):
            copy(path, output / name / path.relative_to(base))
    for name in config['campaigns'] + config['reproductions']:
        base = confined(ROOT / 'runs', name)
        for path in files(base):
            copy(path, output / 'runs' / name / path.relative_to(base))
    index = []
    for name in config['campaigns']:
        summary = json.loads((output / 'runs' / name / 'summary.json').read_text())
        index.append({'run_id': name, 'path': f'/runs/{name}/summary.json',
                      'created_at': summary['created_at']})
    write_json(output / 'runs/index.json', index)
    quantum_export(output)
    report = audit(output, check_manifest=False)
    write_json(output / 'publication/audit.json', report)
    write_json(output / MANIFEST, {
        'algorithm': 'SHA256',
        'scope': 'Every public project file except this manifest and excluded installation/Git caches.',
        'quantum_derivative_ledger': 'runs/quantum/public-transformation.json',
        'files': {p.relative_to(output).as_posix(): sha(p.read_bytes()) for p in files(output)}
    })
    return audit(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--output', type=Path, help='Create a new clean public tree from original evidence')
    group.add_argument('--audit', type=Path, help='Audit an existing export, including publication hashes')
    args = parser.parse_args()
    try:
        result = export(args.output) if args.output else audit(args.audit)
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError, tarfile.TarError) as exc:
        parser.exit(1, f'Publication failed: {exc}\n')


if __name__ == '__main__':
    main()
