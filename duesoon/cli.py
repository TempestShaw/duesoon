"""Command line entry point.

  duesoon setup                 first-run wizard
  duesoon [--days N]            print the list
  duesoon --open                write the dashboard and open it
  duesoon --ics FILE            export a calendar file
"""

import argparse
import sys
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import config, wizard
from .api import CanvasError, fetch_planner_items
from .gradescope import GradescopeError, fetch_gradescope
from .ics import render_ics
from .items import Task, to_tasks
from .merge import merge
from .render import render_html, render_text

DEFAULT_DAYS_AHEAD = 30
DEFAULT_DAYS_BACK = 60
DEFAULT_URL = "https://canvas.cmu.edu"
DEFAULT_DASHBOARD = config.CONFIG_DIR / "dashboard.html"


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="duesoon", description="Everything you still owe on Canvas and Gradescope.")
    p.add_argument("command", nargs="?", choices=["list", "setup"], default="list")
    p.add_argument("--days", type=int, default=DEFAULT_DAYS_AHEAD, help="days ahead to include (default 30)")
    p.add_argument("--html", type=Path, help="write the HTML dashboard to this path")
    p.add_argument("--open", action="store_true", help="write the dashboard and open it in a browser")
    p.add_argument("--ics", type=Path, help="write a calendar (.ics) file to this path")
    return p.parse_args(argv)


def collect(env: dict[str, str], days: int, now: datetime) -> list[Task]:
    base_url = env.get("CANVAS_URL", DEFAULT_URL).rstrip("/")
    raw = fetch_planner_items(base_url, env["CANVAS_TOKEN"], now, DEFAULT_DAYS_BACK, days)
    tasks = to_tasks(raw, base_url, now)
    if not (env.get("GRADESCOPE_EMAIL") and env.get("GRADESCOPE_PASSWORD")):
        return tasks
    try:
        gs = fetch_gradescope(env["GRADESCOPE_EMAIL"], env["GRADESCOPE_PASSWORD"])
    except GradescopeError as err:
        print(f"Skipping Gradescope: {err}", file=sys.stderr)
        return tasks
    return merge(tasks, gs, now, now + timedelta(days=days), DEFAULT_DAYS_BACK)


def write(path: Path, content: str, label: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"{label} written to {path.resolve()}")
    return path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.command == "setup":
        return wizard.run()

    env = config.load()
    if not env.get("CANVAS_TOKEN"):
        print("Not set up yet. Run: duesoon setup", file=sys.stderr)
        return 1
    now = datetime.now(timezone.utc).astimezone()
    try:
        tasks = collect(env, args.days, now)
    except CanvasError as err:
        print(err, file=sys.stderr)
        return 1

    print(render_text(tasks))
    html_path = args.html or (DEFAULT_DASHBOARD if args.open else None)
    if html_path:
        write(html_path, render_html(tasks, now), "\nDashboard")
        if args.open:
            webbrowser.open(html_path.resolve().as_uri())
    if args.ics:
        write(args.ics, render_ics(tasks, now), "Calendar")
    return 0
