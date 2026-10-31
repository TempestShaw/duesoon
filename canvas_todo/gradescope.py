"""Read assignments from Gradescope (no official API: logs in and parses HTML).

Requires a Gradescope password. SSO-only accounts can set one with
"Forgot your password?" on https://www.gradescope.com/login.
"""

import http.cookiejar
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from html import unescape

BASE_URL = "https://www.gradescope.com"
TIMEOUT_SECONDS = 30
SUBMITTED_WORDS = ("submitted", "graded", "late")

_TAG = re.compile(r"<[^>]+>")
_TERM_SPLIT = re.compile(r'class="courseList--term[^"]*"')
_COURSE = re.compile(
    r'<a[^>]*class="courseBox[^"]*"[^>]*href="/courses/(\d+)"[^>]*>.*?courseBox--shortname[^>]*>(.*?)</h3>',
    re.S,
)
_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
_HEADER = re.compile(r"<th[^>]*>(.*?)</th>", re.S)
_LINK = re.compile(r'href="(/courses/[^"]+)"')
_STATUS = re.compile(r'class="submissionStatus[^"]*"[^>]*>(.*?)</td>', re.S)
_DUE = re.compile(r'submissionTimeChart--dueDate"[^>]*datetime="([^"]+)"')
_TOKEN = re.compile(r'name="authenticity_token"[^>]*value="([^"]+)"')


class GradescopeError(RuntimeError):
    pass


@dataclass(frozen=True)
class GsAssignment:
    title: str
    course: str
    due: datetime | None
    submitted: bool
    url: str


def _text(html: str) -> str:
    return " ".join(unescape(_TAG.sub(" ", html)).split())


def parse_courses(account_html: str) -> list[tuple[str, str]]:
    """(course_id, short name) for the most recent term on the account page."""
    terms = _TERM_SPLIT.split(account_html)
    current = terms[1] if len(terms) > 1 else account_html
    return [(cid, _text(name)) for cid, name in _COURSE.findall(current)]


def _parse_due(raw: str) -> datetime | None:
    try:
        return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S %z").astimezone()
    except ValueError:
        return None


def parse_assignments(course_html: str, course: str) -> list[GsAssignment]:
    rows = []
    for row in _ROW.findall(course_html):
        header = _HEADER.search(row)
        status = _STATUS.search(row)
        if not header or not status:  # table header row has no status cell
            continue
        status_text = _text(status.group(1)).lower()
        link = _LINK.search(header.group(1))
        due = _DUE.search(row)
        rows = [
            *rows,
            GsAssignment(
                title=_text(header.group(1)),
                course=course,
                due=_parse_due(due.group(1)) if due else None,
                # A score ("8.0 / 10.0") also means it was handed in.
                submitted="/" in status_text or any(w in status_text for w in SUBMITTED_WORDS),
                url=BASE_URL + link.group(1) if link else BASE_URL,
            ),
        ]
    return rows


class GradescopeClient:
    def __init__(self) -> None:
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        )

    def _get(self, path: str, data: dict | None = None) -> str:
        body = urllib.parse.urlencode(data).encode() if data else None
        try:
            with self._opener.open(BASE_URL + path, body, timeout=TIMEOUT_SECONDS) as resp:
                return resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as err:
            raise GradescopeError(f"Gradescope returned {err.code} for {path}") from err
        except urllib.error.URLError as err:
            raise GradescopeError(f"Network error: {err.reason}") from err

    def login(self, email: str, password: str) -> None:
        token = _TOKEN.search(self._get("/login"))
        if not token:
            raise GradescopeError("Could not find the Gradescope login form")
        page = self._get(
            "/login",
            {"utf8": "✓", "authenticity_token": token.group(1), "session[email]": email,
             "session[password]": password, "session[remember_me]": "0", "commit": "Log In"},
        )
        if "courseBox" not in page and "Log Out" not in page:
            raise GradescopeError("Gradescope login failed; check GRADESCOPE_EMAIL / GRADESCOPE_PASSWORD")

    def assignments(self) -> list[GsAssignment]:
        courses = parse_courses(self._get("/account"))
        return [a for cid, name in courses for a in parse_assignments(self._get(f"/courses/{cid}"), name)]


def fetch_gradescope(email: str, password: str) -> list[GsAssignment]:
    client = GradescopeClient()
    client.login(email, password)
    return client.assignments()
