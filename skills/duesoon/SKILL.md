---
name: duesoon
description: Show the student's unfinished Canvas and Gradescope work (missing, past due, upcoming) with the duesoon CLI, installing and setting it up if needed. Use when the user asks what homework or assignments are due, what they are missing, wants a homework dashboard, or wants deadlines in their calendar.
---

# duesoon

`duesoon` is a small Python CLI (https://github.com/TempestShaw/duesoon) that reads the Canvas planner API, and optionally Gradescope, and lists everything the student still owes.

## 1. Make sure it is installed

Run `duesoon --help`. If the command is not found, install it, preferring the first tool that exists:

```bash
uv tool install git+https://github.com/TempestShaw/duesoon
pipx install git+https://github.com/TempestShaw/duesoon
python3 -m pip install --user git+https://github.com/TempestShaw/duesoon
```

Python 3.10+ is required.

## 2. Make sure it is set up

If `duesoon` prints "Not set up yet", the user has to run the wizard **in their own terminal**, because it asks for a Canvas token and optionally a Gradescope password:

```bash
duesoon setup
```

Do not ask for the token or password in chat, and do not type them for the user. Tell the user:

- Canvas token: Canvas → Account → Settings → "+ New Access Token".
- Gradescope (optional): school SSO accounts first need a password, set via "Forgot your password?" on gradescope.com/login.

Settings are stored in `~/.config/duesoon/config.env` with permissions 600. Never print that file.

## 3. Use it

| Goal | Command |
|------|---------|
| List the next 30 days | `duesoon` |
| Different window | `duesoon --days 7` |
| Open the dashboard in a browser | `duesoon --open` |
| Calendar file with 24-hour reminders | `duesoon --ics ~/duesoon.ics`, then open the file to import it |

When reporting results:

- Lead with **Missing** items. Then list anything due within 48 hours, then a short count of the rest.
- "Past due, not submitted on Canvas" can be a false alarm when the work was turned in somewhere else. Say so, and suggest connecting Gradescope if it isn't connected.
- Use the student's language and keep the summary short.
