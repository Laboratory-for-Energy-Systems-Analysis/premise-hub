#!/usr/bin/env python3
"""Browser QA and a landscape PDF of the Seoul lecture."""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
from scripts.browser_smoke import launch_chromium


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8057/seoul-2026/")
    parser.add_argument("--output", type=Path, default=Path("build/seoul-review"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(args.url + "health") as response:
        health = json.load(response)
    all_count = health["all_slides"]
    slide_keys = health["slide_keys"]
    pdf_count = health["pdf_pages"]
    pdf_all_count = health["pdf_all_pages"]
    errors, failures, layout = [], [], []
    with sync_playwright() as p:
        browser = launch_chromium(p)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on(
            "response",
            lambda response: (
                failures.append([response.status, response.url])
                if response.status >= 400
                else None
            ),
        )
        page.goto(args.url, wait_until="networkidle")
        page.locator(".snu-slide-0").wait_for()
        presenter = context.new_page()
        presenter.goto(args.url + "presenter", wait_until="networkidle")
        assert presenter.locator("#timer").inner_text() == "70:00"
        presenter.locator("#start").click()
        presenter.wait_for_timeout(1200)
        assert presenter.locator("#timer").inner_text() != "70:00"
        presenter.reload(wait_until="networkidle")
        assert presenter.locator("#start").inner_text() == "Pause timer"
        presenter.locator("#start").click()
        presenter.locator("#discussion").click()
        assert presenter.locator("#timer").inner_text() == "20:00"
        presenter.locator("#teaching").click()
        for index in range(all_count):
            key = slide_keys[index]
            page.evaluate("i => {location.hash='slide-'+i}", index)
            slide = page.locator(f".snu-slide-{index}")
            slide.wait_for()
            page.wait_for_timeout(300)
            assert presenter.locator("#slide-notes").get_attribute("data-slide-index") == str(index)
            assert 4 <= presenter.locator("#notes>li").count() <= 5
            layout.append(
                {
                    "index": index,
                    **slide.evaluate(
                        "e => ({w:e.clientWidth,h:e.clientHeight,scrollW:e.scrollWidth,scrollH:e.scrollHeight})"
                    ),
                }
            )
            if key in ("current", "future", "inventory", "response", "erw-sensitivity"):
                assert page.locator(
                    "#stage .comparison-grid>.comparison-panel"
                ).evaluate_all("els=>els.map(e=>e.dataset.case)") == [
                    "DACCS",
                    "BECCS",
                    "ERW",
                    "Cement + CCS",
                ]
            if key == "about":
                assert index == 1
                assert slide.locator('.bio-role').inner_text() == 'Scientist'
                assert slide.locator('.bio-project').count() == 4
                assert slide.locator('.bio-publication').count() == 3
                assert slide.locator('.bio-timeline time').all_text_contents() == ['2012','2018','2019']
                assert slide.locator('.bio-swiss-map').count() == 1
                assert slide.locator('img[alt="edges logo"]').count() == 1
                assert slide.locator('img').evaluate_all('es=>es.every(e=>e.complete && e.naturalWidth>0)')
            if key == "supply-chain":
                for i, case in enumerate(("DACCS", "BECCS", "ERW", "Cement + CCS")):
                    page.get_by_role(
                        "tab", name=f"Show {case} process diagram", exact=True
                    ).click()
                    assert page.locator("#stage .process-panel:visible").count() == 1
                    assert (
                        page.locator(
                            "#stage .process-panel:visible .process-heading strong"
                        ).inner_text()
                        == case
                    )
                    assert page.locator("#stage .process-panel:visible .process-sources a").count() >= 2
                    assert page.locator("#stage .process-flow-key").count() == 4
                    page.screenshot(path=args.output / f"process-{i}.png")
                page.get_by_role("button", name="Next technology", exact=True).click()
                assert page.locator("#stage .process-position").inner_text() == "1 / 4"
                page.get_by_role(
                    "tab", name="Show DACCS process diagram", exact=True
                ).focus()
                page.keyboard.press("ArrowRight")
                assert page.locator("#stage .process-position").inner_text() == "2 / 4"
                assert page.locator("[data-slide-key='supply-chain']").is_visible()
                page.keyboard.press("Home")
            if key == "inventory":
                assert slide.locator("#inventory-view").count() == 0
                annual_ranges, cumulative_ranges = set(), set()
                for i in range(4):
                    chart = page.locator(f"#four-time-{i} .js-plotly-plot")
                    annual_ranges.add(chart.evaluate("e => e.layout.yaxis.range.join(',')"))
                    cumulative_ranges.add(chart.evaluate("e => e.layout.yaxis2.range.join(',')"))
                    assert chart.evaluate("e => e.layout.yaxis2.range[0]") == -1000
                    assert chart.evaluate("e => e.layout.xaxis.range.join(',')") == "-5,100"
                    assert chart.evaluate("e => e.data.every(t => t.type === 'scatter')")
                    assert set(chart.evaluate("e => e.data.filter(t => t.stackgroup).map(t => t.stackgroup)")) == {"positive", "negative"}
                    overlays=(["ERW timing minimum","ERW timing maximum","Cumulative GWP100"]
                              if i==2 else ["Cumulative GWP100"])
                    assert chart.evaluate("e => e.data.filter(t => t.yaxis === 'y2').map(t => t.name)") == overlays
                    assert chart.evaluate("e => e.layout.meta.cumulative_overlay")
                    assert chart.evaluate("e => e.layout.xaxis.ticktext[0]") == ("2035" if i == 3 else "2030")
                    assert chart.evaluate("e => e.data.filter(t => !t.stackgroup).map(t => t.name)") == overlays
                    assert chart.evaluate("e => e.data.filter(t => t.stackgroup).every(t => t.line.shape === 'linear')")
                    assert chart.evaluate("e => !e.data.some(t => t.name === 'Direct / avoided emissions')")
                assert len(annual_ranges) == len(cumulative_ranges) == 1
                dac=page.locator("#four-time-0 .js-plotly-plot")
                assert dac.evaluate("e => e.data.filter(t => t.name.startsWith('Electricity + heat')).map(t => t.name)") == ["Electricity + heat (+)","Electricity + heat (−)"]
                assert dac.evaluate("e => e.data.find(t => t.name==='Electricity + heat (−)').fillpattern.shape") == "/"
                page.screenshot(path=args.output / "inventory-cumulative-overlay.png")
            if key == "delay":
                page.wait_for_function(
                    "document.querySelector('#pulse-timing-chart .js-plotly-plot')?.layout.meta.delay===0"
                )
                assert page.get_by_role("radio", name="2030 · same year", exact=True).is_checked()
                annotations = page.locator("#pulse-timing-chart .js-plotly-plot").evaluate(
                    "e=>e.layout.annotations.map(a=>a.text)"
                )
                assert "+1 t emitted" in annotations and "−1 t removed" in annotations
                page.get_by_text("2080 · 50 years later", exact=True).click()
                page.wait_for_function(
                    "document.querySelector('#pulse-timing-chart .js-plotly-plot')?.layout.meta.equivalent_kg>600"
                )
            if key == "response":
                assert slide.locator('[role="radio"]').count() == 0
                handles = slide.locator('#response-horizon [role="slider"]')
                assert handles.count() == 2
                handles.nth(1).focus()
                handles.nth(1).press("ArrowLeft")
                page.wait_for_function(
                    "document.querySelector('#four-forcing-0 .js-plotly-plot')?.layout.xaxis.range[1]===2049"
                )
                assert page.locator('#response-window-label').inner_text() == "2030–2049"
                for i in range(4):
                    assert "pW·year/m²" in page.locator(f'#four-forcing-area-{i}').inner_text()
                handles.nth(1).press("End")
                page.wait_for_function("document.querySelector('#four-forcing-0 .js-plotly-plot')?.layout.xaxis.range[1]===2200")
            if key == "suppliers":
                page.get_by_role("tab", name="Explore supply mixes", exact=True).click()
                page.locator("#context-chart").wait_for(state="visible")
                page.screenshot(path=args.output / "supplier-mixes.png")
                page.get_by_role("tab", name="Trace an input", exact=True).click()
                assert page.locator(".supplier-trace").is_visible()
            if key == "future":
                for pathway, label in (("SSP2-NPi", "~2.6 °C in 2100"),
                                        ("SSP2-PkBudg1000", "<2 °C in 2100 (default)")):
                    page.get_by_label(label, exact=True).check()
                    page.wait_for_function(
                        "p => [0,1,2,3].every(i => document.querySelector('#future-case-'+i+' .js-plotly-plot')?.layout.meta.bars_pathway === p)",
                        arg=pathway,
                    )
                    for i in range(4):
                        chart = page.locator(f"#future-case-{i} .js-plotly-plot")
                        assert chart.evaluate("e => e.layout.meta.years.join(',')") == "2025,2035,2050"
                        assert chart.evaluate("e => e.data.filter(t => t.type==='scatter').map(t => t.name)") == [
                            "~2.6 °C in 2100 net", "<2 °C in 2100 net", "2025 reference net"
                        ]
                        assert page.locator(f"#future-score-{i}").inner_text().startswith("2050: ")
                    page.screenshot(path=args.output / f"future-{pathway}.png")
            if key == "clocks":
                assert slide.get_by_role("tab").count() == 0
                assert slide.locator(".project-clocks img").is_visible()
                assert "Equipment stages + ERW arrows schematic" in slide.locator(".project-clocks-key").inner_text()
                page.screenshot(path=args.output / "integrated-clocks.png")
            if key == "pause-gwp":
                hints = slide.locator(".gwp-pause-hint")
                assert hints.count() == 4
                for i in range(4):
                    assert hints.nth(i).locator("img.gwp-hint-timeline").is_visible()
                    assert hints.nth(i).locator("p").count() == 0
                assert slide.locator(".gwp-pause-references a").count() == 3
                page.screenshot(path=args.output / "gwp-discussion-hints.png")
            if key == "trails":
                for case in ("DACCS", "BECCS", "ERW", "Cement + CCS"):
                    page.get_by_role("tab", name=case, exact=True).click()
                    assert page.locator(".route-example:visible").get_attribute("data-case") == case
                    assert page.locator("[data-slide-key='trails']").is_visible()
                    panel = page.locator(".route-example:visible")
                    assert panel.get_attribute("data-routing-kind") == "actual-trails-graph"
                    frame = panel.locator("iframe").content_frame
                    frame.locator("body[data-ready='true']").wait_for(timeout=60000)
                    assert frame.locator("#depth").input_value() == "3"
                    assert frame.locator("body").evaluate("()=>window.trailsGraph.loadedDepth") == 3
                    assert frame.locator("#view").input_value() == "dated"
                    assert frame.locator("#status").inner_text().endswith("Actual TRAILS routing output")
                    frame.locator("body").evaluate("""() => {
                        const g=window.trailsGraph, root=g.nodes.find(n=>n.depth===0);
                        if(!g.nodes.filter(n=>n.depth>0).every(n=>n.y<root.y)) throw Error('Functional unit must be at bottom');
                        if(g.branches.length<2) throw Error('Expected physical root activities, not a single wrapper');
                    }""")
                    frame.locator('body[data-activity-labels]:not([data-activity-labels="0"])').wait_for(timeout=60000)
                    assert frame.locator("body").evaluate("()=>window.trailsGraph.activityLabels.length") > 0
                    if case == "DACCS":
                        branch = frame.locator("body").evaluate("()=>window.trailsGraph.branches.find(b=>b.label.startsWith('market group for electricity, medium voltage')).key")
                        frame.locator("#branch").select_option(branch)
                        assert frame.locator("body").evaluate("()=>window.trailsGraph.nodes.length < window.trailsGraph.rawNodes")
                        assert frame.locator("body").evaluate("()=>window.trailsGraph.nodes.some(n=>n.depth===0)")
                        frame.locator("#branch").select_option("all")
                    frame.locator("#depth").select_option("0")
                    assert "1 dated nodes" in frame.locator("#status").inner_text()
                    frame.locator("#depth").select_option("4")
                    frame.locator("body[data-ready='true']").wait_for(timeout=60000)
                    assert frame.locator("body").evaluate("()=>window.trailsGraph.loadedDepth") == 4
                    assert page.locator(".route-frame").evaluate_all("fs=>fs.filter(f=>f.getAttribute('src')!=='about:blank').length") == 1
                    page.screenshot(path=args.output / f"routing-{case.split()[0].lower()}.png")
                assert page.locator(".route-data-workflow img").evaluate_all("es=>es.every(e=>e.complete && e.naturalWidth>0)")
                page.get_by_role("tab", name="DACCS", exact=True).focus()
                page.keyboard.press("ArrowRight")
                assert page.locator(".route-example:visible").get_attribute("data-case") == "BECCS"
                page.keyboard.press("Home")
                page.screenshot(path=args.output / "routing-example.png")
            if key == "pulse-equivalence":
                assert page.get_by_role("tab",name="How the comparison works",exact=True).get_attribute("aria-selected") == "true"
                assert slide.locator('.case-equivalence-method:visible').count() == 1
                page.get_by_role("tab",name="Match the four case areas",exact=True).click()
                assert slide.locator('[data-comparison="case-pulse-equivalence"] .comparison-panel').count() == 4
                initial = page.locator("#case-equivalence-0 .js-plotly-plot").evaluate("e=>e.layout.meta")
                handle = page.locator("#equivalence-window .rc-slider-handle")
                handle.nth(2).focus()
                page.keyboard.press("ArrowRight")
                page.wait_for_function("document.querySelector('#case-equivalence-0 .js-plotly-plot')?.layout.meta.window_end===2105")
                after = page.locator("#case-equivalence-0 .js-plotly-plot").evaluate("e=>e.layout.meta")
                assert after["case"] == initial["case"]
                assert after["equivalent_kg"] != initial["equivalent_kg"]
                handle.nth(1).focus()
                page.keyboard.press("ArrowRight")
                page.wait_for_function("document.querySelector('#case-equivalence-0 .js-plotly-plot')?.layout.meta.reference_year===2035")
                for i in range(4):
                    assert "kg CO₂-pulse-eq" in page.locator(f"#case-equivalence-readout-{i}").inner_text()
                    meta = page.locator(f"#case-equivalence-{i} .js-plotly-plot").evaluate("e=>e.layout.meta")
                    assert abs(meta["system_area"] - meta["matched_reference_area"]) < 1e-9
                assert "pulse 2035" in page.locator('#case-equivalence-window-summary').inner_text()
                page.get_by_role("tab", name="How the comparison works", exact=True).click()
                assert page.locator(".case-equivalence-method:visible").count() == 1
            if key == "sources":
                assert slide.locator('.resource-route').count() == 4
                for card in slide.locator('.resource-route').all():
                    assert card.locator('.resource-first-step').is_visible()
                    assert card.locator('a').count() >= 2
            if key == "workflow":
                assert slide.locator('.workflow-stage').count() == 5
                assert slide.locator('.workflow-choice-grid>div').count() == 4
                assert slide.locator('img').evaluate_all('es=>es.every(e=>e.complete && e.naturalWidth>0)')
            if key == "thanks":
                table = slide.locator('.seoul-closing-scores table')
                assert table.locator('tbody tr').count() == 4
                assert table.locator('tbody tr').first.locator('td').count() == 5
                assert table.locator('.closing-gross-score').all_text_contents() == ['≈ 1.32','≈ 4.67','≈ 1.20','≈ 1.44']
                assert 'GWP100' in table.inner_text() and 'CO₂-pulse-eq' in table.inner_text()
                assert 'Future 2035' in table.inner_text()
                assert table.locator('.closing-operation-period').all_text_contents() == ['2030–2049']*3+['2035–2064']
                assert slide.locator('.closing-score-takeaways li').count() == 3
                assert slide.locator('.closing-score-context').count() == 0
            if key == "erw-sensitivity":
                before = page.locator("#four-time-2 .js-plotly-plot").evaluate(
                    "e=>e.layout.meta"
                )
                page.locator("#erw-duration").click()
                page.locator(".VirtualizedSelectOption").get_by_text(
                    "30", exact=True
                ).click()
                page.wait_for_function(
                    "document.querySelector('#four-time-2 .js-plotly-plot')?.layout.meta.duration===30"
                )
                assert before["duration"] == 100
                page.get_by_role("tab", name="What this test does not cover", exact=True).click()
                assert page.locator(".uncertainty-card:visible").count() == 4
                page.screenshot(path=args.output / "uncertainty-layers.png")
                page.get_by_role("tab", name="Test ERW uptake timing", exact=True).click()
            if key in ("current", "future", "inventory", "erw-sensitivity"):
                for plot in page.locator("#stage .js-plotly-plot").all():
                    assert plot.evaluate("e=>!(e.layout.updatemenus||[]).length")
                if key in ("current", "future"):
                    for plot in page.locator("#stage .js-plotly-plot").all():
                        assert plot.evaluate(
                            "e=>{const v=e.data.filter(t=>t.type==='bar' && t.visible!==false).flatMap(t=>t.y); return Math.min(...v)<0 && Math.max(...v)>0;}"
                        )
            if index < all_count:
                page.screenshot(path=args.output / f"slide-{index:02d}.png")
        # Keyboard navigation on the audience page, not the notes page.
        page.evaluate("location.hash='slide-0'")
        page.locator(".snu-slide-0").wait_for()
        page.locator("body").click(position={"x": 4, "y": 400})
        page.keyboard.press("ArrowRight")
        page.locator(".snu-slide-1").wait_for()
        page.wait_for_function("location.hash === '#slide-1'")
        page.reload(wait_until="networkidle")
        page.locator(".snu-slide-1").wait_for()
        # Print all core slides with the actual Export PDF control.
        page.evaluate("window.print = () => { window.__printCalled = true; }")
        page.locator("#pdf-button").click()
        page.wait_for_function(
            "document.querySelector('#print-deck')?.dataset.ready==='true'",
            timeout=60000,
        )
        assert page.evaluate("window.__printCalled")
        assert page.locator("#print-deck>.snu-slide").count() == pdf_count
        about = page.locator("#print-deck>.snu-slide").nth(1)
        assert about.get_attribute('data-slide-key') == 'about'
        assert about.locator('.bio-portrait').evaluate('e=>e.complete && e.naturalWidth>0')
        assert page.locator("#print-deck [data-slide-key='pause-gwp'] .gwp-hint-timeline").count() == 4
        response = page.locator("#print-deck [data-slide-key='response']")
        assert response.locator(".forcing-area").count() == 4
        for area in response.locator(".forcing-area").all():
            assert "pW·year/m²" in area.inner_text()
        for chart in response.locator(".js-plotly-plot").all():
            assert chart.evaluate("e=>e.layout.xaxis.range") == [2030, 2050]
        assert page.locator(
            "#print-deck [data-slide-key='supply-chain'] .process-panel:not([hidden]) .process-heading strong"
        ).all_text_contents() == ["DACCS", "BECCS", "ERW", "Cement + CCS"]
        # Plotly creates its own SVG clip-path identifiers during rendering.
        identifiers = page.locator("#print-deck [id]").evaluate_all(
            "els=>els.map(e=>e.id)"
        )
        assert len(identifiers) == len(set(identifiers))
        page.emulate_media(media="print")
        page.pdf(
            path=str(args.output / "SNU_2026_Romain_Sacchi_Time_explicit_LCA.pdf"),
            print_background=True,
            prefer_css_page_size=True,
        )
        page.emulate_media(media="screen")
        page.locator("#print-backups input").check()
        page.evaluate("window.__printCalled = false")
        page.locator("#pdf-button").click()
        page.wait_for_function(
            "n=>document.querySelectorAll('#print-deck>.snu-slide').length===n && document.querySelector('#print-deck')?.dataset.ready==='true' && window.__printCalled",
            arg=pdf_all_count,
            timeout=60000,
        )
        page.emulate_media(media="print")
        page.pdf(
            path=str(
                args.output / "SNU_2026_Romain_Sacchi_Time_explicit_LCA_with_backup.pdf"
            ),
            print_background=True,
            prefer_css_page_size=True,
        )
        page.emulate_media(media="screen")
        page.set_viewport_size({"width": 1280, "height": 720})
        page.evaluate("i=>location.hash='slide-'+i", slide_keys.index("suppliers"))
        page.locator('[data-slide-key="suppliers"]').wait_for()
        page.screenshot(path=args.output / "laptop-1280.png")
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=args.output / "mobile.png")
        presenter.screenshot(path=args.output / "presenter.png", full_page=True)
        browser.close()
    report = dict(errors=errors, failed_requests=failures, layout=layout)
    (args.output / "browser-report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    assert not errors and not failures
    assert all(
        row["scrollH"] <= row["h"] + 2 and row["scrollW"] <= row["w"] + 2
        for row in layout
    )


if __name__ == "__main__":
    main()
