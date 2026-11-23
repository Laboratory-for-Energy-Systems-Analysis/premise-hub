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
            slide_count = presenter.locator("#selection option").count()
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
                for index in range(slide_count):
                    print(f"{label} {index+1}/{slide_count}", flush=True)
                    go(index)
                    assert presenter.locator("#selection").input_value() == str(index)
                    assert presenter.locator("#cue-text").inner_text()
                    page.screenshot(path=str(args.output / f"{label}-{index+1:02d}.png"))
                    overflow(f"{label}-{index+1}")

            page.set_viewport_size({"width": 1440, "height": 900})
            go(4)
            routing = page.frame_locator("#mcv-route-frame")

            def check_network():
                routing.locator("body[data-ready=true] canvas").wait_for()
                assert "Niveau 0" in routing.locator("#service").inner_text()
                assert routing.locator("#depth").input_value() == "1"
                assert "Activités de coordination" in routing.locator("#status").inner_text()
                assert routing.locator("#branch option").all_text_contents() == [
                    "Toutes les branches", "Construction · 2027–2029",
                    "Exploitation · 2030–2049", "Fin de vie · 2050",
                ]
                routing.locator("#branch").select_option("end-of-life")
                assert routing.locator("#network").evaluate("""() => window.trailsGraph.nodes
                    .every(n => n.depth === 0 || n.year === 2050)""")
                routing.locator("#branch").select_option("all")

            def high_voltage_labels():
                return set(routing.locator("#network").evaluate("""() => {
                    const {nodes, activityName} = window.trailsGraph;
                    return nodes.filter(n => n.name === 'market group for electricity, high voltage').map(activityName);
                }"""))

            check_network()
            assert routing.locator("#network").evaluate("""async () => {
                const expected = ['Construction DACCS', 'Électricité consommée', 'Fin de vie DACCS'];
                for (let frame = 0; frame < 60; frame++) {
                    const labels = window.trailsGraph.activityLabels.map(label => label.name);
                    if (expected.every(name => labels.includes(name))) return true;
                    await new Promise(resolve => requestAnimationFrame(resolve));
                }
                return false;
            }""")
            routing.locator("#depth").select_option("2")
            routing.locator("body[data-ready=true]").wait_for()
            assert "niveaux 0–2" in routing.locator("#status").inner_text()
            assert high_voltage_labels() == {"Électricité de réseau · haute tension"}
            routing.get_by_role("link", name="Routage d’origine").click()
            routing.locator("body[data-ready=true]").wait_for()
            assert routing.locator("#depth").input_value() == "3"
            routing.locator("#view").select_option("grouped")
            assert "groupes d’activités" in routing.locator("#status").inner_text()
            routing.get_by_role("link", name="Premier plan").click()
            check_network()
            page.get_by_role("radio", name="BECCS", exact=True).check()
            page.wait_for_function("() => document.querySelector('#mcv-route-frame').getAttribute('src').endsWith('/beccs.html')")
            routing.get_by_role("link", name="Routage d’origine").wait_for()
            check_network()
            assert high_voltage_labels() == {"Électricité évitée"}
            assert routing.locator("#network").evaluate("""() => window.trailsGraph.nodes.some(n =>
                n.name.startsWith('forest carbon regrowth differential') && n.depth === 1)""")
            page.screenshot(path=str(args.output / "routing-beccs-foreground.png"))
            routing.locator("#view").select_option("grouped")
            assert high_voltage_labels() == {"Électricité évitée"}
            assert routing.locator("#depth option").all_text_contents() == ["0", "0–1", "0–2", "0–3"]
            routing.locator("#depth").select_option("3")
            routing.locator("body[data-ready=true]").wait_for(timeout=30000)
            assert routing.locator("#depth").input_value() == "3"
            assert high_voltage_labels() == {"Électricité évitée", "Électricité de réseau · haute tension"}
            assert routing.locator("#network").evaluate("""() => {
                const {nodes, network, activityName} = window.trailsGraph;
                const forest = nodes.find(n => n.supplyContext && n.years.includes(2131));
                const other = nodes.find(n => n.name === forest?.name && !n.supplyContext);
                if (!forest || !other || activityName(forest) === activityName(other)) return false;
                network.emit('click', {nodes: [forest.id]});
                return true;
            }""")
            assert "La récolte de 2049 prolonge cette demande jusqu’en 2131" in routing.locator("#info").inner_text()
            routing.locator("#branch").select_option("construction")
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
            assert "1,14 t nettes de CO₂" in page.locator("#pulse-takeaway").inner_text()
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
                (True, "PrésentationMCV2026_146_Sacchi_avec_annexes.pdf", slide_count),
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
            report = {"errors": errors, "failed_requests": failed_requests, "overflows": overflows, "core_slides": 10, "full_slides": slide_count}
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
