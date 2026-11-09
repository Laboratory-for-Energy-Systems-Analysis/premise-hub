"""Measure each app in a fresh process, including a serialized slide walkthrough.

Run with the same Python/dependencies as production. macOS RSS is not directly
comparable with Heroku/Linux; compare before/after using the same environment.
This is sequential traffic, not a concurrent-user or browser PDF benchmark.
"""

from __future__ import annotations

import argparse
import gc
import importlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
APPS = (
    "ccus_webinar",
    "lca_time",
    "setac_2026",
    "seoul_2026",
    "kent_2026",
    "workshop",
    "scenario_explorer",
)


def memory():
    gc.collect()
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak /= 1024**2 if sys.platform == "darwin" else 1024
    try:
        rss = (
            int(
                subprocess.check_output(
                    ["ps", "-o", "rss=", "-p", str(os.getpid())],
                    stderr=subprocess.DEVNULL,
                )
            )
            / 1024
        )
    except (OSError, subprocess.CalledProcessError):
        rss = None
    return {
        "rss_mib": round(rss, 1) if rss is not None else None,
        "peak_mib": round(peak, 1),
    }


def profile(name):
    sys.path.insert(0, str(ROOT))
    started = time.monotonic()
    if name == "portal":
        importlib.import_module("portal.wsgi")
        report = {"app": name, "startup": memory()}
        report["apps"] = [profile(app) for app in APPS]
        report["warm"] = memory()
        report["seconds"] = round(time.monotonic() - started, 2)
        return report
    app = importlib.import_module(f"apps.{name}.app")
    report = {"app": name, "startup": memory(), "slides": []}
    if name == "scenario_explorer":
        frame = app.get_dataset(app.DEFAULT_DATASET)
        report["dataset_mib"] = round(frame.memory_usage(deep=True).sum() / 1024**2, 1)
        # Exercise a cached hit too: SimpleCache deserializes another DataFrame.
        second = app.get_dataset(app.DEFAULT_DATASET)
        assert len(second) == len(frame)
        del frame, second
    else:
        from plotly.utils import PlotlyJSONEncoder

        if name == "workshop":
            count = app.LAST_SLIDE + 1
            render = lambda i: app.render_slide(
                i,
                0,
                {"A": 0, "B": 0, "C": 0, "D": 0},
                {"sector": "Electricity", "year": 2060, "mode": "share"},
                {},
                "image",
            )
        elif name in ("lca_time", "ccus_webinar"):
            count = app.LAST_SLIDE + 1
            render = app.render_slide
        else:
            count = len(app.ALL_SLIDES)
            render = app.render_slide
        for index in range(count):
            slide = render(index)
            payload = json.dumps(slide, cls=PlotlyJSONEncoder)
            size = len(payload)
            del slide, payload
            report["slides"].append({"index": index, "json_bytes": size, **memory()})
    report["warm"] = memory()
    report["seconds"] = round(time.monotonic() - started, 2)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apps", nargs="+", choices=(*APPS, "portal"), default=APPS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker", choices=(*APPS, "portal"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(profile(args.worker)))
        return
    reports = []
    for name in args.apps:
        child = subprocess.run(
            [sys.executable, __file__, "--worker", name],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if child.returncode:
            print(child.stdout + child.stderr, file=sys.stderr)
            raise SystemExit(child.returncode)
        report = json.loads(child.stdout.strip().splitlines()[-1])
        reports.append(report)
        print(
            json.dumps({k: report[k] for k in ("app", "startup", "warm", "seconds")}),
            flush=True,
        )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(
                {"platform": sys.platform, "python": sys.version, "apps": reports},
                indent=2,
            )
            + "\n"
        )


if __name__ == "__main__":
    main()
