"""Exercise the mounted/standalone deck and export its main-talk PDF."""

from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8050/setac-2026/")
    parser.add_argument("--output", type=Path, default=Path("build/setac-2026"))
    parser.add_argument("--browser", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    errors = []
    overflows = []
    bad_requests = []
    with sync_playwright() as p:
        executable = args.browser
        if executable is None and not Path(p.chromium.executable_path).is_file():
            brave = Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser")
            if brave.is_file():
                executable = brave
        browser = p.chromium.launch(
            **({"executable_path": str(executable)} if executable else {})
        )
        try:
            context = browser.new_context(
                viewport={"width": 1440, "height": 900}, device_scale_factor=1
            )
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on(
                "response",
                lambda response: (
                    bad_requests.append(f"{response.status}: {response.url}")
                    if response.status >= 400
                    else None
                ),
            )
            base = args.url.rstrip("/") + "/"
            landing = context.request.get(base)
            assert landing.status == 200, "Presentation must open without a password"
            assert 'type="password"' not in landing.text()
            core_count = context.request.get(base + "health").json()["core_slides"]
            page.goto(base, wait_until="networkidle")
            page.locator(".setac-slide-1").wait_for()
            presenter = context.new_page()
            presenter.goto(base + "presenter", wait_until="networkidle")
            page.bring_to_front()
            page.set_default_timeout(15000)
            pulse_slide = None
            default_pulse_cards = None
            closing_slide = None
            for index in range(core_count):
                print(f"Checking slide {index+1}", flush=True)
                slide = page.locator(f"#stage .setac-slide-{index+1}")
                slide.wait_for()
                page.wait_for_function(
                    "() => !document.querySelector('#stage [data-dash-is-loading=true]')"
                )
                page.wait_for_function(
                    """() => [...document.querySelectorAll('#stage .dash-graph')].every(root => {
                        const plot = root.querySelector('.js-plotly-plot');
                        return plot && plot._fullLayout && plot._fullData && plot._fullData.length &&
                            Math.abs(plot._fullLayout.width - root.clientWidth) < 3 &&
                            Math.abs(plot._fullLayout.height - root.clientHeight) < 3;
                    })""",
                    polling=100,
                )
                page.screenshot(path=str(args.output / f"slide-{index+1:02d}.png"))
                overflow = page.evaluate(
                    """() => [...document.querySelectorAll('#stage .slide-body, #stage .slide-body *')].filter(e => {
                  if (e.closest('.js-plotly-plot, .rc-slider')) return false;
                  const css=getComputedStyle(e); if(css.display==='none'||css.position==='absolute') return false;
                  return e.clientWidth>0 && (e.scrollWidth>e.clientWidth+3 || e.scrollHeight>e.clientHeight+3);
                }).map(e => ({tag:e.tagName,cls:e.className,w:e.clientWidth,sw:e.scrollWidth,h:e.clientHeight,sh:e.scrollHeight}))"""
                )
                if overflow:
                    overflows.append({"slide": index + 1, "elements": overflow})
                assert presenter.locator("#selection").input_value() == str(index)
                assert presenter.locator("#cue-text").inner_text()
                assert not presenter.locator("#technical-notes").evaluate("e => e.open")
                if page.locator("#pulse-window").count():
                    pulse_slide = index + 1
                    default_pulse_cards = page.locator("#pulse-values").inner_text()
                if page.locator("#temporal-view").count():
                    page.get_by_text("Unstacked lines", exact=True).click()
                    page.wait_for_function("""() => {
                            const p=document.querySelector('#temporal-chart .js-plotly-plot');
                            return p._fullLayout.meta.view === 'unstacked' && p.data.every(t => !t.stackgroup);
                        }""")
                    page.screenshot(path=str(args.output / "temporal-unstacked.png"))
                    page.get_by_text("Stacked areas", exact=True).click()
                    page.wait_for_function(
                        "() => document.querySelector('#temporal-chart .js-plotly-plot')._fullLayout.meta.view === 'stacked'"
                    )
                if page.locator("#stage .closing-takeaways").count():
                    closing_slide = index + 1
                    assert page.locator("#stage .closing-takeaways li").count() == 4
                    assert (
                        page.locator("#stage .closing-contact address a").get_attribute(
                            "href"
                        )
                        == "mailto:romain.sacchi@psi.ch"
                    )
                if page.locator("#mix-pathway").count():
                    assert page.locator(
                        "#stage .mix-panels .js-plotly-plot"
                    ).evaluate_all(
                        """plots => plots.length === 3 && plots.every(plot =>
                            plot.data.every(trace => trace.x.join(',') === '2025,2030,2035,2040,2045,2050'))"""
                    )
                    for indicator, region in (
                        ("CO₂ emissions", "World"),
                        ("CO₂ emissions", "Northern Europe"),
                        ("Population", "Northern Europe"),
                    ):
                        page.locator("#context-indicator").click()
                        page.get_by_text(indicator, exact=True).last.click()
                        page.locator("#context-region").click()
                        page.get_by_text(region, exact=True).last.click()
                        page.wait_for_function(
                            """([indicator, region]) => {
                              const meta = document.querySelector('#context-chart .js-plotly-plot')._fullLayout.meta;
                              return meta.indicator === indicator && meta.region === region;
                            }""",
                            arg=[
                                "CO2" if indicator == "CO₂ emissions" else indicator,
                                "ENC" if region == "Northern Europe" else region,
                            ],
                        )
                        page.screenshot(
                            path=str(
                                args.output
                                / f"context-{indicator.split()[0]}-{region.split()[0]}.png"
                            )
                        )
                    page.locator("#context-indicator").click()
                    page.get_by_text("GMST", exact=True).click()
                    page.wait_for_function(
                        "() => document.querySelector('#context-chart .js-plotly-plot')._fullLayout.meta.region === 'World'"
                    )
                    assert "World" in page.locator("#context-region").inner_text()
                    # Scenario changes update all three plots; materials share
                    # the selected scenario. Hover exposes the actual shares.
                    page.get_by_role(
                        "radio", name="NPi · policies in place", exact=True
                    ).check()
                    page.wait_for_function(
                        """() => ['context-chart','mix-electricity','mix-heat','mix-material'].every(id =>
                      document.querySelector('#'+id+' .js-plotly-plot')._fullLayout.meta.pathway === 'SSP2-NPi')"""
                    )
                    # Plotly's transparent drag layer receives the pointer.
                    page.locator("#mix-electricity .barlayer .point").first.hover(
                        force=True
                    )
                    page.wait_for_function(
                        "() => document.querySelector('#mix-electricity .hoverlayer').textContent.includes('Hydro')"
                    )
                    for sector in ("Cement clinker", "Truck transport"):
                        page.locator("#mix-material-sector").click()
                        page.get_by_text(sector, exact=True).click()
                        page.wait_for_function(
                            """sector =>
                          document.querySelector('#mix-material .js-plotly-plot')._fullLayout.meta.sector === sector""",
                            arg=sector,
                        )
                        page.screenshot(
                            path=str(
                                args.output / f"mix-{sector.split()[0].lower()}.png"
                            )
                        )
                if index < core_count - 1:
                    page.locator("#next-button").click()
            assert page.locator("#next-button").is_disabled()
            page.locator("#backup-button").click()
            page.locator(f".setac-slide-{core_count + 1}").wait_for()
            total_count = presenter.locator("#selection option").count()
            for index in range(core_count + 1, total_count + 1):
                page.locator(f".setac-slide-{index}").wait_for()
                page.screenshot(
                    path=str(args.output / f"backup-{index-core_count}.png")
                )
                if index < total_count:
                    page.locator("#next-button").click()
            page.locator("#backup-button").click()
            page.locator(f".setac-slide-{core_count}").wait_for()
            assert (
                page.locator("#stage h1").inner_text()
                == "Data sources and model versions"
            )
            assert closing_slide is not None
            assert pulse_slide is not None
            page.evaluate(
                "index => { window.location.hash = 'slide-' + index; }", pulse_slide - 1
            )
            page.locator(f"#stage .setac-slide-{pulse_slide}").wait_for()
            handles = page.locator("#pulse-window [role=slider]")
            assert handles.count() == 3
            assert handles.nth(0).get_attribute("aria-valuenow") == "2020"
            assert handles.nth(1).get_attribute("aria-valuenow") == "2030"
            for index, key, expected in ((0, "Home", 2000), (1, "ArrowRight", 2035)):
                handles.nth(index).focus()
                handles.nth(index).press(key)
                page.wait_for_function(
                    """([field,value]) => document.querySelector('#pulse-chart .js-plotly-plot')._fullLayout.meta[field] === value""",
                    arg=["start" if index == 0 else "reference", expected],
                )
                assert (
                    str(expected) in page.locator("#pulse-configuration").inner_text()
                )
                assert str(expected) in page.locator("#pulse-comparison").inner_text()
                assert str(expected) in page.locator("#pulse-takeaway").inner_text()
                assert page.locator(f".setac-slide-{pulse_slide}").count() == 1
            page.screenshot(path=str(args.output / "pulse-three-handles.png"))
            # Restore the default start and reference before checking the far endpoint.
            handles.nth(0).focus()
            for _ in range(4):
                handles.nth(0).press("ArrowRight")
            handles.nth(1).focus()
            handles.nth(1).press("ArrowLeft")
            handles.nth(2).focus()
            handles.nth(2).press("End")
            page.wait_for_function(
                """() => {
                    const plot = document.querySelector('#pulse-chart .js-plotly-plot');
                    const cards = document.querySelector('#pulse-values').textContent;
                    return plot._fullLayout.meta.end === 2300 && [1, 3].every(i =>
                        cards.includes(Math.round(plot.data[i].y[0]).toLocaleString('en-US'))
                    );
                }""",
                polling=100,
                timeout=15000,
            )
            assert (
                page.locator(f".setac-slide-{pulse_slide}").count() == 1
            )  # Arrow keys stay in slider.
            takeaway = page.locator("#pulse-takeaway").inner_text()
            assert "2020–2300" in takeaway
            assert "0.823 tonnes of CO₂" in takeaway
            assert "0.889 tonnes of CO₂" in takeaway
            page.screenshot(path=str(args.output / "pulse-2300.png"))
            # Capture the actual export callback, but suppress the interactive dialog.
            page.evaluate("window.print = () => { window.__printCalled = true; }")
            page.locator("#pdf-button").click()
            page.wait_for_function(
                "() => window.__printCalled && document.querySelector('#print-deck').dataset.ready === 'true'",
                timeout=60000,
            )
            assert page.locator("#print-deck>.slide").count() == core_count
            page.emulate_media(media="print")
            page.pdf(
                path=str(args.output / "1.01.T01_Romain Sacchi.pdf"),
                print_background=True,
                prefer_css_page_size=True,
            )
            page.screenshot(path=str(args.output / "print-preview.png"), full_page=True)
            # The print deck has no repeated IDs or live controls and uses defaults.
            assert page.locator("#print-deck #pulse-window").count() == 0
            assert (
                page.locator(
                    f"#print-deck .setac-slide-{pulse_slide} .pulse-values"
                ).inner_text()
                == default_pulse_cards
            )
            assert (
                "Thank you"
                in page.locator(
                    f"#print-deck .setac-slide-{closing_slide}"
                ).inner_text()
            )
            assert (
                page.locator(f"#print-deck .setac-slide-{core_count} h1").inner_text()
                == "Data sources and model versions"
            )
            assert page.locator("#print-deck #mix-pathway").count() == 0
            context_meta = page.locator(
                "#print-deck .context-panel .js-plotly-plot"
            ).evaluate("e => e._fullLayout.meta")
            assert context_meta == {
                "indicator": "GMST",
                "region": "World",
                "pathway": "SSP2-PkBudg1000",
                "unit": "°C above 1850–1900",
            }
            pulse_meta = page.locator(
                "#print-deck .pulse-results .js-plotly-plot"
            ).evaluate("e => e._fullLayout.meta")
            assert pulse_meta == {"start": 2020, "reference": 2030, "end": 2100}
            mix_meta = page.locator(
                "#print-deck .mix-panels .js-plotly-plot"
            ).evaluate_all("els => els.map(e => e._fullLayout.meta)")
            assert [meta["sector"] for meta in mix_meta] == [
                "Electricity",
                "District heat",
                "Steel",
            ]
            assert all(meta["pathway"] == "SSP2-PkBudg1000" for meta in mix_meta)
            assert page.locator("#print-deck .mix-panels .js-plotly-plot").evaluate_all(
                """plots => plots.every(plot => plot.data.every(trace =>
                    trace.x.join(',') === '2025,2030,2035,2040,2045,2050'))"""
            )
            assert page.locator("#print-deck .mix-panels .js-plotly-plot").evaluate_all(
                """plots => plots.every(plot => [...plot.querySelectorAll('.legendtext')].every(label =>
                    label.getBoundingClientRect().bottom <= plot.getBoundingClientRect().bottom + 1))"""
            ), "A printed mix legend is clipped"
            ids = page.locator("[id]").evaluate_all("els => els.map(e => e.id)")
            assert len(ids) == len(set(ids)), "Duplicate component IDs"
            page.emulate_media(media="screen")
            # 16:9 conference laptop viewport.
            page.set_viewport_size({"width": 1280, "height": 720})
            for index in range(core_count):
                page.evaluate(
                    "index => { window.location.hash = 'slide-' + index; }", index
                )
                page.locator(f"#stage .setac-slide-{index + 1}").wait_for()
                page.wait_for_function(
                    """() => [...document.querySelectorAll('#stage .dash-graph')].every(root => {
                  const plot = root.querySelector('.js-plotly-plot');
                  return plot && plot._fullLayout && plot._fullData.length &&
                    Math.abs(plot._fullLayout.width - root.clientWidth) < 3 &&
                    Math.abs(plot._fullLayout.height - root.clientHeight) < 3;
                })""",
                    polling=100,
                )
                page.screenshot(path=str(args.output / f"laptop-{index + 1:02d}.png"))
        except BaseException:
            print({"errors": errors, "bad_requests": bad_requests}, flush=True)
            if page.locator("#pulse-window").count():
                print(page.locator("#pulse-window").inner_html(), flush=True)
                print(page.locator("#pulse-values").inner_text(), flush=True)
            page.screenshot(path=str(args.output / "failure.png"))
            traceback.print_exc()
            raise
        finally:
            browser.close()
    report = {
        "errors": errors,
        "failed_requests": bad_requests,
        "overflows": overflows,
        "core_slides": core_count,
    }
    (args.output / "browser-report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    assert not errors and not bad_requests and not overflows


if __name__ == "__main__":
    main()
