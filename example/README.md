# Example home repo

A small, fictional home repo (a backend developer, "Sam", with two code repos) showing what Trellis keeps once it has been in use for a while. Nothing here is real data. It's adapted from the eval fixtures in `trellis/evals/`, which contain deliberate problems for the routines to catch; this copy is the healthy version.

| File | What it shows |
|---|---|
| `CLAUDE.md` | The map: under 40 lines, loaded in every session that works on the repo. It points to everything else instead of containing it. |
| `tasks/active.md`, `tasks/backlog.md` | One line per task. No PR or CI status: that gets looked up, because copies go stale. |
| `tasks/export-timeout.md` | A task file: why, decisions (dated, with the reason), gotchas, next step. The SessionStart hook points a session at it when you work in the `export-timeout` worktree. |
| `tasks/archive/billing-report.md` | What closing a task leaves behind: outcome, decisions, and a journal digest, written before the raw journal expires. |
| `journal/` | Append-only, one file per day, `## <task> HH:MM` headings. Written by the routines, not by hand. |
| `references/lessons.md` | One line per lesson with its history: which repo, how often it came up (`seen`), when, and where from. A lesson seen often enough gets proposed as a rule, check or skill (`promoted:`), and expensive ones carry `cost:`. |
| `references/style.md`, `references/environment.md` | Facts about you and your tools, used across projects. |
| `meta/pattern-log.md` | Notes on how the system itself is working, which reviews and usage reports draw on. |

To look around with Trellis itself: `HOME_REPO=/path/to/example claude`, then ask "what's on today?". Routines will want to commit, so try it on a copy.
