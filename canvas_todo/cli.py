"""Command line entry point: python -m canvas_todo [--days N] [--html PATH]."""

import argparse
import os
import sys
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .api import CanvasError, fetch_planner_items
from .gradescope import GradescopeError, fetch_gradescope
from .items import to_tasks
from .merge import merge
from .render import render_html, render_text

DEFAULT_DAYS_AHEAD = 30
DEFAULT_DAYS_BACK = 60
DEFAULT_URL = "https://canvas.cmu.edu"


def load_env(path: Path) -> dict[str, str]:
    """Read KEY=VALUE lines from a .env file (missing file -> empty)."""
    if not path.is_file():
        return {}
    pairs = (line.split("=", 1) for line in path.read_text().splitlines() if "=" in line and not line.startswith("#"))
    return {k.strip(): v.strip().strip('"') for k, v in pairs}


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="List unfinished Canvas work.")
    p.add_argument("--days", type=int, default=DEFAULT_DAYS_AHEAD, help="days ahead to include")
    p.add_argument("--html", type=Path, help="write an HTML dashboard to this path")
    p.add_argument("--open", action="store_true", help="open the HTML dashboard in a browser")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    env = {**load_env(Path.cwd() / ".env"), **os.environ}
    token = env.get("CANVAS_TOKEN")
    if not token:
        print("CANVAS_TOKEN is not set (put it in .env or the environment).", file=sys.stderr)
        return 1
    base_url = env.get("CANVAS_URL", DEFAULT_URL).rstrip("/")
    now = datetime.now(timezone.utc).astimezone()

    try:
        raw = fetch_planner_items(base_url, token, now, DEFAULT_DAYS_BACK, args.days)
    except CanvasError as err:
        print(err, file=sys.stderr)
        return 1

    tasks = to_tasks(raw, base_url, now)
    if env.get("GRADESCOPE_EMAIL") and env.get("GRADESCOPE_PASSWORD"):
        try:
            gs = fetch_gradescope(env["GRADESCOPE_EMAIL"], env["GRADESCOPE_PASSWORD"])
            tasks = merge(tasks, gs, now, now + timedelta(days=args.days), DEFAULT_DAYS_BACK)
        except GradescopeError as err:
            print(f"Skipping Gradescope: {err}", file=sys.stderr)
    print(render_text(tasks))
    if args.html:
        args.html.write_text(render_html(tasks, now), encoding="utf-8")
        print(f"\nDashboard written to {args.html.resolve()}")
        if args.open:
            webbrowser.open(args.html.resolve().as_uri())
    return 0
