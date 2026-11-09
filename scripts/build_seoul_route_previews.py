"""Extract exact depth-three responses from the existing verified routing graphs.

This changes only the transport representation, not routing or scientific data.
Run with --check to verify committed previews and their pinned response hashes.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apps.seoul_2026 import routing


def projection(graph):
    graph["nodes"] = [node for node in graph["nodes"] if node["depth"] <= 3]
    ids = {node["id"] for node in graph["nodes"]}
    graph["edges"] = [
        edge
        for edge in graph["edges"]
        if edge["source"] in ids and edge["target"] in ids
    ]
    graph["loaded_max_depth"] = 3
    return json.dumps(graph, separators=(",", ":")).encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    hashes = {}
    for slug in routing.SLUGS.values():
        source = routing.verified_route_path(slug, "json")
        payload = projection(json.loads(source.read_text()))
        digest = hashlib.sha256(payload).hexdigest()
        hashes[slug] = digest
        target = source.with_name(f"{slug}-depth3.json.gz")
        if args.check:
            assert gzip.decompress(target.read_bytes()) == payload, slug
            assert routing.SHALLOW_ROUTE_SHA256[slug] == digest, slug
        else:
            buffer = io.BytesIO()
            with gzip.GzipFile(
                fileobj=buffer, mode="wb", filename="", mtime=0
            ) as stream:
                stream.write(payload)
            target.write_bytes(buffer.getvalue())
    print(json.dumps(hashes, indent=2))


if __name__ == "__main__":
    main()
