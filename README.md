# duesoon

**One list of everything you still owe on Canvas and Gradescope.** Missing work comes first. Lecture events, announcements and graded work are filtered out. Runs on your laptop, uses only the Python standard library, and does no browser automation.

🌐 **Website:** https://tempestshaw.github.io/duesoon/

## Install

```bash
uv tool install git+https://github.com/TempestShaw/duesoon     # or: pipx install ...
duesoon setup                                                   # paste your Canvas token
duesoon --open                                                  # dashboard in your browser
```

Create the Canvas token under **Account → Settings → + New Access Token**. Gradescope is optional. If you sign in through school SSO, first set a Gradescope password with "Forgot your password?".

## Usage

| Command | What it does |
|---------|--------------|
| `duesoon` | Text list for the next 30 days |
| `duesoon --days 7` | Change the window |
| `duesoon --open` | Write the HTML dashboard and open it |
| `duesoon --html out.html` | Write the dashboard to a specific path |
| `duesoon --ics ~/duesoon.ics` | Calendar file with a 24-hour reminder per deadline |
| `duesoon setup` | (Re)connect Canvas / Gradescope |

The list has three sections:

- **Missing**: Canvas has marked the assignment missing.
- **Past due, not submitted on Canvas**: the due date passed and Canvas has no submission. Work turned in on Gradescope is removed automatically when Gradescope is connected.
- **Upcoming**: due within the window. Items due within 48 hours are highlighted.

## Claude Code skill

```bash
mkdir -p ~/.claude/skills/duesoon && curl -fsSL https://raw.githubusercontent.com/TempestShaw/duesoon/main/skills/duesoon/SKILL.md -o ~/.claude/skills/duesoon/SKILL.md
```

Then ask Claude "what homework am I missing?". It installs duesoon if needed and summarizes the list. You type secrets into `duesoon setup` yourself, never into the chat.

## Privacy

Settings are stored in `~/.config/duesoon/config.env` with mode 600. A `.env` file in the current directory or environment variables also work. Your data goes only to your Canvas server and to gradescope.com. Gradescope has no official API, so duesoon logs in and reads the course pages. That part may break if Gradescope changes its layout.

## Development

```bash
python3 -m pytest
```

MIT licensed. Not affiliated with Instructure or Gradescope.
