"""Release guards: exercise tampered and unsafe publication inputs."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile

import pytest

spec = importlib.util.spec_from_file_location('matterlab_publication', Path(__file__).resolve().parents[1] / 'tools/export_public.py')
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)


@pytest.fixture
def public_tree(tmp_path):
    run = tmp_path / 'runs/example'
    run.mkdir(parents=True)
    (run / 'measurement.txt').write_text('energy = -1.25 eV\n')
    digest = hashlib.sha256((run / 'measurement.txt').read_bytes()).hexdigest()
    (run / 'manifest.json').write_text(json.dumps({'files': {'measurement.txt': digest}}))
    (run / 'summary.json').write_text('{}')
    (tmp_path / 'configs').mkdir()
    (tmp_path / 'configs/publication.json').write_text(json.dumps({'campaigns': ['example'], 'reproductions': []}))
    quantum = tmp_path / 'runs/quantum'
    quantum.mkdir()
    (quantum / 'manifest.sha256').write_text('')
    return tmp_path


def test_modified_measurement_is_rejected(public_tree):
    assert publication.audit(public_tree, check_manifest=False)['passed']
    (public_tree / 'runs/example/measurement.txt').write_text('energy = -9.99 eV\n')
    with pytest.raises(ValueError, match='Evidence hash mismatch'):
        publication.audit(public_tree, check_manifest=False)


def test_manifest_cannot_read_outside_release(public_tree):
    (public_tree / 'runs/example/manifest.json').write_text(json.dumps({'files': {'../../../outside': '0' * 64}}))
    with pytest.raises(ValueError, match='Unsafe relative path'):
        publication.audit(public_tree, check_manifest=False)


@pytest.mark.parametrize('payload', [chr(0x4e2d), '/'+ 'Users' + '/private-user/project', 'gh' + 'p_' + 'a' * 36])
def test_release_rejects_language_paths_and_credentials(public_tree, payload):
    (public_tree / 'README.md').write_text(payload)
    with pytest.raises(ValueError, match='Non-English|Private path'):
        publication.audit(public_tree, check_manifest=False)


def test_nested_archive_text_is_inspected(public_tree):
    content = ('/' + 'home' + '/private-user/file').encode()
    member = tarfile.TarInfo('state.xml')
    member.size = len(content)
    with tarfile.open(public_tree / 'density.tar.gz', 'w:gz') as archive:
        archive.addfile(member, io.BytesIO(content))
    with pytest.raises(ValueError, match='Private path'):
        publication.audit(public_tree, check_manifest=False)


def test_publication_manifest_rejects_extra_file(public_tree):
    target = public_tree / 'publication/manifest.json'
    target.parent.mkdir()
    files = {p.relative_to(public_tree).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in public_tree.rglob('*') if p.is_file()}
    target.write_text(json.dumps({'files': files}))
    assert publication.audit(public_tree)['passed']
    (public_tree / 'unexpected.txt').write_text('Unreviewed addition')
    with pytest.raises(ValueError, match='complete public file set'):
        publication.audit(public_tree)


@pytest.mark.parametrize('relative', ['scratch/private.txt', 'private.tmp', 'tools/__pycache__/private.txt'])
def test_excluded_content_cannot_hide_from_audit(public_tree, relative):
    path = public_tree / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('Unreviewed content')
    with pytest.raises(ValueError, match='Unreviewed excluded content'):
        publication.audit(public_tree, check_manifest=False)


def test_missing_required_reproduction_fails(public_tree):
    config = public_tree / 'configs/publication.json'
    config.write_text(json.dumps({'campaigns': ['example'], 'reproductions': ['missing-replay']}))
    with pytest.raises(ValueError, match='directory coverage'):
        publication.audit(public_tree, check_manifest=False)


def test_missing_source_directory_fails(tmp_path):
    with pytest.raises(ValueError, match='Required source directory'):
        list(publication.files(tmp_path / 'missing'))
