# Capture and rule placement

In real use, explicit capture was rare: most knowledge entered through closing and end-of-session. When the user does ask to save something, save it **directly in the right place**. An inbox nobody sorts goes stale.

## Where things go

| What | Where |
|---|---|
| A decision or gotcha about the current task | `tasks/<task>.md` under `## Decisions` (`- <date>: …`) or `## Gotchas` |
| A lesson useful beyond this task | `references/lessons.md`, one line under `## <area>` with `(repo; seen; last; from)` metadata. Search first; reinforce a match instead of duplicating it (see `references/knowledge.md`). |
| A preference about how to work | `references/style.md` |
| A tool or environment fact | `references/environment.md` (or whichever environment reference the repo has) |
| A pointer to something outside the repo | the relevant index reference: path + what it is + why it matters |
| Work to do later | `tasks/backlog.md` |
| Truly unsure | `inbox.md` with a date. A review sorts it. |
| Status that can be looked up | Nowhere. Say so and explain why. |
| Secrets, hosts, customer data | Nowhere. Refuse and suggest the proper secret store. |

Confirm the location with a one-line reply ("Saved to references/lessons.md under ## Build").

## Rule placement ("add this to global mem", "always do X")

| Scope of the rule | Where it goes |
|---|---|
| Must hold in **every** session, safety-critical | the global `~/.claude/CLAUDE.md` "Home repo" section (keep it to 1–3 hard rules) |
| About how the home repo itself works | the repo's `CLAUDE.md` (watch the 40-line budget) |
| Context that's useful but not always needed | a `references/` file, pointed to from `CLAUDE.md` |
| Only about one project directory | that project's `CLAUDE.md` or its auto-memory |

After changing the global file, tell the user: **sessions that are already running won't pick it up until they restart.**
