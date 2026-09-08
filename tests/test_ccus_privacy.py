"""Public-file and HTTP privacy contract. Private inputs stay offline."""
import gzip
import json
from pathlib import Path
import subprocess

from apps.ccus_webinar.webinar.release import load_release_bundle, validate_manifest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'apps/ccus_webinar'
PRIVATE_FILES = {
    'data/model_contract.json', 'data/source_manifest.json',
    'data/assumptions/industrial_heat_pump.json',
    'data/assumptions/component_lifetimes.json',
    'data/assumptions/non_fossil_uptake_profiles.json',
    'data/assumptions/non_fossil_uptake_candidate.json',
    'data/assumptions/non_fossil_uptake_candidate.sha256',
    'data/runtime/system_flows_2025.json', 'data/runtime/direct_utilities_2025.json',
}


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def test_private_inputs_are_not_distributed():
    files = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', 'apps/ccus_webinar'],
        cwd=ROOT, text=True).splitlines()
    paths = [Path(n).relative_to('apps/ccus_webinar').as_posix() for n in files]
    assert not PRIVATE_FILES.intersection(paths)
    assert not any(p.startswith(('dev/', 'generated/', 'scripts/')) for p in paths)
    assert not any(p.endswith(('.xlsb', '.xlsx', '.zip', '.key')) for p in paths)


def test_public_data_has_no_private_derivations_or_physical_inventory_payload():
    manifest = json.loads((APP/'data/runtime/manifest.json').read_text())
    validate_manifest(manifest, APP)
    assert not PRIVATE_FILES.intersection(manifest['evidence_hashes'])
    paths = set(manifest['evidence_hashes']) | {v['path'] for v in manifest['bundles'].values()}
    for name in paths:
        path = APP/name
        if name.endswith('.json.gz'):
            data = json.loads(gzip.decompress(path.read_bytes()))
        elif name.endswith('.json'):
            data = json.loads(path.read_text())
        else:
            continue
        public_si = name in {'data/public/bau_detail_2025.json', 'data/public/capture_details_2025.json'}
        if public_si:
            assert data['source']['doi'] == '10.1016/j.jclepro.2023.138935'
            assert data['source']['workbook_sha256'] == 'a347acaa6c21c0e710dfd29678b329b420398df5a4f866dd6c68591e5a42a36b'
        for node in walk(data):
            assert not {'physical_carbon_display', 'original_evidence_hashes',
                        'source_columns', 'derivation', 'coefficient_of_performance'}.intersection(node), name
            if not public_si:
                assert 'source_cells' not in node and 'column' not in node, name
        serialized = json.dumps(data)
        assert 'scenarios_16_05_2022' not in serialized, name
        assert 'Capture plant!E' not in serialized, name


def test_removed_downloads_cannot_be_requested():
    from portal.wsgi import application
    from werkzeug.test import Client
    from werkzeug.wrappers import Response
    client = Client(application, Response)
    client.post('/ccus-webinar/login', data={'password': '11092026'})
    assert client.get('/ccus-webinar/evidence/utilities').status_code == 404
    heat = client.get('/ccus-webinar/evidence/heat-pump')
    assert heat.status_code == 200
    assert 'derivation' not in heat.json
    assert 'coefficient_of_performance' not in heat.json
    assert client.get('/ccus-webinar/evidence/quantities').json['status'] == 'public_si_illustration'
    assert 'physical_carbon_display' not in load_release_bundle().payloads


def test_temporal_public_view_never_reads_local_physical_export(monkeypatch):
    from apps.ccus_webinar.webinar.temporal_carbon_presentation import load_carbon_display
    def forbidden(*args, **kwargs):
        raise AssertionError('Public view attempted to read local inventory')
    bundle = load_release_bundle()
    monkeypatch.setattr(Path, 'read_text', forbidden)
    assert load_carbon_display(bundle) is None
