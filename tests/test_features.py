import stat
from datetime import datetime, timezone

from duesoon import config
from duesoon.ics import render_ics
from duesoon.items import MISSING, UPCOMING, Task

NOW = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)


def test_config_precedence(tmp_path, monkeypatch):
    cfg = tmp_path / "config.env"
    cfg.write_text("CANVAS_TOKEN=from_config\nCANVAS_URL=https://a\n")
    (tmp_path / ".env").write_text("CANVAS_URL=https://b\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(config, "CONFIG_FILE", cfg)
    monkeypatch.delenv("CANVAS_TOKEN", raising=False)
    monkeypatch.setenv("CANVAS_URL", "https://c")
    env = config.load()
    assert env["CANVAS_TOKEN"] == "from_config"
    assert env["CANVAS_URL"] == "https://c"  # environment wins


def test_save_is_private_and_roundtrips(tmp_path, monkeypatch):
    cfg = tmp_path / "sub" / "config.env"
    monkeypatch.setattr(config, "CONFIG_FILE", cfg)
    config.save({"CANVAS_TOKEN": "t", "GRADESCOPE_EMAIL": ""})
    assert stat.S_IMODE(cfg.stat().st_mode) == 0o600
    assert config.read_env_file(cfg) == {"CANVAS_TOKEN": "t", "GRADESCOPE_EMAIL": ""}


def test_ics_has_one_event_per_dated_task():
    tasks = [
        Task("HW; 1, part", "Course", NOW, "https://x/1", UPCOMING),
        Task("Late", "Course", NOW, "https://x/2", MISSING),
        Task("Undated", "Course", None, "https://x/3", UPCOMING),
    ]
    ics = render_ics(tasks, NOW)
    assert ics.startswith("BEGIN:VCALENDAR\r\n") and ics.endswith("END:VCALENDAR\r\n")
    assert ics.count("BEGIN:VEVENT") == 2
    assert "SUMMARY:[Course] HW\\; 1\\, part" in ics
    assert "SUMMARY:⚠️ MISSING [Course] Late" in ics
    assert "DTSTART:20261030T120000Z" in ics
