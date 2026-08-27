#!/usr/bin/env python3
"""Audit the computed size of every visible text node in the slide deck."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop.config import CORE_LAST_SLIDE, LAST_SLIDE

TEXT_AUDIT_SCRIPT = r"""
root => {
  const rows = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const text = node.nodeValue.replace(/\s+/g, ' ').trim();
    if (!text) continue;
    const el = node.parentElement;
    if (!el) continue;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    if (
      style.display === 'none' ||
      style.visibility === 'hidden' ||
      Number(style.opacity) === 0 ||
      rect.width < 1 ||
      rect.height < 1
    ) continue;
    const className = typeof el.className === 'string'
      ? el.className
      : (el.className && el.className.baseVal) || '';
    const ancestry = [];
    let ancestor = el;
    while (ancestor && ancestry.length < 5) {
      const ancestorClass = typeof ancestor.className === 'string'
        ? ancestor.className.trim().split(/\s+/).filter(Boolean).slice(0, 3).join('.')
        : '';
      ancestry.push(
        ancestor.tagName.toLowerCase() +
        (ancestor.id ? '#' + ancestor.id : '') +
        (ancestorClass ? '.' + ancestorClass : '')
      );
      if (ancestor === root) break;
      ancestor = ancestor.parentElement;
    }
    rows.push({
      px: Number.parseFloat(style.fontSize),
      text: text.slice(0, 120),
      tag: el.tagName.toLowerCase(),
      id: el.id || '',
      className,
      ancestry: ancestry.join(' < '),
      source: Boolean(el.closest('.source-note')),
      plotly: Boolean(el.closest('.js-plotly-plot')),
      overflow_x: Math.max(0, el.scrollWidth - el.clientWidth),
      overflow_y: Math.max(0, el.scrollHeight - el.clientHeight),
    });
  }
  return rows;
}
"""


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
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--threshold", type=float, default=10.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        browser = launch_chromium(playwright)
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        page.goto(args.url, wait_until="networkidle")
        for slide in range(LAST_SLIDE + 1):
            page.wait_for_selector(".slide")
            visible_graphs = page.locator(".graph-frame:visible")
            if visible_graphs.count():
                page.wait_for_timeout(500)
            page.wait_for_timeout(250)
            title_locator = page.locator(".slide-title")
            if not title_locator.count():
                title_locator = page.locator(".slide h1")
            title = title_locator.first.text_content() if title_locator.count() else ""
            rows = page.locator(".slide").evaluate(TEXT_AUDIT_SCRIPT)
            flagged = [row for row in rows if row["px"] < args.threshold]
            content = [row for row in flagged if not row["source"]]
            sizes = Counter(round(row["px"], 2) for row in content)
            smallest = sorted(content, key=lambda row: (row["px"], row["text"]))[:20]
            overflowing = [
                row
                for row in rows
                if (row["overflow_x"] > 1 or row["overflow_y"] > 1)
                and not row["source"]
                and not row["plotly"]
            ]
            report.append(
                {
                    "slide": slide + 1,
                    "title": " ".join(title.split()),
                    "minimum_px": min((row["px"] for row in rows), default=None),
                    "flagged_content_count": len(content),
                    "flagged_source_count": len(flagged) - len(content),
                    "content_sizes": dict(sorted(sizes.items())),
                    "smallest_content": smallest,
                    "overflowing_content": overflowing,
                }
            )
            if slide < LAST_SLIDE:
                if slide == CORE_LAST_SLIDE:
                    page.get_by_role("button", name="Backup", exact=True).click()
                else:
                    page.locator("#next-button").click()
        browser.close()

    payload = {
        "viewport": [args.width, args.height],
        "threshold_px": args.threshold,
        "slides": report,
    }
    rendered = json.dumps(payload, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
