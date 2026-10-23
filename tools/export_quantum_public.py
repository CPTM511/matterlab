#!/usr/bin/env python3
"""Export a traceable public derivative of immutable local quantum evidence.

No solver, network, or package-installation commands are executed. Run this
from the original project after copying project source files into staging.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'runs/quantum'
TEXT_SUFFIXES = {'.in', '.out', '.json', '.xml', '.log', '.txt', '.sha256', '.EXIT'}
HOME_PATTERN = re.compile(r'(?<![A-Za-z0-9:/])/(?:Users|home)/[^/\s<>"\']+')
NUMBER_PATTERN = re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def portable(text: str) -> str:
    text = text.replace(str(ROOT), '${PROJECT_ROOT}')
    text = text.replace(str(Path.home()), '${HOME}')
    return HOME_PATTERN.sub('${HOME}', text)


def assert_portable(text: str) -> None:
    if str(ROOT) in text or str(Path.home()) in text or HOME_PATTERN.search(text):
        raise ValueError('An absolute home/workspace path remains in exported text')


def xml_numbers(data: bytes) -> list:
    values = []
    for node in ET.fromstring(data).iter():
        for key, value in [('text', node.text), *node.attrib.items()]:
            tokens = (value or '').split()
            if tokens and all(NUMBER_PATTERN.fullmatch(token) for token in tokens):
                values.append((node.tag, key, tokens))
    return values


def export_archive(data: bytes) -> tuple[bytes, list[dict]]:
    members = []
    payload = io.BytesIO()
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as source:
        with gzip.GzipFile(fileobj=payload, mode='wb', filename='', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as target:
                for member in source.getmembers():
                    path = PurePosixPath(member.name)
                    if path.is_absolute() or '..' in path.parts or not member.isfile():
                        raise ValueError('Density archive contains an unsupported or unsafe member')
                    original = source.extractfile(member).read()
                    exported = original
                    operations = ['normalize archive ownership, permissions, and timestamps']
                    if path.suffix in {'.xml', '.txt'}:
                        exported = portable(original.decode('utf-8')).encode()
                        assert_portable(exported.decode())
                        if exported != original:
                            operations.append('replace absolute paths with portable placeholders')
                        if path.suffix == '.xml' and xml_numbers(original) != xml_numbers(exported):
                            raise ValueError('An embedded XML numerical field changed')
                    else:
                        operations.append('preserve binary payload bytes exactly')
                    clean = tarfile.TarInfo(member.name)
                    clean.size = len(exported)
                    clean.mode = 0o644
                    clean.uid = clean.gid = 0
                    clean.uname = clean.gname = ''
                    clean.mtime = 0
                    target.addfile(clean, io.BytesIO(exported))
                    members.append({'path': member.name, 'original_sha256': digest(original),
                                    'exported_sha256': digest(exported), 'operations': operations})
    result = payload.getvalue()
    with tarfile.open(fileobj=io.BytesIO(result), mode='r:gz') as check:
        for member, recorded in zip(check.getmembers(), members, strict=True):
            if member.uid or member.gid or member.uname or member.gname or member.mtime:
                raise ValueError('Archive metadata normalization failed')
            actual = check.extractfile(member).read()
            if digest(actual) != recorded['exported_sha256']:
                raise ValueError('Archive payload integrity check failed')
            if member.name.endswith('.hdf5') and digest(actual) != recorded['original_sha256']:
                raise ValueError('Binary density payload changed')
    return result, members


def validate_records(directory: Path) -> dict:
    records = []
    for path in sorted(directory.glob('catio3-cubic-*/summary.json')):
        summary = json.loads(path.read_text())
        for filename, key in [('input.in', 'input_sha256'), ('output.out', 'output_sha256')]:
            if digest((path.parent / filename).read_bytes()) != summary[key]:
                raise ValueError(f'{path.parent.name}: recorded {filename} hash mismatch')
        output = (path.parent / 'output.out').read_text()
        converged = bool(re.search(r'convergence has been achieved in\s+\d+ iterations', output))
        if converged != summary['scf_converged'] or ('JOB DONE.' in output) != summary['job_done']:
            raise ValueError(f'{path.parent.name}: raw output and summary disagree')
        energy = re.findall(r'!\s+total energy\s+=\s+([-\d.]+)\s+Ry', output)
        if summary['total_energy_Ry'] is not None:
            if not energy or not math.isfinite(summary['total_energy_Ry']) or float(energy[-1]) != summary['total_energy_Ry']:
                raise ValueError(f'{path.parent.name}: raw energy and summary disagree')
        xml_path = path.parent / 'data-file-schema.xml'
        if xml_path.exists():
            xml = ET.parse(xml_path).getroot()
            xml_converged = xml.find('.//scf_conv/convergence_achieved')
            if xml_converged is None or ((xml_converged.text or '').strip() == 'true') != converged:
                raise ValueError(f'{path.parent.name}: XML convergence and raw output disagree')
            if summary['total_energy_Ry'] is not None:
                etot = xml.find('.//total_energy/etot')
                if etot is None or not math.isfinite(float(etot.text)) or abs(2 * float(etot.text) - summary['total_energy_Ry']) > 1e-7:
                    raise ValueError(f'{path.parent.name}: XML energy and raw output disagree')
        accepted = summary['returncode'] == 0 and summary['job_done'] and converged
        records.append({'run': path.parent.name, 'accepted': accepted,
                        'returncode': summary['returncode'], 'scf_converged': converged,
                        'total_energy_Ry': summary['total_energy_Ry']})
    if not records:
        raise ValueError('No quantum run summaries found')
    return {'recorded_runs': len(records), 'accepted_runs': sum(r['accepted'] for r in records),
            'unaccepted_runs': sum(not r['accepted'] for r in records), 'records': records}


def export(output: Path) -> dict:
    output = output.resolve()
    if output == ROOT or ROOT.is_relative_to(output) or output.is_relative_to(SOURCE):
        raise ValueError('Output must be a separate staging project, not original evidence or its ancestor')
    if not output.is_dir() or not (output / 'tools/quantum/verify_evidence.py').is_file():
        raise ValueError('Copy project source files to the staging root before export')
    source_files = sorted(p for p in SOURCE.rglob('*') if p.is_file() and 'scratch' not in p.relative_to(SOURCE).parts)
    if (SOURCE / 'public-transformation.json').exists():
        raise ValueError('Export from the original evidence project, not an already published derivative')
    if any(p.is_symlink() for p in SOURCE.rglob('*') if 'scratch' not in p.relative_to(SOURCE).parts):
        raise ValueError('Symbolic links are not supported in source evidence')
    source_hashes = {p: digest(p.read_bytes()) for p in source_files}
    source_status = validate_records(SOURCE)
    destination = output / 'runs/quantum'
    for directory in [output / 'runs', destination, output / 'docs', output / 'tools/quantum']:
        if directory.is_symlink():
            raise ValueError('Staged output directories must not be symbolic links')
    allowed = {p.relative_to(SOURCE).as_posix() for p in source_files}
    allowed |= {'historical-manifest.sha256', 'public-transformation.json', 'public-export-verification.json'}
    if destination.exists():
        for p in destination.rglob('*'):
            if p.is_symlink() or (p.is_file() and p.relative_to(destination).as_posix() not in allowed):
                raise ValueError('Staged quantum directory contains unexpected files; use clean staging')
    destination.mkdir(parents=True, exist_ok=True)
    transformations = []
    for source in source_files:
        relative = source.relative_to(SOURCE)
        target_relative = Path('historical-manifest.sha256') if relative == Path('manifest.sha256') else relative
        target = destination / target_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        original = source.read_bytes()
        exported = original
        operations = []
        member_records = None
        if source.name.endswith('.tar.gz'):
            exported, member_records = export_archive(original)
            operations.append('repack density archive with normalized metadata and portable text paths')
        elif source.suffix in TEXT_SUFFIXES or not original:
            exported = portable(original.decode('utf-8')).encode()
            assert_portable(exported.decode())
            if exported != original:
                operations.append('replace absolute home/workspace paths with portable placeholders')
            if source.suffix == '.xml' and xml_numbers(original) != xml_numbers(exported):
                raise ValueError('An XML numerical field changed')
        else:
            raise ValueError(f'Unsupported evidence format: {relative.as_posix()}')
        if relative == Path('manifest.sha256'):
            operations.append('retain historical hash listing under a distinct filename; not the public manifest')
        target.write_bytes(exported)
        record = {'source': f'runs/quantum/{relative.as_posix()}',
                  'exported': f'runs/quantum/{target_relative.as_posix()}',
                  'original_sha256': digest(original), 'exported_sha256': digest(exported),
                  'operations': operations or ['copy bytes unchanged']}
        if member_records is not None:
            record['archive_members'] = member_records
        transformations.append(record)
    by_export = {r['exported']: r for r in transformations}
    for summary_path in sorted(destination.glob('catio3-cubic-*/summary.json')):
        summary = json.loads(summary_path.read_text())
        original_summary = dict(summary)
        summary['input_sha256'] = digest((summary_path.parent / 'input.in').read_bytes())
        summary['output_sha256'] = digest((summary_path.parent / 'output.out').read_bytes())
        summary_path.write_bytes(json_bytes(summary))
        for key in summary.keys() - {'input_sha256', 'output_sha256'}:
            if summary[key] != original_summary[key]:
                raise ValueError('A scientific or status field changed during hash refresh')
        record = by_export[summary_path.relative_to(output).as_posix()]
        source_summary = json.loads((ROOT / record['source']).read_text())
        record['original_recorded_input_sha256'] = source_summary['input_sha256']
        record['original_recorded_output_sha256'] = source_summary['output_sha256']
        record['exported_sha256'] = digest(summary_path.read_bytes())
        record['operations'].append('refresh input/output hashes to match exported derivative files')
    english = (ROOT / 'docs/quantum-validation.en.md').read_bytes()
    for filename, source_name in [('quantum-validation.md', 'quantum-validation.md'),
                                  ('quantum-validation.en.md', 'quantum-validation.en.md')]:
        target = output / 'docs' / filename
        if target.is_symlink():
            raise ValueError('Staged document must not be a symbolic link')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(english)
        transformations.append({'source': f'docs/{source_name}', 'exported': f'docs/{filename}',
                                'original_sha256': digest((ROOT / 'docs' / source_name).read_bytes()),
                                'exported_sha256': digest(english),
                                'operations': ['publish English documentation; retain original documentation locally']})
    exported_status = validate_records(destination)
    if exported_status != source_status:
        raise ValueError('Source and exported scientific/status records differ')
    report = {'schema_version': 1, **exported_status, 'source_status_identical': True,
              'input_output_hashes_verified': True, 'raw_log_xml_consistency_verified': True,
              'binary_density_payloads_unchanged': True,
              'scope': 'Evidence preservation and consistency; not physical convergence or candidate validation.'}
    (destination / 'public-export-verification.json').write_bytes(json_bytes(report))
    ledger = {'schema_version': 1, 'kind': 'public derivative of locally preserved quantum evidence',
              'placeholders': {'${PROJECT_ROOT}': 'absolute path of the original project, replaced for publication',
                               '${HOME}': 'absolute home directory path, replaced for publication'},
              'source_manifest_sha256': source_hashes[SOURCE / 'manifest.sha256'],
              'transformations': transformations,
              'generated_artifacts': ['runs/quantum/public-export-verification.json',
                                      'runs/quantum/manifest.sha256'],
              'originals_preserved': True}
    ledger_data = json_bytes(ledger)
    assert_portable(ledger_data.decode())
    (destination / 'public-transformation.json').write_bytes(ledger_data)
    manifest_files = [p for p in destination.rglob('*') if p.is_file() and p.name != 'manifest.sha256']
    manifest_files += [p for p in (output / 'tools/quantum').iterdir() if p.is_file()]
    manifest_files += [output / 'docs/quantum-validation.md', output / 'docs/quantum-validation.en.md']
    if (output / 'tools/export_quantum_public.py').is_file():
        manifest_files.append(output / 'tools/export_quantum_public.py')
    manifest = ''.join(f'{digest(p.read_bytes())}  {p.relative_to(output).as_posix()}\n'
                       for p in sorted(manifest_files))
    (destination / 'manifest.sha256').write_text(manifest)
    for p, expected in source_hashes.items():
        if digest(p.read_bytes()) != expected:
            raise ValueError('Original quantum evidence changed during export')
    return {'recorded_runs': report['recorded_runs'], 'accepted_runs': report['accepted_runs'],
            'unaccepted_runs': report['unaccepted_runs'], 'manifest_files': len(manifest_files),
            'source_status_identical': True, 'original_evidence_unchanged': True,
            'transformation_manifest': 'runs/quantum/public-transformation.json'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Existing public staging root containing copied project source')
    args = parser.parse_args()
    try:
        print(json.dumps(export(args.output), indent=2))
    except (OSError, ValueError, ET.ParseError, tarfile.TarError) as exc:
        parser.exit(1, f'Quantum export failed: {portable(str(exc))}\n')


if __name__ == '__main__':
    main()
