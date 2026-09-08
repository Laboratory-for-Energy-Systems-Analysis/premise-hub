"""Read-only gas-mix context, kept separate from calculated LCA artifacts."""
import hashlib
import json
from pathlib import Path

APP = Path(__file__).resolve().parents[1]


def load_gas_shares(root=APP):
    path = root / 'data/processed/gas_supply_shares.json'
    try:
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != path.with_suffix('.sha256').read_text().strip():
            return []
        artifact = json.loads(payload)
        rows = artifact['rows']
        if artifact['basis'] != 'IAM secondary gas production by energy' or artifact['location'] != 'ENC':
            return []
        return rows
    except (OSError, ValueError, KeyError, TypeError):
        return []
