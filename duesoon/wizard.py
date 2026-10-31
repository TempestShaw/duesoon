"""Interactive first-run setup: `duesoon setup`."""

from datetime import datetime, timezone
from getpass import getpass

from . import config
from .api import CanvasError, fetch_planner_items
from .gradescope import GradescopeError, fetch_gradescope

DEFAULT_URL = "https://canvas.cmu.edu"


def _ask(prompt: str, default: str = "") -> str:
    shown = f" [{default}]" if default else ""
    return input(f"{prompt}{shown}: ").strip() or default


def _check_canvas(url: str, token: str) -> bool:
    try:
        fetch_planner_items(url, token, datetime.now(timezone.utc), 1, 1)
        return True
    except CanvasError as err:
        print(f"  ✗ {err}")
        return False


def _check_gradescope(email: str, password: str) -> bool:
    try:
        fetch_gradescope(email, password)
        return True
    except GradescopeError as err:
        print(f"  ✗ {err}")
        return False


def run() -> int:
    current = config.load()
    print("duesoon setup. Settings are saved to", config.CONFIG_FILE, "(readable only by you).\n")

    url = _ask("Canvas URL", current.get("CANVAS_URL", DEFAULT_URL)).rstrip("/")
    print(f"Create a token at {url}/profile/settings -> '+ New Access Token'.")
    token = getpass("Canvas token (hidden): ").strip() or current.get("CANVAS_TOKEN", "")
    if not token or not _check_canvas(url, token):
        print("Canvas check failed; nothing saved.")
        return 1
    print("  ✓ Canvas connected")

    values = {"CANVAS_URL": url, "CANVAS_TOKEN": token, "GRADESCOPE_EMAIL": "", "GRADESCOPE_PASSWORD": ""}
    if _ask("Also connect Gradescope? (y/N)", "n").lower().startswith("y"):
        print("SSO users: set a password first via 'Forgot your password?' on gradescope.com/login.")
        email = _ask("Gradescope email", current.get("GRADESCOPE_EMAIL", ""))
        password = getpass("Gradescope password (hidden): ")
        if _check_gradescope(email, password):
            print("  ✓ Gradescope connected")
            values = {**values, "GRADESCOPE_EMAIL": email, "GRADESCOPE_PASSWORD": password}
        else:
            print("  Skipping Gradescope; run `duesoon setup` again to retry.")

    path = config.save(values)
    print(f"\nSaved to {path}. Try: duesoon --open")
    return 0
