from datetime import datetime, timezone

from canvas_todo.gradescope import GsAssignment, parse_assignments, parse_courses
from canvas_todo.items import PAST_DUE, UPCOMING, Task
from canvas_todo.merge import merge

NOW = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)

ACCOUNT_HTML = """
<div class="courseList">
  <div class="courseList--term">Fall 2026</div>
  <div class="courseList--coursesForTerm">
    <a class="courseBox" href="/courses/111"><h3 class="courseBox--shortname">15-645</h3>
      <div class="courseBox--name">Database Systems</div></a>
    <a class="courseBox" href="/courses/222"><h3 class="courseBox--shortname">95-702</h3></a>
  </div>
  <div class="courseList--term">Spring 2026</div>
  <div class="courseList--coursesForTerm">
    <a class="courseBox" href="/courses/999"><h3 class="courseBox--shortname">OLD</h3></a>
  </div>
</div>
"""

COURSE_HTML = """
<table id="assignments-student-table">
<thead><tr><th scope="col">Name</th><th>Status</th></tr></thead><tbody>
<tr role="row"><th class="table--primaryLink" scope="row">
  <a href="/courses/111/assignments/1/submissions/5">Project #2 - Database Index</a></th>
  <td class="submissionStatus"><div class="submissionStatus--score">100.0 / 100.0</div></td>
  <td><time class="submissionTimeChart--dueDate" datetime="2026-10-25 23:59:00 -0400">Oct 25</time></td></tr>
<tr role="row"><th class="table--primaryLink" scope="row">
  <button class="js-submitAssignment" data-assignment-id="2">Homework #4 - Query Execution</button></th>
  <td class="submissionStatus"><div class="submissionStatus--text">No Submission</div></td>
  <td><time class="submissionTimeChart--dueDate" datetime="2026-11-01 23:59:00 -0400">Nov 01</time></td></tr>
<tr role="row"><th scope="row">DRC 1</th>
  <td class="submissionStatus"><div class="submissionStatus--text">Submitted</div></td>
  <td></td></tr>
</tbody></table>
"""


def test_parse_courses_takes_current_term_only():
    assert parse_courses(ACCOUNT_HTML) == [("111", "15-645"), ("222", "95-702")]


def test_parse_assignments():
    got = parse_assignments(COURSE_HTML, "15-645")
    assert [(a.title, a.submitted) for a in got] == [
        ("Project #2 - Database Index", True),
        ("Homework #4 - Query Execution", False),
        ("DRC 1", True),
    ]
    assert got[1].due == datetime(2026, 11, 2, 3, 59, tzinfo=timezone.utc)
    assert got[2].due is None


def canvas(title, status):
    return Task(title=title, course="Database Systems", due=NOW, url="u", status=status)


def test_merge_hides_canvas_items_submitted_on_gradescope():
    tasks = [canvas("Project #2 - Database Index", PAST_DUE), canvas("Lab 9", UPCOMING)]
    gs = [GsAssignment("project #2 database index", "15-645", None, True, "g")]
    assert [t.title for t in merge(tasks, gs, NOW, NOW)] == ["Lab 9"]


def test_merge_adds_gradescope_only_unsubmitted_work():
    due = datetime(2026, 11, 3, tzinfo=timezone.utc)
    gs = [
        GsAssignment("Written HW 5", "15-645", due, False, "g5"),
        GsAssignment("Lab 9", "15-645", due, False, "dup"),  # already on Canvas
        GsAssignment("Old", "15-645", datetime(2026, 1, 1, tzinfo=timezone.utc), False, "old"),
    ]
    out = merge([canvas("Lab 9", UPCOMING)], gs, NOW, datetime(2026, 12, 1, tzinfo=timezone.utc))
    assert sorted(t.title for t in out) == ["Lab 9", "Written HW 5"]
    assert next(t for t in out if t.title == "Written HW 5").course == "15-645 (Gradescope)"
