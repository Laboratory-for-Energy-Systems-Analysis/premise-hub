"""Hash-checked exact-year sector shares for slide 9."""
import hashlib
import json
from pathlib import Path

APP = Path(__file__).resolve().parents[1]


def load_sector_shares(root=APP):
    path = root / 'data/processed/sector_shares_six_years.json'
    try:
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != path.with_suffix('.sha256').read_text().strip():
            return []
        artifact = json.loads(payload)
        packages = {r['pathway']: r['sha256'] for r in json.loads(
            (root / 'data/source_manifest.json').read_text())['trails_packages']}
        if artifact['packages'] != packages or artifact['year_policy'] != 'exact package anchors':
            return []
        return artifact['rows']
    except (OSError, ValueError, KeyError, TypeError):
        return []
