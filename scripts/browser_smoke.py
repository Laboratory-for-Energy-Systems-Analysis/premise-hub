#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def launch_chromium(playwright):
    expected = Path(playwright.chromium.executable_path)
    if expected.is_file():
        return playwright.chromium.launch()
    installed = sorted(
        (Path.home() / "Library" / "Caches" / "ms-playwright").glob(
            "chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell"
        )
    )
    if installed:
        return playwright.chromium.launch(executable_path=str(installed[-1]))
    return playwright.chromium.launch()


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
        browser = launch_chromium(playwright)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.on(
            "request",
            lambda request: (
                bad_root_requests.append(request.url)
                if request.url.startswith(f"{base}/_dash")
                or request.url.startswith(f"{base}/assets/")
                else None
            ),
        )

        page.goto(base, wait_until="networkidle")
        page.get_by_role(
            "heading",
            name="Explore pathways. Transform inventories. Understand results.",
        ).wait_for()
        if args.output:
            page.screenshot(path=args.output / "landing-desktop.png", full_page=True)

        page.goto(f"{base}/scenarios/", wait_until="networkidle")
        page.get_by_role("heading", name="premise scenario explorer").wait_for()
        page.locator("#dataset-version-dropdown").wait_for()
        page.locator(".js-plotly-plot").first.wait_for()
        assert page.locator(".psi-mark").is_visible()
        assert page.locator(".result-card").count() == 1
        assert page.locator(".result-card").first.evaluate(
            "el => getComputedStyle(el).borderTopColor === 'rgb(0, 138, 130)'"
        )
        page.get_by_role("button", name="Add comparison").click()
        page.get_by_text("That model–scenario pair is already included.").wait_for()
        if args.output:
            page.screenshot(path=args.output / "scenario-explorer.png", full_page=True)

        district_url = (
            f"{base}/scenarios/?version=2.4.9"
            "&sector=Heat+-+District+heating"
            "&pair=image%3ASSP1-L&region=World&mode=relative"
        )
        page.goto(district_url, wait_until="networkidle")
        page.get_by_role(
            "heading", name="Heat - District heating", exact=True
        ).wait_for()
        page.get_by_text("Derived World", exact=True).first.wait_for()
        page.locator(".js-plotly-plot").first.wait_for()
        plot_contract = page.locator(".js-plotly-plot").first.evaluate(
            "el => ({trace_count: el.data.length, y_range: el.layout.yaxis.range, legends: el.querySelectorAll('.legend').length})"
        )
        assert plot_contract["trace_count"] <= 9, plot_contract
        assert plot_contract["y_range"] == [0, 100], plot_contract
        assert plot_contract["legends"] == 1, plot_contract
        assert "sector=Heat+-+District+heating" in page.locator(
            "#share-view-link"
        ).get_attribute("href")
        if args.output:
            page.screenshot(
                path=args.output / "scenario-explorer-district-heat.png", full_page=True
            )

        transport_url = (
            f"{base}/scenarios/?version=2.4.9"
            "&sector=Transport+Passenger+Cars"
            "&pair=image%3ASSP1-L&pair=image%3ASSP1-M"
            "&pair=image%3ASSP1-VLLO&pair=image%3ASSP2-M"
            "&region=World&mode=absolute"
        )
        page.goto(transport_url, wait_until="networkidle")
        page.get_by_role(
            "heading", name="Transport Passenger Cars", exact=True
        ).wait_for()
        page.locator(".js-plotly-plot").nth(3).wait_for()
        assert page.locator(".result-card").count() == 4
        transport_contract = page.locator(".js-plotly-plot").evaluate_all(
            """els => els.map(el => ({
                upperRange: el.layout.yaxis.range[1],
                unit: el.layout.yaxis.title.text
            }))"""
        )
        assert all(
            80_000 < plot["upperRange"] < 200_000 for plot in transport_contract
        ), transport_contract
        assert all(
            plot["unit"] == "Vehicle-kilometers (billion)"
            for plot in transport_contract
        ), transport_contract

        removal_url = (
            f"{base}/scenarios/?version=2.4.9"
            "&sector=Carbon+Dioxide+Removal"
            "&pair=image%3ASSP1-L&region=World&mode=absolute"
        )
        page.goto(removal_url, wait_until="networkidle")
        page.get_by_role(
            "heading", name="Carbon Dioxide Removal", exact=True
        ).wait_for()
        page.locator(".js-plotly-plot").first.wait_for()
        removal_contract = page.locator(".js-plotly-plot").first.evaluate(
            "el => el.data.map(trace => trace.stackgroup)"
        )
        assert len(removal_contract) > 1, removal_contract
        assert all(group == "1" for group in removal_contract), removal_contract

        page.goto(f"{base}/workshop/", wait_until="networkidle")
        page.locator(".slide").wait_for()
        page.locator("#next-button").click()
        page.get_by_role(
            "heading", name="Societies demand services—not tonnes of fuel"
        ).wait_for()
        if args.output:
            page.screenshot(path=args.output / "workshop.png")

        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.goto(base, wait_until="networkidle")
        assert mobile.locator("body").evaluate(
            "el => el.scrollWidth <= window.innerWidth + 1"
        )
        if args.output:
            mobile.screenshot(path=args.output / "landing-mobile.png", full_page=True)

        mobile.goto(f"{base}/scenarios/", wait_until="networkidle")
        mobile.get_by_role("heading", name="premise scenario explorer").wait_for()
        mobile.locator(".js-plotly-plot").first.wait_for()
        assert mobile.locator("body").evaluate(
            "el => el.scrollWidth <= window.innerWidth + 1"
        )
        assert mobile.locator(".result-card").first.evaluate(
            "el => { const tick = el.querySelector('.xtick'); return tick && tick.getBoundingClientRect().bottom <= el.getBoundingClientRect().bottom; }"
        )
        assert mobile.locator(".primary-controls").evaluate(
            "el => getComputedStyle(el).gridTemplateColumns.split(' ').length === 1"
        )
        mobile.get_by_role("button", name="Add comparison").wait_for()
        if args.output:
            mobile.screenshot(
                path=args.output / "scenario-explorer-mobile.png", full_page=True
            )
        browser.close()

    if bad_root_requests:
        raise AssertionError(f"Unprefixed Dash or asset requests: {bad_root_requests}")
    print("Portal browser smoke checks passed")


if __name__ == "__main__":
    main()
