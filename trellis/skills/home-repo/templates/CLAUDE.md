# <repo-name> — <owner>'s personal context

**Who:** <role>. Main repos: `<repo>` (<areas>), `<repo>` (<areas>).
**Style:** <trait>, <trait>, <trait>. Details → `references/style.md`
**Task backend:** <worktree tool "<name>" | git branches | none>. Push allowed: <yes/no>. Journal retention: <6> weeks.

## Map (read only what you need)
- `tasks/active.md`: current priorities. `tasks/<task>.md`: why/decisions/gotchas/next. Read before working on that task.
- `tasks/backlog.md`: inactive work. `tasks/archive/`: closed tasks. Read only when asked about the past.
- `journal/YYYY-MM-DD.md`: append-only session log. Read the latest one at start of day.
- `references/style.md`: how I like to work. Read when making judgment calls about form.
- `references/lessons.md`: cross-task gotchas by area. Read before work in that area.
- `references/environment.md`: tools and setup. Read when tooling misbehaves.
- `meta/pattern-log.md`: how this system is working. Append when it gets in the way.

## Ownership
- <backend> owns branches/worktrees. Tickets live in <tracker>. This repo owns what/why/next/history.
- Never store status that can be looked up; look it up when asked.

## Routines
Handled by the home-repo skill: start day, new task, park/resume, handoff, close task(s), end session, review, capture, commit, system report.
<Owner-specific overrides, one line each, e.g. "closing always tags unlanded work instead of asking".>

## Rules
- No secrets, credentials, hostnames/IPs or customer data.
- Parallel sessions: edit only your task file; append-only to journal and pattern-log.
