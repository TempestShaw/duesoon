# canvas-todo

Never miss a Canvas assignment. One command lists everything you still owe — missing, past due, and upcoming — and can write a small HTML dashboard. Pure Python standard library, no browser automation.

## Setup

1. Canvas → **Account → Settings → + New Access Token**.
2. `cp .env.example .env` and paste the token (and your school's Canvas URL).

`.env` is gitignored. Treat the token like a password.

## Usage

```bash
python3 -m canvas_todo                       # next 30 days, text output
python3 -m canvas_todo --days 14
python3 -m canvas_todo --html dashboard.html --open
```

Sections:

- **Missing**: Canvas has marked the assignment missing.
- **Past due**: the due date passed and nothing was submitted *on Canvas*. Work handed in on Gradescope or elsewhere shows up here, so check before you panic.
- **Upcoming**: due within the window. Items due within 48 hours are highlighted in the dashboard.

Calendar events, announcements, and graded or submitted work are hidden. Anything you tick "mark as done" in the Canvas planner is hidden too.

## Gradescope (optional)

Gradescope has no official API, so canvas-todo logs in with your email and password and reads the course pages. Fill `GRADESCOPE_EMAIL` and `GRADESCOPE_PASSWORD` in `.env`. If you sign in through school SSO, first set a Gradescope password with "Forgot your password?" on the login page.

With Gradescope enabled:

- Canvas items already submitted on Gradescope (matched by title) disappear from the list.
- Open Gradescope work that isn't on Canvas is added, tagged `(Gradescope)`.

If the login fails, the tool prints a warning and falls back to Canvas only. The parser relies on Gradescope's page layout and may break when that changes.

## Tests

```bash
python3 -m pytest
```

## License

MIT
