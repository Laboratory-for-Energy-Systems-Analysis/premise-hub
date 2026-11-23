"""Prepare MCV routing assets and capture their print previews."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from apps.mcv_2026.routing import (
    foreground_graph, foreground_start, foreground_template_options, french_graph_template,
)
from scripts.build_seoul_route_previews import projection


def run(workspace, destination):
    from flask import Flask, render_template_string
    from playwright.sync_api import sync_playwright

    app = Flask(__name__)
    library = ROOT / "apps/lca_time/assets/routing/lib/vis-9.1.2/vis-network.min.js"
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {"files": {}}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for case in ("daccs", "beccs"):
            source = workspace / "data/processed" / f"{case}-routing.json.gz"
            full = gzip.decompress(source.read_bytes())
            graph = json.loads(full)
            foreground = foreground_graph(graph)
            initial = json.dumps(foreground_start(foreground))
            digest = graph["metadata"]["package_sha256"]
            assert manifest.setdefault("package_sha256", digest) == digest
            shallow = projection(graph)
            artifacts = {
                f"{case}.json.gz": source.read_bytes(),
                f"{case}-depth3.json.gz": gzip.compress(shallow, mtime=0),
            }
            with app.app_context():
                html = render_template_string(
                    french_graph_template(), case_slug=case, print_preview=True,
                    **foreground_template_options(foreground),
                )

            def preview_asset(route):
                path = urlsplit(route.request.url).path
                if path.endswith(".html"):
                    route.fulfill(body=html, content_type="text/html")
                elif path.endswith(".js"):
                    route.fulfill(path=library, content_type="application/javascript")
                elif path.endswith(".json"):
                    route.fulfill(body=initial, content_type="application/json")
                else:
                    route.abort()

            page = browser.new_page(viewport={"width": 720, "height": 250}, device_scale_factor=2)
            page.route("**/*", preview_asset)
            page.goto(f"http://mcv.test/routing/{case}.html")
            page.wait_for_function("window.trailsGraph?.loadedDepth === 1")
            artifacts[f"{case}.png"] = page.screenshot()
            page.close()
            for name, payload in artifacts.items():
                (destination / name).write_bytes(payload)
                manifest["files"][name] = hashlib.sha256(payload).hexdigest()
        browser.close()
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--destination", type=Path, default=ROOT / "apps/mcv_2026/data/routing")
    args = parser.parse_args()
    run(args.workspace.resolve(), args.destination.resolve())


if __name__ == "__main__":
    main()
