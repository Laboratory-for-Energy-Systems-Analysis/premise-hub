"""Capture browser callbacks and replay paced visitors against a presentation.

Run only against an explicitly authorized target. This models HTTP traffic, not
browser rendering. Static asset caching, PDF printing and mixed-app workloads
are outside the default test. Each thread represents one paced visitor.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
import re
import sys
from threading import Event, Lock
import time
from urllib.parse import urlsplit

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def now():
    return datetime.now(timezone.utc).isoformat()


def percentile(values, q):
    if not values:
        return None
    values = sorted(values)
    return round(values[max(0, math.ceil(q * len(values)) - 1)], 3)


def capture(args):
    from playwright.sync_api import sync_playwright
    from scripts.browser_smoke import launch_chromium

    target = args.url.rstrip("/") + "/"
    origin = urlsplit(target).netloc
    groups = []
    pending = set()
    last_request = [time.monotonic()]
    current = {"name": "bootstrap", "requests": []}
    groups.append(current)

    def record(request):
        parts = urlsplit(request.url)
        if parts.netloc != origin:
            return
        dynamic = request.method == "POST" and parts.path.endswith(
            "/_dash-update-component"
        )
        graph = "/routing/" in parts.path and parts.path.endswith(".json")
        shell = request.method == "GET" and (
            request.url == target
            or parts.path.endswith(("/_dash-layout", "/_dash-dependencies"))
        )
        if dynamic or graph or shell:
            pending.add(request)
            last_request[0] = time.monotonic()
            current["requests"].append(
                {
                    "method": request.method,
                    "url": request.url,
                    "json": request.post_data_json if dynamic else None,
                }
            )

    def finished(request):
        pending.discard(request)

    def settle(page):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            page.wait_for_timeout(100)
            if not pending and time.monotonic() - last_request[0] > .6:
                return
        raise RuntimeError(f"Presentation requests did not settle: {len(pending)} pending")

    with sync_playwright() as playwright:
        browser = launch_chromium(playwright)
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        page.on("request", record)
        page.on("requestfinished", finished)
        page.on("requestfailed", finished)
        page.goto(target, wait_until="domcontentloaded")
        page.locator(".snu-slide-0").wait_for()
        settle(page)
        for slide in args.slides:
            current = {"name": f"slide-{slide}", "slide": slide, "requests": []}
            groups.append(current)
            page.evaluate("i => {location.hash='slide-'+i}", slide)
            page.locator(f".snu-slide-{slide}").wait_for()
            settle(page)
            print(json.dumps({"captured": current["name"], "requests": len(current["requests"])}), flush=True)
        browser.close()
    if not all(group["requests"] for group in groups):
        raise RuntimeError("An empty browser action was captured")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"url": target, "captured_at": now(), "groups": groups}, indent=2)
        + "\n"
    )
    print(
        json.dumps(
            {
                "model": str(args.output),
                "actions": [
                    {"name": g["name"], "requests": len(g["requests"])} for g in groups
                ],
            }
        ),
        flush=True,
    )


def stage(args, model, users):
    stop, lock = Event(), Lock()
    requests_log, actions_log, metrics = [], [], []
    reason = []
    start = time.monotonic()
    since = time.time()
    stage_start = now()
    output = args.output / f"{users}-users"
    output.mkdir(parents=True, exist_ok=True)
    request_file = (output / "requests.jsonl").open("w")

    def halt(message):
        with lock:
            if not reason:
                reason.append(message)
        stop.set()

    def send(session, item, user, action):
        started = time.monotonic()
        entry = {
            "at": now(),
            "user": user,
            "action": action,
            "method": item["method"],
            "path": urlsplit(item["url"]).path,
        }
        try:
            response = session.request(
                item["method"], item["url"], json=item["json"], timeout=(5, 15)
            )
            entry.update(
                status=response.status_code, bytes=len(response.content), error=None
            )
            if response.status_code not in (200, 204):
                entry["error"] = f"HTTP {response.status_code}"
            elif item["method"] == "POST" and response.status_code == 200:
                body = response.json()
                if not isinstance(body.get("response"), dict):
                    entry["error"] = "Invalid Dash response"
        except Exception as exc:
            entry.update(status=None, bytes=0, error=f"{type(exc).__name__}: {exc}")
        entry["seconds"] = round(time.monotonic() - started, 4)
        with lock:
            requests_log.append(entry)
            request_file.write(json.dumps(entry) + "\n")
            request_file.flush()
            recent = requests_log[-100:]
            errors = sum(bool(row["error"]) for row in recent)
        if errors >= 3 and errors / len(recent) > 0.02:
            halt("At least three request failures and more than 2% recent errors")
        return not entry["error"]

    def visit(user):
        rng = random.Random(20261110 + user + users * 100)
        if stop.wait(user / args.ramp_per_second):
            return
        with requests.Session() as session:
            session.headers.update(
                {
                    "User-Agent": "premise-hub-authorized-load-test/1.0",
                    "X-Load-Test": f"{args.run_id}-{users}",
                }
            )
            groups = model["groups"]
            sequence = [groups[0]]
            index = user % (len(groups) - 1)
            while not stop.is_set() and time.monotonic() - start < args.seconds:
                group = (
                    sequence.pop()
                    if sequence
                    else groups[1 + index % (len(groups) - 1)]
                )
                index += 1
                began = time.monotonic()
                success = True
                for item in group["requests"]:
                    if stop.is_set():
                        return
                    success = send(session, item, user, group["name"]) and success
                with lock:
                    actions_log.append(
                        {
                            "at": now(),
                            "user": user,
                            "name": group["name"],
                            "seconds": round(time.monotonic() - began, 4),
                            "success": success,
                        }
                    )
                if group["name"] != "bootstrap":
                    stop.wait(rng.uniform(args.think_min, args.think_max))

    pool = ThreadPoolExecutor(max_workers=users)
    futures = [pool.submit(visit, user) for user in range(users)]
    log_position = args.runtime_log.stat().st_size if args.runtime_log.exists() else 0
    r14_times, slow_windows = [], 0
    last_metric = time.monotonic()
    try:
        while not stop.wait(2) and time.monotonic() - start < args.seconds:
            if args.runtime_log.exists():
                with args.runtime_log.open() as stream:
                    stream.seek(log_position)
                    lines = stream.readlines()
                    log_position = stream.tell()
                for line in lines:
                    if any(
                        text in line
                        for text in (
                            "Error R15",
                            "State changed from up to crashed",
                            "Stopping process with SIGKILL",
                        )
                    ):
                        halt("Heroku reported a memory kill or crashed dyno")
                    if "Error R14" in line:
                        r14_times.append(time.monotonic())
                        if len(r14_times) >= 2 and r14_times[-1] - r14_times[-2] < 65:
                            halt("Repeated Heroku R14 memory warnings")
                    values = {
                        key: float(value)
                        for key, value in re.findall(r"sample#([\w_]+)=([\d.]+)", line)
                    }
                    if values:
                        metrics.append({"at": line.split(" ")[0], **values})
                        last_metric = time.monotonic()
                if time.monotonic() - last_metric > 50:
                    halt("Runtime metric stream unavailable for over 50 seconds")
                if int(time.monotonic() - start) % 20 < 2:
                    with lock:
                        recent = requests_log[-100:]
                        latency = percentile([r["seconds"] for r in recent], 0.95)
                        count = len(requests_log)
                    slow_windows = (
                        slow_windows + 1 if latency is not None and latency > 8 else 0
                    )
                    if slow_windows >= 2:
                        halt(
                            "Request p95 above 8 seconds in two consecutive monitoring windows"
                        )
                    print(
                        json.dumps(
                            {
                                "users": users,
                                "elapsed": round(time.monotonic() - start),
                                "requests": count,
                                "recent_p95_seconds": latency,
                                "metrics": metrics[-1] if metrics else None,
                            }
                        ),
                        flush=True,
                    )
    finally:
        stop.set()
        pool.shutdown(wait=True)
        request_file.close()
    for future in futures:
        future.result()
    elapsed = time.monotonic() - start
    errors = [row for row in requests_log if row["error"]]
    latencies = [row["seconds"] for row in requests_log]
    actions = [row["seconds"] for row in actions_log if row["name"] != "bootstrap"]
    report = {
        "users": users,
        "started_at": stage_start,
        "finished_at": now(),
        "epoch_start": since,
        "seconds": round(elapsed, 2),
        "requests": len(requests_log),
        "errors": len(errors),
        "error_examples": errors[:5],
        "request_p50": percentile(latencies, 0.5),
        "request_p95": percentile(latencies, 0.95),
        "request_max": max(latencies, default=None),
        "actions": len(actions),
        "action_p95": percentile(actions, 0.95),
        "requests_per_second": round(len(requests_log) / elapsed, 2),
        "metrics": metrics,
        "stopped_reason": reason,
        "settings": {
            "think_seconds": [args.think_min, args.think_max],
            "ramp_users_per_second": args.ramp_per_second,
        },
    }
    (output / "actions.json").write_text(json.dumps(actions_log, indent=2) + "\n")
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                key: value
                for key, value in report.items()
                if key not in ("metrics", "error_examples")
            }
        ),
        flush=True,
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    capture_parser = sub.add_parser("capture")
    capture_parser.add_argument("--url", required=True)
    capture_parser.add_argument(
        "--slides", type=int, nargs="+", default=[5, 11, 14, 15, 17, 18, 19]
    )
    capture_parser.add_argument("--output", type=Path, required=True)
    run = sub.add_parser("run")
    run.add_argument("--model", type=Path, required=True)
    run.add_argument("--users", type=int, nargs="+", default=[10, 25, 50])
    run.add_argument("--seconds", type=int, default=120)
    run.add_argument("--think-min", type=float, default=15)
    run.add_argument("--think-max", type=float, default=25)
    run.add_argument("--ramp-per-second", type=float, default=2)
    run.add_argument("--cooldown", type=int, default=25)
    run.add_argument("--runtime-log", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--run-id", default="2026-11-10")
    args = parser.parse_args()
    if args.command == "capture":
        capture(args)
        return
    model = json.loads(args.model.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    reports = []
    for users in args.users:
        report = stage(args, model, users)
        reports.append(report)
        (args.output / "summary.json").write_text(
            json.dumps({"model": str(args.model), "stages": reports}, indent=2) + "\n"
        )
        if report["stopped_reason"] or report["errors"]:
            break
        if users != args.users[-1]:
            time.sleep(args.cooldown)


if __name__ == "__main__":
    main()
