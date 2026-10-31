from datetime import datetime, timedelta, timezone

from canvas_todo.api import next_link
from canvas_todo.cli import load_env
from canvas_todo.items import MISSING, PAST_DUE, UPCOMING, to_tasks
from canvas_todo.render import render_html, render_text

NOW = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)
BASE = "https://canvas.example.edu"


def item(title, days, ptype="assignment", **sub):
    due = (NOW + timedelta(days=days)).isoformat()
    return {
        "plannable_type": ptype,
        "plannable": {"title": title, "due_at": due},
        "context_name": "Course",
        "html_url": f"/x/{title}",
        "submissions": {"submitted": False, "graded": False, "missing": False, **sub},
    }


def test_filters_and_classifies():
    raw = [
        item("missing", -3, missing=True),
        item("pastdue", -1),
        item("future", 2),
        item("done", 1, submitted=True),
        item("graded", -5, graded=True),
        item("event", 1, ptype="calendar_event"),
        item("news", 1, ptype="announcement"),
    ]
    tasks = to_tasks(raw, BASE, NOW)
    assert [(t.title, t.status) for t in tasks] == [
        ("missing", MISSING),
        ("pastdue", PAST_DUE),
        ("future", UPCOMING),
    ]
    assert tasks[0].url == f"{BASE}/x/missing"


def test_overridden_complete_is_hidden():
    raw = [{**item("x", 1), "planner_override": {"marked_complete": True}}]
    assert to_tasks(raw, BASE, NOW) == []


def test_next_link():
    header = '<https://a/p?page=1>; rel="current", <https://a/p?page=2>; rel="next"'
    assert next_link(header) == "https://a/p?page=2"
    assert next_link("") is None


def test_render_escapes_html():
    tasks = to_tasks([item("<script>", 1)], BASE, NOW)
    html = render_html(tasks, NOW)
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "Upcoming (1)" in render_text(tasks)


def test_load_env(tmp_path):
    (tmp_path / ".env").write_text('# c\nCANVAS_TOKEN="abc"\nCANVAS_URL=https://x\n')
    assert load_env(tmp_path / ".env") == {"CANVAS_TOKEN": "abc", "CANVAS_URL": "https://x"}
    assert load_env(tmp_path / "nope") == {}
