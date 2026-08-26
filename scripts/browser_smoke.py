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


def unlock_presentation(page, url: str, password: str) -> None:
    page.goto(url, wait_until="networkidle")
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Open presentation").click()
    page.wait_for_url(url)
    page.wait_for_load_state("networkidle")


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
        page.get_by_role("heading", name="Research using Premise").wait_for()
        publication_count = page.locator("[data-publication-item]").count()
        assert publication_count >= 49
        assert page.locator("#publication-result-count").text_content() == (
            f"{publication_count} verified publications"
        )
        page.locator("#publication-search").fill("FuelEU Maritime")
        assert page.locator("[data-publication-item]:visible").count() == 1
        assert page.locator("#publication-result-count").text_content() == (
            f"1 of {publication_count} publications"
        )
        page.locator("#publication-reset").click()
        assert page.locator("[data-publication-item]:visible").count() == publication_count
        if args.output:
            page.screenshot(path=args.output / "landing-desktop.png", full_page=True)

        page.goto(f"{base}/ecosystem/", wait_until="networkidle")
        page.get_by_role(
            "heading", name="The Brightway ecosystem, connected."
        ).wait_for()
        page.locator(".ecosystem-edge").first.wait_for(state="attached")
        all_nodes = page.locator(".ecosystem-node")
        legacy_nodes = page.locator('.ecosystem-node[data-status="legacy"]')
        legacy_count = legacy_nodes.count()
        assert page.locator(".ecosystem-node:not([hidden])").count() == (
            all_nodes.count() - legacy_count
        )
        premise_node = page.locator('[data-tool-id="premise"]')
        premise_node.hover()
        page.locator(".ecosystem-edge.is-active").first.wait_for(state="attached")
        assert page.locator(".ecosystem-node.is-related").count() >= 3
        premise_node.click()
        page.get_by_role("dialog").wait_for()
        assert page.locator("#ecosystem-detail-name").text_content() == "premise"
        assert page.url.endswith("/ecosystem/#premise")
        page.locator("#ecosystem-detail-close").click()
        page.locator("#ecosystem-search").fill("pulpo")
        assert page.locator("#ecosystem-result-count").text_content().startswith("1 of")
        page.locator("#ecosystem-status-filter").select_option("legacy")
        assert page.locator("#ecosystem-result-count").text_content().startswith("0 of")
        page.locator("#ecosystem-search").fill("")
        assert (
            page.locator("#ecosystem-result-count")
            .text_content()
            .startswith(f"{legacy_count} of")
        )
        page.locator("#ecosystem-reset").click()
        if args.output:
            page.screenshot(path=args.output / "ecosystem-desktop.png", full_page=True)

        page.evaluate(
            """localStorage.setItem("saved-view-store", JSON.stringify({
                revision: 2,
                version: "2.4.9",
                sector: "GMST increase",
                pairs: [
                    {model: "image", scenario: "SSP1-L"},
                    {model: "image", scenario: "SSP1-M"}
                ],
                regions: ["World"],
                mode: "absolute"
            }))"""
        )
        page.goto(f"{base}/scenarios/", wait_until="networkidle")
        page.get_by_role("heading", name="premise scenario explorer").wait_for()
        page.locator("#dataset-version-dropdown").wait_for()
        page.locator(".js-plotly-plot").first.wait_for()
        assert page.locator(".psi-mark").is_visible()
        assert page.locator(".result-card").count() == 1
        assert page.locator(".js-plotly-plot").first.evaluate(
            "el => el.data.map(trace => trace.name)"
        ) == ["IMAGE · SSP1-L", "IMAGE · SSP2-M", "IMAGE · SSP3-H"]
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

        unlock_presentation(page, f"{base}/workshop/", "03092026")
        page.locator(".slide").wait_for()
        page.locator("#next-button").click()
        page.get_by_role(
            "heading", name="Societies demand services—not tonnes of fuel"
        ).wait_for()
        if args.output:
            page.screenshot(path=args.output / "workshop.png")

        page.goto(f"{base}/lca-time/", wait_until="networkidle")
        page.locator(".slide").wait_for()
        page.get_by_role(
            "heading", name="How time changes LCA results"
        ).wait_for()
        page.locator("#next-button").click()
        page.get_by_role(
            "heading", name="One study, three treatments of time"
        ).wait_for()
        page.get_by_role(
            "link", name="Sacchi et al. (2026) · TRAILS preprint"
        ).wait_for()
        if args.output:
            page.screenshot(path=args.output / "lca-through-time.png")

        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.goto(base, wait_until="networkidle")
        assert mobile.locator("body").evaluate(
            "el => el.scrollWidth <= window.innerWidth + 1"
        )
        mobile.get_by_role("heading", name="Research using Premise").wait_for()
        assert mobile.locator(".publication-controls").evaluate(
            "el => getComputedStyle(el).gridTemplateColumns.split(' ').length === 1"
        )
        if args.output:
            mobile.screenshot(path=args.output / "landing-mobile.png", full_page=True)

        mobile.goto(f"{base}/ecosystem/", wait_until="networkidle")
        mobile.get_by_role(
            "heading", name="The Brightway ecosystem, connected."
        ).wait_for()
        assert mobile.locator("body").evaluate(
            "el => el.scrollWidth <= window.innerWidth + 1"
        )
        assert mobile.locator("#ecosystem-connections").evaluate(
            "el => getComputedStyle(el).display === 'none'"
        )
        mobile.locator('[data-tool-id="trails"]').click()
        mobile.get_by_role("dialog").wait_for()
        assert mobile.locator("#ecosystem-detail-name").text_content() == "TRAILS"
        if args.output:
            mobile.screenshot(path=args.output / "ecosystem-mobile.png", full_page=True)
        mobile.locator("#ecosystem-detail-close").click()

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
