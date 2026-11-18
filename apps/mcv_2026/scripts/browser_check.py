"""Check the French deck in Chromium and export the actual print layouts."""

import argparse
import json
import os
from pathlib import Path
import re

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8051/mcv-2026/")
    parser.add_argument("--output", type=Path, default=Path("build/mcv-2026"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    errors, failed_requests, overflows = [], [], []
    base = args.url.rstrip("/") + "/"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()
            if context.request.get(base).status == 401:
                password = os.getenv("MCV_2026_PASSWORD")
                if not password:
                    raise RuntimeError("Set MCV_2026_PASSWORD to unlock the presentation")
                login = context.request.post(base, form={"password": password})
                assert login.ok, "Presentation login failed"
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("response", lambda response: failed_requests.append(f"{response.status} {response.url}") if response.status >= 400 else None)
            page.goto(base, wait_until="networkidle")
            page.locator("#stage .mcv-slide-1").wait_for()
            assert page.locator("html").get_attribute("lang") == "fr"
            presenter = context.new_page()
            presenter.goto(base + "presenter", wait_until="networkidle")
            assert "11:40" in presenter.locator("h2").inner_text()
            page.bring_to_front()

            def go(index):
                page.evaluate("i => { location.hash = 'slide-' + i; }", index)
                page.locator(f"#stage .mcv-slide-{index + 1}").wait_for()
                page.wait_for_function("""() => [...document.querySelectorAll('#stage .dash-graph')].every(root => {
                    const plot = root.querySelector('.js-plotly-plot');
                    return plot && plot._fullLayout && plot._fullData.length &&
                        Math.abs(plot._fullLayout.width-root.clientWidth)<3 &&
                        Math.abs(plot._fullLayout.height-root.clientHeight)<3;
                })""", polling=100)
                page.wait_for_function("""() => [...document.querySelectorAll('#stage img')].every(i => i.complete && i.naturalWidth)""")

            def overflow(label):
                elements = page.evaluate("""() => [...document.querySelectorAll('#stage .slide, #stage .slide *')].filter(e => {
                    if(e.closest('.js-plotly-plot,.rc-slider')) return false;
                    const s=getComputedStyle(e);
                    if(s.display==='none'||s.position==='absolute') return false;
                    return e.clientWidth>0 && (e.scrollWidth>e.clientWidth+3 || e.scrollHeight>e.clientHeight+3);
                }).map(e => ({tag:e.tagName,cls:e.className,w:e.clientWidth,sw:e.scrollWidth,h:e.clientHeight,sh:e.scrollHeight}))""")
                if elements:
                    overflows.append({"view": label, "elements": elements})

            for width, height, label in ((1440, 900, "desktop"), (1280, 720, "laptop")):
                page.set_viewport_size({"width": width, "height": height})
                for index in range(14):
                    print(f"{label} {index+1}/14", flush=True)
                    go(index)
                    assert presenter.locator("#selection").input_value() == str(index)
                    assert presenter.locator("#cue-text").inner_text()
                    page.screenshot(path=str(args.output / f"{label}-{index+1:02d}.png"))
                    overflow(f"{label}-{index+1}")

            page.set_viewport_size({"width": 1440, "height": 900})
            go(4)
            routing = page.frame_locator("#mcv-route-frame")
            routing.locator("body[data-ready=true]").wait_for()
            assert "Niveau 0" in routing.locator("#service").inner_text()
            routing.locator("#view").select_option("grouped")
            assert routing.locator("#status").inner_text().find("groupes d’activités") >= 0
            page.get_by_role("radio", name="BECCS", exact=True).check()
            page.wait_for_function("() => document.querySelector('#mcv-route-frame').getAttribute('src').endsWith('/beccs.html')")
            routing.locator("body[data-ready=true]").wait_for()
            routing.locator("#view").select_option("grouped")
            routing.locator("#depth").select_option("4")
            routing.locator("body[data-ready=true]").wait_for(timeout=30000)
            assert routing.locator("#depth").input_value() == "4"
            branch = routing.locator("#branch option").nth(1).get_attribute("value")
            routing.locator("#branch").select_option(branch)
            page.screenshot(path=str(args.output / "routing-beccs.png"))
            go(5)
            page.get_by_text("Courbes séparées", exact=True).click()
            page.wait_for_function("() => document.querySelector('#temporal-chart .js-plotly-plot')._fullLayout.meta.view === 'unstacked'")
            page.get_by_text("Aires empilées", exact=True).click()
            go(7)
            page.get_by_role("radio", name="Jusqu’en 2140", exact=True).check()
            page.wait_for_function("() => document.querySelector('#forcing-chart .js-plotly-plot')._fullLayout.xaxis.range[1]===2140")
            go(8)
            handles = page.locator("#pulse-window [role=slider]")
            handles.nth(2).focus()
            handles.nth(2).press("End")
            page.wait_for_function("() => document.querySelector('#pulse-chart .js-plotly-plot')._fullLayout.meta.end===2300")
            assert "2020–2300" in page.locator("#pulse-takeaway").inner_text()
            assert "1,22 t nettes de CO₂" in page.locator("#pulse-takeaway").inner_text()
            assert "1,13 t nettes de CO₂" in page.locator("#pulse-takeaway").inner_text()
            page.screenshot(path=str(args.output / "pulse-2300.png"))
            handles.nth(0).focus()
            handles.nth(0).press("Home")
            page.wait_for_function("() => document.querySelector('#pulse-chart .js-plotly-plot')._fullLayout.meta.start===2000")
            handles.nth(1).focus()
            handles.nth(1).press("ArrowRight")
            page.wait_for_function("() => document.querySelector('#pulse-chart .js-plotly-plot')._fullLayout.meta.reference===2035")
            assert page.locator("#stage .mcv-slide-9").count() == 1

            go(11)
            page.get_by_role("radio", name="NPi · politiques en place", exact=True).check()
            page.wait_for_function("() => document.querySelector('#mix-electricity .js-plotly-plot')._fullLayout.meta.pathway==='SSP2-NPi'")
            page.locator("#mix-material-sector").click()
            page.get_by_text("Clinker", exact=True).click()
            page.wait_for_function("() => document.querySelector('#mix-material .js-plotly-plot')._fullLayout.meta.sector==='Cement clinker'")

            go(9)
            assert page.locator("#next-button").is_disabled()
            page.locator("#backup-button").click()
            page.locator("#stage .mcv-slide-11").wait_for()
            page.locator("#backup-button").click()
            page.locator("#stage .mcv-slide-10").wait_for()
            page.evaluate("window.print = () => { window.__printCalled = true; };")
            for backups, filename, expected in (
                (False, "PrésentationMCV2026_146_Sacchi.pdf", 10),
                (True, "PrésentationMCV2026_146_Sacchi_avec_annexes.pdf", 14),
            ):
                if backups:
                    page.locator("#print-backups input").check()
                page.evaluate("window.__printCalled=false")
                page.locator("#pdf-button").click()
                page.wait_for_function("() => window.__printCalled && document.querySelector('#print-deck').dataset.ready==='true'", timeout=60000)
                assert page.title() == Path(filename).stem
                assert page.locator("#print-deck>.slide").count() == expected
                assert page.locator("#print-deck #pulse-window").count() == 0
                assert page.locator("#print-deck .pulse-results .js-plotly-plot").evaluate("e => e._fullLayout.meta") == {"start": 2020, "reference": 2030, "end": 2100}
                ids = page.locator("[id]").evaluate_all("els=>els.map(e=>e.id)")
                assert len(ids) == len(set(ids)), "Duplicate component IDs"
                page.emulate_media(media="print")
                page.pdf(path=str(args.output / filename), print_background=True,
                         prefer_css_page_size=True, display_header_footer=False)
                page.emulate_media(media="screen")
                page.evaluate("window.dispatchEvent(new Event('afterprint'))")
                data = (args.output / filename).read_bytes()
                count = len(re.findall(rb"/Type\s*/Page\b", data))
                assert count == expected, f"PDF has {count} pages, expected {expected}"
                assert re.findall(rb"/MediaBox\s*\[([^]]+)\]", data) == [b"0 0 1152 648"] * expected
            report = {"errors": errors, "failed_requests": failed_requests, "overflows": overflows, "core_slides": 10, "full_slides": 14}
            (args.output / "browser-report.json").write_text(json.dumps(report, indent=2))
            print(json.dumps(report, indent=2))
            assert not errors and not failed_requests and not overflows
        except BaseException:
            page.screenshot(path=str(args.output / "failure.png"))
            print(json.dumps({"errors": errors, "failed_requests": failed_requests, "overflows": overflows}, indent=2))
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    main()
