"""Combine Canvas tasks with Gradescope assignments."""

import re
from datetime import datetime, timedelta

from .gradescope import GsAssignment
from .items import Task, status_for

DEFAULT_LOOKBACK_DAYS = 60
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def norm(title: str) -> str:
    return _NON_ALNUM.sub(" ", title.lower()).strip()


def merge(
    tasks: list[Task], gs: list[GsAssignment], now: datetime, until: datetime,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> list[Task]:
    """Drop Canvas tasks already submitted on Gradescope; add Gradescope-only open work."""
    since = now - timedelta(days=lookback_days)
    submitted = {norm(a.title) for a in gs if a.submitted}
    kept = [t for t in tasks if norm(t.title) not in submitted]
    known = {norm(t.title) for t in tasks}
    extra = [
        Task(
            title=a.title,
            course=f"{a.course} (Gradescope)",
            due=a.due,
            url=a.url,
            status=status_for(a.due, now),
        )
        for a in gs
        if not a.submitted and a.due and since <= a.due <= until and norm(a.title) not in known
    ]
    return sorted([*kept, *extra], key=lambda t: t.due or until)
