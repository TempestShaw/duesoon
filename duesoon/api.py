"""Minimal Canvas REST client (stdlib only)."""

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

PER_PAGE = 100
TIMEOUT_SECONDS = 30


class CanvasError(RuntimeError):
    pass


def next_link(link_header: str) -> str | None:
    """Return the rel="next" URL from a Canvas Link header, if any."""
    for part in link_header.split(","):
        if 'rel="next"' in part:
            return part[part.find("<") + 1 : part.find(">")]
    return None


def fetch_all(base_url: str, path: str, params: dict, token: str) -> list[dict]:
    """GET every page of a paginated Canvas endpoint."""
    url: str | None = f"{base_url}{path}?{urllib.parse.urlencode(params)}"
    items: list[dict] = []
    while url:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
                items = [*items, *json.load(resp)]
                url = next_link(resp.headers.get("Link", ""))
        except urllib.error.HTTPError as err:
            raise CanvasError(f"Canvas API returned {err.code}; check CANVAS_TOKEN / CANVAS_URL") from err
        except urllib.error.URLError as err:
            raise CanvasError(f"Network error: {err.reason}") from err
    return items


def fetch_planner_items(
    base_url: str, token: str, now: datetime, days_back: int, days_ahead: int
) -> list[dict]:
    params = {
        "start_date": (now - timedelta(days=days_back)).isoformat(),
        "end_date": (now + timedelta(days=days_ahead)).isoformat(),
        "per_page": PER_PAGE,
    }
    return fetch_all(base_url, "/api/v1/planner/items", params, token)
