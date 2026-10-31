"""Render tasks as plain text or a self-contained HTML dashboard."""

from datetime import datetime
from html import escape

from .items import MISSING, PAST_DUE, UPCOMING, Task

SECTIONS = (
    (MISSING, "Missing"),
    (PAST_DUE, "Past due, not submitted on Canvas"),
    (UPCOMING, "Upcoming"),
)
SOON_HOURS = 48


def fmt_due(due: datetime | None) -> str:
    return due.strftime("%a %m-%d %H:%M") if due else "no due date"


def render_text(tasks: list[Task]) -> str:
    lines: list[str] = []
    for status, label in SECTIONS:
        rows = [t for t in tasks if t.status == status]
        lines = [*lines, f"\n=== {label} ({len(rows)}) ==="]
        lines = [*lines, *(f"  {fmt_due(t.due):<16} [{t.course}] {t.title}" for t in rows)]
    return "\n".join(lines)


def _row(task: Task, now: datetime) -> str:
    soon = task.due and 0 <= (task.due - now).total_seconds() <= SOON_HOURS * 3600
    cls = "soon" if soon else ""
    return (
        f'<li class="{cls}"><time>{escape(fmt_due(task.due))}</time>'
        f'<a href="{escape(task.url)}" target="_blank" rel="noopener">{escape(task.title)}</a>'
        f"<span>{escape(task.course)}</span></li>"
    )


def render_html(tasks: list[Task], now: datetime) -> str:
    sections = ""
    for status, label in SECTIONS:
        rows = [t for t in tasks if t.status == status]
        body = "".join(_row(t, now) for t in rows) or "<li class='empty'>Nothing here 🎉</li>"
        sections += f'<section class="{status}"><h2>{label} <b>{len(rows)}</b></h2><ul>{body}</ul></section>'
    return HTML_TEMPLATE.format(updated=escape(now.strftime("%Y-%m-%d %H:%M")), sections=sections)


HTML_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Due Soon</title>
<style>
:root{{--bg:#fafafa;--fg:#1a1a1a;--muted:#6b6b6b;--card:#fff;--line:#e5e5e5;--red:#c62828;--amber:#b26a00;--blue:#1f5fbf}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151515;--fg:#eee;--muted:#9a9a9a;--card:#1f1f1f;--line:#333;--red:#ef7a7a;--amber:#e0a84a;--blue:#7aa7ef}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:24px 16px}}
h1{{margin:0}} .updated{{color:var(--muted);margin:4px 0 24px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:10px;margin-bottom:20px;padding:4px 16px}}
h2{{font-size:16px}} h2 b{{color:var(--muted);font-weight:500}}
.missing h2{{color:var(--red)}} .past_due h2{{color:var(--amber)}} .upcoming h2{{color:var(--blue)}}
ul{{list-style:none;margin:0;padding:0}}
li{{display:grid;grid-template-columns:130px 1fr;gap:2px 12px;padding:10px 0;border-top:1px solid var(--line)}}
li time{{color:var(--muted);font-variant-numeric:tabular-nums}} li span{{grid-column:2;color:var(--muted);font-size:13px}}
li.soon time{{color:var(--red);font-weight:600}} li.empty{{display:block;color:var(--muted)}}
a{{color:inherit;text-decoration:none}} a:hover{{text-decoration:underline}}
@media (max-width:520px){{li{{grid-template-columns:1fr}} li span{{grid-column:1}}}}
</style></head><body><main>
<h1>Due Soon</h1><p class="updated">Updated {updated}</p>
{sections}
</main></body></html>
"""
