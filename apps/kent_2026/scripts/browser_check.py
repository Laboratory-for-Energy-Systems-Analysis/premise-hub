"""Walk the mounted deck, check overflow, capture screenshots and a PDF."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright
from werkzeug.test import Client
from werkzeug.wrappers import Response


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def install_wsgi_router(context, origin: str):
    """Route browser traffic through the mounted portal without a TCP listener."""
    if str(REPOSITORY_ROOT) not in sys.path:
        sys.path.insert(0, str(REPOSITORY_ROOT))
    from portal.wsgi import application

    client = Client(application, Response)

    def dispatch(route, request):
        parsed = urlsplit(request.url)
        target = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in {"host", "content-length", "connection"}
        }
        response = client.open(
            target,
            method=request.method,
            headers=headers,
            data=request.post_data_buffer,
            base_url=origin,
        )
        response_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in {"content-length", "content-encoding", "transfer-encoding", "connection"}
        }
        route.fulfill(
            status=response.status_code,
            headers=response_headers,
            body=response.get_data(),
        )

    context.route(f"{origin}/**", dispatch)
    return client


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8050/kent-2026/")
    parser.add_argument("--output", type=Path, default=Path("build/kent-2026"))
    parser.add_argument("--browser", type=Path)
    parser.add_argument(
        "--in-process",
        action="store_true",
        help="Serve the mounted WSGI portal through Playwright routing instead of a TCP listener.",
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    errors, bad_requests, overflows = [], [], []
    with sync_playwright() as playwright:
        executable = args.browser
        if executable is None:
            bundled = Path(playwright.chromium.executable_path)
            revision = bundled.parents[4].name.removeprefix("chromium-")
            headless_candidates = list(
                (bundled.parents[5] / f"chromium_headless_shell-{revision}").glob(
                    "chrome-headless-shell-mac-*/chrome-headless-shell"
                )
            )
            if headless_candidates:
                executable = headless_candidates[0]
            elif bundled.is_file():
                executable = bundled
            else:
                brave = Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser")
                if brave.is_file():
                    executable = brave
        launch_options = {"args": ["--single-process"]}
        if executable:
            launch_options["executable_path"] = str(executable)
        browser = playwright.chromium.launch(**launch_options)
        context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        base = args.url.rstrip("/") + "/"
        client = install_wsgi_router(context, base.rstrip("/").removesuffix("/kent-2026")) if args.in_process else None
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("response", lambda response: bad_requests.append(f"{response.status}: {response.url}") if response.status >= 400 else None)
        if client is None:
            assert context.request.get(base).status == 200
            assert context.request.get(base + "presenter").status == 200
            health = context.request.get(base + "health").json()
        else:
            mount = urlsplit(base).path
            assert client.get(mount).status_code == 200
            assert client.get(mount + "presenter").status_code == 200
            health = client.get(mount + "health").get_json()
        assert health["core_slides"] == 12
        page.goto(base, wait_until="networkidle")
        for index in range(health["core_slides"]):
            slide = page.locator(f"#stage #slide-{index}")
            slide.wait_for()
            page.wait_for_function("() => !document.querySelector('#stage [data-dash-is-loading=true]')")
            page.wait_for_function("() => [...document.querySelectorAll('#stage .dash-graph')].every(root => root.querySelector('.js-plotly-plot'))")
            page.screenshot(path=str(args.output / f"slide-{index+1:02d}.png"))
            overflow = page.evaluate("""() => [...document.querySelectorAll('#stage .slide-body, #stage .slide-body *')].filter(e => {
              if (e.closest('.dash-graph')) return false;
              if (e.closest('.rc-slider')) return false;
              if (e.classList.contains('cumulative-chart-wrap')) return false;
              const css=getComputedStyle(e); if(css.display==='none'||css.position==='absolute') return false;
              return e.clientWidth>0 && (e.scrollWidth>e.clientWidth+3 || e.scrollHeight>e.clientHeight+3);
            }).map(e => ({tag:e.tagName,cls:String(e.className),w:e.clientWidth,sw:e.scrollWidth,h:e.clientHeight,sh:e.scrollHeight}))""")
            if overflow:
                overflows.append({"slide": index + 1, "elements": overflow})
            if index == 4:
                zoom_buttons = page.locator("#stage .capability-zoom-button")
                assert zoom_buttons.count() == 5
                zoom_buttons.nth(3).click()
                modal = page.locator("#capability-zoom-modal")
                modal.wait_for(state="visible")
                assert page.locator("#capability-zoom-title").inner_text() == "Year-specific charging mix"
                page.screenshot(path=str(args.output / "slide-05-zoom-charging.png"))
                page.keyboard.press("Escape")
                modal.wait_for(state="hidden")
            if index == 5:
                family_cards = page.locator("#stage .mobility-family-card")
                assert family_cards.count() == 4
                assert page.locator("#stage .mobility-stack-candidate").count() == 22
                assert page.locator("#stage .mobility-analysis-card").count() == 2
                family_cards.nth(2).click()
                family_modal = page.locator("#family-zoom-modal")
                family_modal.wait_for(state="visible")
                assert page.locator("#family-zoom-title").inner_text() == "City buses · life-cycle contributions"
                assert family_modal.locator(".mobility-stack-candidate").count() == 7
                page.screenshot(path=str(args.output / "slide-06-zoom-buses.png"))
                page.keyboard.press("Escape")
                family_modal.wait_for(state="hidden")
            if index == 8:
                page.get_by_text("Fine particles", exact=True).click()
                page.wait_for_function("() => document.querySelector('#cumulative-summary')?.innerText.includes('incidences')")
                assert "keeping advantage" in page.locator("#cumulative-summary").inner_text()
                page.screenshot(path=str(args.output / "slide-09-fine-particles.png"))
                page.get_by_text("Climate change", exact=True).click()
                page.wait_for_function("() => document.querySelector('#cumulative-summary')?.innerText.includes('CO₂-eq')")
                fuel_slider = page.locator("#cumulative-fuel [role=slider]")
                fuel_slider.press("ArrowRight")
                fuel_slider.press("ArrowRight")
                fuel_slider.press("ArrowRight")
                page.wait_for_function("() => document.querySelector('#cumulative-summary')?.innerText.includes('E85 · corn')")
                assert "sustained break-even" in page.locator("#cumulative-summary").inner_text()
                page.screenshot(path=str(args.output / "slide-09-e85.png"))
            if index == 9:
                assert page.locator("#decision-landscape .heatmaplayer").count() == 1
                page.locator("#landscape-horizon").get_by_text("2060", exact=True).click()
                page.locator("#landscape-year").get_by_text("2035", exact=True).click()
                page.wait_for_function("() => document.querySelector('#decision-landscape')?.innerText.includes('retired')")
                page.screenshot(path=str(args.output / "slide-10-horizon-2060.png"))
            if index < health["core_slides"] - 1:
                if index == 0:
                    page.keyboard.press("ArrowRight")
                else:
                    page.locator("#next-button").click()
        assert page.locator("#next-button").is_disabled()
        assert health["backup_slides"] == 0
        assert page.locator("#backup-button, #print-backups").count() == 0
        # Mount the deterministic print deck without invoking a native dialog.
        page.evaluate("window.print = () => { window.__printed = true; }")
        page.locator("#pdf-button").click()
        page.wait_for_function("() => window.__printed === true", timeout=60000)
        page.wait_for_function(
            "count => document.querySelectorAll('#print-deck > .presentation-slide').length === count",
            arg=health["core_slides"],
        )
        assert page.locator("#print-deck > .presentation-slide").count() == health["core_slides"]
        page.emulate_media(media="print")
        print_overflows = page.evaluate("""() => [...document.querySelectorAll('#print-deck > .presentation-slide')].flatMap((slide, index) =>
          [...slide.querySelectorAll('.slide-body, .slide-body *')].filter(e => {
            if (e.closest('.dash-graph')) return false;
            const css=getComputedStyle(e); if(css.display==='none'||css.position==='absolute') return false;
            return e.clientWidth>0 && (e.scrollWidth>e.clientWidth+3 || e.scrollHeight>e.clientHeight+3);
          }).map(e => ({slide:index+1,tag:e.tagName,cls:String(e.className),w:e.clientWidth,sw:e.scrollWidth,h:e.clientHeight,sh:e.scrollHeight})))""")
        for item in print_overflows:
            overflows.append({"slide": f"print-{item.pop('slide')}", "elements": [item]})
        pdf_path = args.output / "Kent_Seminar_Keep_or_Replace_Romain_Sacchi.pdf"
        page.pdf(path=str(pdf_path), print_background=True, width="16in", height="9in")
        browser.close()
    pdf_data = pdf_path.read_bytes()
    pdf_pages = pdf_data.count(b"/Type /Page\n")
    if not pdf_data.startswith(b"%PDF-") or pdf_pages != health["core_slides"]:
        errors.append(f"PDF integrity check failed: header={pdf_data[:8]!r}, pages={pdf_pages}")
    report = {"console_errors": errors, "bad_requests": bad_requests, "overflows": overflows, "pdf_pages": pdf_pages}
    (args.output / "browser-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if errors or bad_requests or overflows:
        raise SystemExit(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
