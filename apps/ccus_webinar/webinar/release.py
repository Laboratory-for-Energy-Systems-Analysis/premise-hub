"""Versioned webinar approval overlay over immutable diagnostic evidence.

Schema 2.1 distinguishes verified checks from explicitly accepted assumptions.
It does not rewrite historical manifests or claim routing convergence.
"""
from functools import lru_cache
import json
import gzip
from pathlib import Path
from ..lca_model.results import ResultBundle, REQUIRED_GATES, file_sha256

APP = Path(__file__).resolve().parents[1]
PORTABLE_MANIFEST = APP/'data/runtime/manifest.json'
MANIFEST = PORTABLE_MANIFEST if PORTABLE_MANIFEST.exists() else APP/'generated/releases/webinar-2026-09-08/manifest.json'
MAIN_TABLES = {'static_totals', 'static_contributions', 'static_subprocesses',
    'temporal_totals', 'temporal_contributions', 'fair_responses', 'pulse_equivalence', 'pulse_reference'}
EXPECTED_BUNDLES = {'main', *(f'{y}-{p}' for y in (2035,2050) for p in ('SSP2-NPi','SSP2-PkBudg1000'))}


def safe_path(root, name):
    p = (root/name).resolve()
    if Path(name).is_absolute() or not p.is_relative_to(root.resolve()):
        raise ValueError('Unsafe release path')
    return p


def validate_manifest(manifest, root):
    if manifest.get('schema_version') != '2.1.0' or manifest.get('status') != 'approved':
        raise ValueError('Release not approved')
    review = manifest.get('review', {})
    if not all(review.get(k) for k in ('reviewer','reviewed_at','note')):
        raise ValueError('Missing reviewer decision')
    gates = manifest.get('gates', {})
    if set(gates) != REQUIRED_GATES:
        raise ValueError('Incomplete release gates')
    for gate, item in gates.items():
        if item.get('status') not in ('verified','accepted_assumption') or not item.get('basis'):
            raise ValueError('Unresolved release gate: '+gate)
        if not item.get('evidence') or any(p not in manifest.get('evidence_hashes', {}) for p in item['evidence']):
            raise ValueError('Missing gate evidence: '+gate)
    if gates['trails_convergence']['status'] != 'accepted_assumption' or manifest.get('convergence_tested') is not False:
        raise ValueError('This release must not claim convergence was tested')
    if set(manifest.get('bundles', {})) != EXPECTED_BUNDLES:
        raise ValueError('Incomplete released states')
    for name, digest in manifest.get('evidence_hashes', {}).items():
        if file_sha256(safe_path(root, name)) != digest:
            raise ValueError('Changed release evidence/input: '+name)
    for item in manifest['bundles'].values():
        if file_sha256(safe_path(root, item['path'])) != item['sha256']:
            raise ValueError('Changed released result: '+item['path'])


@lru_cache(maxsize=1)
def release_manifest():
    if not MANIFEST.exists():
        return None
    data = json.loads(MANIFEST.read_text())
    validate_manifest(data, APP)
    return data


@lru_cache(maxsize=5)
def load_release_bundle(key='main'):
    if not MANIFEST.exists():
        return None
    try:
        meta = release_manifest()
        path = safe_path(APP, meta['bundles'][key]['path'])
        content = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
        raw = json.loads(content)
        tables = {k:tuple(v) for k,v in raw['tables'].items()}
        required = MAIN_TABLES if key=='main' else {'static_totals','static_subprocesses'}
        if not required <= tables.keys() or any(not tables[k] for k in required):
            raise ValueError('Missing released tables')
        for name in required-{'pulse_reference'}:
            if {r['system'] for r in tables[name]} != {'BAU','CCS','CCUS'}:
                raise ValueError('Incomplete system coverage: '+name)
        return ResultBundle('approved', meta['bundle_id']+'/'+key,
            'Reviewed webinar results with documented modelling assumptions', meta,
            tables, raw['payloads'], raw.get('arrays', {}))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ResultBundle('stale','webinar-release-invalid',str(exc),{}, {})
