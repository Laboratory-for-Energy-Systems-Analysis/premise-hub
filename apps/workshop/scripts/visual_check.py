#!/usr/bin/env python3
"""Capture every presenter state and report viewport overflow.

Run this with a local server already listening on port 8050 and a Python
environment that contains Playwright plus its Chromium browser.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop.config import (
    ANONYMOUS_SLIDE,
    CORE_LAST_SLIDE,
    FIRST_SECTOR_SLIDE,
    IAM_MAP_SLIDE,
    LAST_SLIDE,
    RESULT_TRACER_SLIDE,
)


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
    parser.add_argument("--output", type=Path, default=Path("build/visual-check"))
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    vertical_overflow: list[tuple[int, int]] = []
    document_overflow: list[tuple[int, int]] = []
    with sync_playwright() as playwright:
        browser = launch_chromium(playwright)
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        page.goto(args.url, wait_until="networkidle")
        for slide in range(LAST_SLIDE + 1):
            page.wait_for_selector(".slide")
            if page.locator(".graph-frame").count():
                page.wait_for_selector(".graph-frame .js-plotly-plot")
            page.wait_for_timeout(500)
            page.screenshot(path=args.output / f"slide-{slide + 1:02d}.png")
            overflow = page.locator(".slide").evaluate(
                "el => ({x: el.scrollWidth - el.clientWidth, "
                "y: el.scrollHeight - el.clientHeight})"
            )
            if overflow["x"] > 1:
                failures.append(
                    f"slide {slide + 1}: horizontal overflow {overflow['x']} px"
                )
            stage_overflow = page.locator(".slide-stage").evaluate(
                "el => Math.max(0, el.scrollHeight - el.clientHeight)"
            )
            vertical_overflow.append((slide + 1, stage_overflow))
            document_overflow.append(
                (
                    slide + 1,
                    page.evaluate(
                        "Math.max(0, document.documentElement.scrollHeight - window.innerHeight)"
                    ),
                )
            )
            if page.locator(".backup-link-button").count():
                origin_label = page.locator("#slide-label").text_content()
                page.locator(".backup-link-button").click()
                page.wait_for_selector(".backup-slide")
                assert page.locator(".backup-return-button").count() == 1
                page.locator(".backup-return-button").click()
                page.wait_for_function(
                    "label => document.querySelector('#slide-label')?.textContent === label",
                    arg=origin_label,
                )
                assert page.locator(".backup-slide").count() == 0
            if slide == ANONYMOUS_SLIDE:
                page.locator("#reveal-button").click()
                page.wait_for_timeout(500)
                page.screenshot(
                    path=args.output / f"slide-{slide + 1:02d}-revealed.png"
                )
            if slide == IAM_MAP_SLIDE:
                initial_regions = len(
                    set(
                        page.locator(".iam-world-map-graph .js-plotly-plot").evaluate(
                            "el => el.data[0].customdata"
                        )
                    )
                )
                assert initial_regions == 26
                for model_label, expected_regions in [
                    ("MESSAGE", 12),
                    ("REMIND", 12),
                    ("REMIND-EU", 21),
                    ("TIAM-UCL", 16),
                    ("GCAM", 32),
                ]:
                    page.get_by_role("button", name=model_label, exact=True).click()
                    page.wait_for_timeout(400)
                    assert (
                        page.locator(".iam-map-button.active")
                        .filter(has_text=model_label)
                        .count()
                        == 1
                    )
                    page.wait_for_function(
                        "expected => { const el = document.querySelector("
                        "'.iam-world-map-graph .js-plotly-plot'); "
                        "return el?.data?.[0]?.customdata && "
                        "new Set(el.data[0].customdata).size === expected; }",
                        arg=expected_regions,
                    )
                    region_count = len(
                        set(
                            page.locator(
                                ".iam-world-map-graph .js-plotly-plot"
                            ).evaluate("el => el.data[0].customdata")
                        )
                    )
                    assert region_count == expected_regions
                page.screenshot(path=args.output / f"slide-{slide + 1:02d}-gcam.png")
            if slide == FIRST_SECTOR_SLIDE:
                initial_colours = page.locator(".sector-main .js-plotly-plot").evaluate(
                    "el => Object.fromEntries(el.data.map(trace => "
                    "[trace.name, trace.marker.color]))"
                )
                page.get_by_role("button", name="2040").click()
                page.wait_for_timeout(500)
                assert (
                    page.locator(".control-chip.active").filter(has_text="2040").count()
                    == 1
                )
                updated_colours = page.locator(".sector-main .js-plotly-plot").evaluate(
                    "el => Object.fromEntries(el.data.map(trace => "
                    "[trace.name, trace.marker.color]))"
                )
                shared_technologies = set(initial_colours) & set(updated_colours)
                assert shared_technologies
                assert all(
                    initial_colours[technology] == updated_colours[technology]
                    for technology in shared_technologies
                )
                page.get_by_role("button", name="Absolute", exact=True).click()
                page.wait_for_timeout(500)
                assert (
                    page.locator(".control-chip.active")
                    .filter(has_text="Absolute")
                    .count()
                    == 1
                )
                absolute_title = page.locator(".sector-gwp .js-plotly-plot").evaluate(
                    "el => el.layout.title.text"
                )
                assert "LCA-scaled GWP" in absolute_title
                page.screenshot(
                    path=args.output / f"slide-{slide + 1:02d}-electricity-absolute.png"
                )
                for sector_label, slug in [
                    ("Passenger cars", "passenger-cars"),
                    ("Cement", "cement"),
                    ("Steel", "steel"),
                ]:
                    page.get_by_role("button", name=sector_label, exact=True).click()
                    page.wait_for_timeout(500)
                    assert (
                        page.locator(".control-chip.active")
                        .filter(has_text=sector_label)
                        .count()
                        == 1
                    )
                    sector_gwp_title = page.locator(
                        ".sector-gwp .js-plotly-plot"
                    ).evaluate("el => el.layout.title.text")
                    if sector_label == "Passenger cars":
                        assert "Absolute GWP unavailable" in sector_gwp_title
                    else:
                        assert "LCA-scaled GWP" in sector_gwp_title
                    page.screenshot(
                        path=args.output / f"slide-{slide + 1:02d}-{slug}-absolute.png"
                    )
            if slide == RESULT_TRACER_SLIDE:
                page.get_by_role("button", name="Cement", exact=True).click()
                page.wait_for_timeout(400)
                page.get_by_role("button", name="SSP2-M", exact=True).click()
                page.wait_for_timeout(400)
                page.get_by_role("button", name="2040", exact=True).click()
                page.wait_for_timeout(400)
                page.get_by_role("button", name="Metals", exact=True).click()
                page.wait_for_timeout(600)
                for label in ["Cement", "SSP2-M", "2040", "Metals"]:
                    assert (
                        page.locator(".control-chip.active")
                        .filter(has_text=label)
                        .count()
                        == 1
                    )
                selected_trajectory = page.locator(
                    ".tracer-result-graph .js-plotly-plot"
                ).evaluate(
                    "el => el.data.filter(trace => trace.opacity === 1)"
                    ".map(trace => trace.name)"
                )
                assert selected_trajectory == ["SSP2-M"]
                contribution_title = page.locator(
                    ".tracer-contribution-graph .js-plotly-plot"
                ).evaluate("el => el.layout.title.text")
                assert "SSP2-M · 2040" in contribution_title
                assert (
                    page.locator(".tracer-selected-result")
                    .get_by_text("SSP2-M", exact=True)
                    .count()
                    >= 1
                )
                page.screenshot(
                    path=args.output / f"slide-{slide + 1:02d}-cement-ssp2-m-metals.png"
                )
            if slide < LAST_SLIDE:
                if slide == CORE_LAST_SLIDE:
                    page.get_by_role("button", name="Backup", exact=True).click()
                else:
                    page.locator("#next-button").click()
                page.wait_for_timeout(250)
        browser.close()

    if failures:
        raise SystemExit("\n".join(failures))
    scrolled = [(slide, amount) for slide, amount in vertical_overflow if amount > 1]
    page_scrolled = [
        (slide, amount) for slide, amount in document_overflow if amount > 1
    ]
    print(f"Captured {LAST_SLIDE + 1} slides in {args.output}; no horizontal overflow")
    print(f"Vertical stage overflow: {scrolled or 'none'}")
    print(f"Document overflow: {page_scrolled or 'none'}")


if __name__ == "__main__":
    main()
