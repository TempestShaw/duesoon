"""Settings: ~/.config/duesoon/config.env, then ./.env, then environment variables."""

import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "duesoon"
CONFIG_FILE = CONFIG_DIR / "config.env"
KEYS = ("CANVAS_URL", "CANVAS_TOKEN", "GRADESCOPE_EMAIL", "GRADESCOPE_PASSWORD")


def read_env_file(path: Path) -> dict[str, str]:
    """Read KEY=VALUE lines (missing file -> empty)."""
    if not path.is_file():
        return {}
    pairs = (
        line.split("=", 1)
        for line in path.read_text().splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    )
    return {k.strip(): v.strip().strip('"') for k, v in pairs}


def load() -> dict[str, str]:
    return {**read_env_file(CONFIG_FILE), **read_env_file(Path.cwd() / ".env"), **os.environ}


def save(values: dict[str, str]) -> Path:
    """Write settings readable only by the current user."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(CONFIG_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write("".join(f"{k}={v}\n" for k, v in values.items()))
    os.chmod(CONFIG_FILE, 0o600)
    return CONFIG_FILE
