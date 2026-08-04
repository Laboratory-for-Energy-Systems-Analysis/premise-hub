#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8050")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    base = args.url.rstrip("/")
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)

    bad_root_requests: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.on(
            "request",
            lambda request: bad_root_requests.append(request.url)
            if request.url.startswith(f"{base}/_dash") or request.url.startswith(f"{base}/assets/")
            else None,
        )

        page.goto(base, wait_until="networkidle")
        page.get_by_role("heading", name="Explore pathways. Transform inventories. Understand results.").wait_for()
        if args.output:
            page.screenshot(path=args.output / "landing-desktop.png", full_page=True)

        page.goto(f"{base}/scenarios/", wait_until="networkidle")
        page.get_by_role("heading", name="premise scenario explorer").wait_for()
        page.locator("#dataset-version-dropdown").wait_for()
        page.locator(".js-plotly-plot").first.wait_for()
        if args.output:
            page.screenshot(path=args.output / "scenario-explorer.png", full_page=True)

        page.goto(f"{base}/workshop/", wait_until="networkidle")
        page.locator(".slide").wait_for()
        page.locator("#next-button").click()
        page.get_by_role("heading", name="Societies demand services—not tonnes of fuel").wait_for()
        if args.output:
            page.screenshot(path=args.output / "workshop.png")

        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.goto(base, wait_until="networkidle")
        assert mobile.locator("body").evaluate("el => el.scrollWidth <= window.innerWidth + 1")
        if args.output:
            mobile.screenshot(path=args.output / "landing-mobile.png", full_page=True)
        browser.close()

    if bad_root_requests:
        raise AssertionError(f"Unprefixed Dash or asset requests: {bad_root_requests}")
    print("Portal browser smoke checks passed")


if __name__ == "__main__":
    main()
