"""Turn raw Canvas planner items into a classified to-do list."""

from dataclasses import dataclass
from datetime import datetime, timedelta

# Planner types that represent work to hand in (calendar events / announcements are noise).
WORK_TYPES = frozenset({"assignment", "quiz", "discussion_topic", "planner_note"})

MISSING = "missing"  # Canvas itself flags it missing
PAST_DUE = "past_due"  # due date passed, not submitted on Canvas (may be on Gradescope etc.)
THIS_WEEK = "this_week"  # due within the next WEEK_DAYS
UPCOMING = "upcoming"
WEEK_DAYS = 7


@dataclass(frozen=True)
class Task:
    title: str
    course: str
    due: datetime | None
    url: str
    status: str


def is_done(item: dict) -> bool:
    sub = item.get("submissions") or {}
    override = item.get("planner_override") or {}
    return any((sub.get("submitted"), sub.get("excused"), sub.get("graded"), override.get("marked_complete")))


def parse_due(item: dict) -> datetime | None:
    plannable = item.get("plannable") or {}
    raw = plannable.get("due_at") or item.get("plannable_date")
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone() if raw else None


def classify(item: dict, now: datetime) -> str:
    if (item.get("submissions") or {}).get("missing"):
        return MISSING
    return status_for(parse_due(item), now)


def status_for(due: datetime | None, now: datetime) -> str:
    if due is None:
        return UPCOMING
    if due < now:
        return PAST_DUE
    return THIS_WEEK if due <= now + timedelta(days=WEEK_DAYS) else UPCOMING


def to_tasks(raw: list[dict], base_url: str, now: datetime) -> list[Task]:
    """Keep unfinished work items, classified and sorted by due date."""
    tasks = [
        Task(
            title=(item.get("plannable") or {}).get("title", "?").strip(),
            course=item.get("context_name", "?"),
            due=parse_due(item),
            url=base_url + item.get("html_url", ""),
            status=classify(item, now),
        )
        for item in raw
        if item.get("plannable_type") in WORK_TYPES and not is_done(item)
    ]
    return sorted(tasks, key=lambda t: t.due or now)
