"""Export tasks as an iCalendar file (Apple / Google / Outlook calendar)."""

import hashlib
from datetime import datetime, timezone

from .items import MISSING, Task

_STAMP = "%Y%m%dT%H%M%SZ"


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _event(task: Task, stamp: str) -> list[str]:
    due = task.due.astimezone(timezone.utc).strftime(_STAMP)
    uid = hashlib.sha1(task.url.encode()).hexdigest()
    prefix = "⚠️ MISSING " if task.status == MISSING else ""
    return [
        "BEGIN:VEVENT",
        f"UID:{uid}@duesoon",
        f"DTSTAMP:{stamp}",
        f"DTSTART:{due}",
        f"DTEND:{due}",
        f"SUMMARY:{_escape(f'{prefix}[{task.course}] {task.title}')}",
        f"URL:{task.url}",
        "BEGIN:VALARM",
        "TRIGGER:-P1D",
        "ACTION:DISPLAY",
        "DESCRIPTION:Due in 24 hours",
        "END:VALARM",
        "END:VEVENT",
    ]


def render_ics(tasks: list[Task], now: datetime) -> str:
    stamp = now.astimezone(timezone.utc).strftime(_STAMP)
    events = [line for t in tasks if t.due for line in _event(t, stamp)]
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//duesoon//EN", *events, "END:VCALENDAR"]
    return "\r\n".join(lines) + "\r\n"
