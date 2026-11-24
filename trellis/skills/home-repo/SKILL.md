---
name: home-repo
description: Run the user's personal context repo ("home repo"): a git-tracked markdown folder of their tasks, decisions, lessons, journal and working style. Use it when the user starts or ends a day or session ("what's on today?", "end of session", "end the day"); starts, resumes, parks, hands off or closes a piece of work ("new task to…", "where was I on X", "give me a prompt for that task", "clean this task up", "close merged tasks"); wants their task list or notes tidied; wants something kept across projects ("save this to home-repo", "add this to global mem"); or wants a second brain set up. Natural phrasings are the normal case, even without the words "home repo". Not for: code or PR review, commits or issues in project repos, the agent's own todo list, /init, or facts about only the current directory (auto-memory).
---

# Home repo

The home repo is a git-tracked folder of markdown that gives every agent session the user's context: what they're working on, why, what was decided, what went wrong before, and how they like to work. It grows as a **side effect of working**, mostly when tasks start and close, and isn't meant to need upkeep of its own.

Evidence from real use shaped this design:
- Users don't remember capture phrases. Lessons, journal entries and system notes get written reliably only when another routine is already running, so every routine here writes them as part of its job.
- A **task** is the unit that carries context between sessions. The task file is the handoff path.
- Users phrase things in many ways. Map what they say to the nearest routine by intent.
- Most failures were skipped steps (a missed cleanup, a commit that emptied a file, a guessed timestamp), not bad judgment. So the routines are checklists, and the helper script does the mechanical checks.

## 1. Find the repo

Run `python3 <skill-dir>/scripts/home_repo.py locate` (use `python` or `py` where `python3` isn't available, e.g. Windows; "`home_repo.py <cmd>`" below means this invocation). It checks `$HOME_REPO`, then `~/.claude/home-repo.json`, then the current directory (if it has `tasks/active.md`), then `~/home-repo` and `~/projects/home-repo`. If nothing is found and the user wants one set up, follow `routines/init.md`. Read the repo's own `CLAUDE.md` before doing anything else; it's the map, and the owner's conventions there take precedence over the defaults in this skill. Some repos keep the map in `AGENTS.md` instead (the "Home Repo" pattern, or an owner who also uses other agents), sometimes with a `CLAUDE.md` that only imports it. `CLAUDE.md` in this skill means whichever file is the map.

## 2. Layout and when to read each part

```
<home-repo>/
├── CLAUDE.md            map + owner profile, ≤40 lines   → always read first (or AGENTS.md)
├── skills/              optional: the owner's own skills (Home Repo pattern) → where promoted skills go
├── tasks/
│   ├── active.md        current priorities                → start of day, new task
│   ├── backlog.md       real but inactive work             → new task, review
│   ├── <task>.md        why / decisions / gotchas / next  → working on or closing that task
│   └── archive/         closed task summaries              → only when the past is asked about
├── journal/YYYY-MM-DD.md  append-only raw log; expires     → start of day, closing
├── references/          style, environment, lessons, indexes → when the task touches that area
└── meta/
    ├── pattern-log.md   notes about how the system itself works → system changes, reviews
    └── pending.md       sessions that ended unjournaled (written by a hook)
```

Load as little as you can. The repo's `CLAUDE.md` says what each reference file is for, so open a reference only when the current work needs it.

## 3. Routines

Find the routine that matches the user's intent and **read its file before acting**. Each file is a checklist.

| Intent (example phrasings) | File |
|---|---|
| Set up or adopt a home repo | `routines/init.md` |
| "what's on today?", "where was I", resuming a session | `routines/start-day.md` |
| "new task to…", "I have a new task", "prepare me a space to review X", re-opening closed work | `routines/new-task.md` |
| "give me a prompt for that task", handing off to a fresh session | `routines/handoff.md` |
| "park this", "put X on hold", "blocked on…", "pick X back up" | `routines/park-task.md` |
| "close this task", "clean this task up", "close X, Y, Z", "close merged tasks" | `routines/close-task.md` |
| "end of session", "close the work for today", "end the day", "journal this" | `routines/end-session.md` |
| "tidy up my home repo", "review my tasks/notes", "weekly review", "reconcile my tasks" (any time) | `routines/review.md` |
| "save this to home-repo", "note this on the task", "add … to global mem", where a rule should live | `routines/capture.md` |
| "commit home-repo", or any commit the routines make *to the home repo* | `routines/commit.md` |
| "how is my home repo being used", a de-identified usage report to share | `routines/system-report.md` |

### Shared words: tell them apart

Several phrases overlap with other skills and built-in behavior. Use the context to decide, and if it's still unclear, ask in one short question rather than guessing.

| Word | Home repo when… | Something else when… |
|---|---|---|
| review | it's about tasks, notes or the home repo itself | it's about code, a diff or a PR → a code-review skill |
| close / clean up | it names a tracked task or its work as a whole | it's a GitHub issue/PR, a file, a process, or a todo item |
| done / clean it up | said about the work of an active task ("this is done, clean it up"): ask once whether to close the task too | it's clearly about code or files only |
| commit | the home repo, or the last step of a routine here | a project repo → normal git workflow |
| new task / task | a piece of the user's work that needs context and a workspace | the agent's in-session todo list, or a scheduled agent (`/schedule`) |
| save / remember | it should be available across projects or machines | it only concerns this directory → built-in auto-memory |
| init / set up | a home repo or second brain | a project `CLAUDE.md` → `/init` |
| status | the user's own tasks and day | a deploy, CI or service status |

### Other tools that overlap

If any of these are installed, divide the work rather than duplicating it:
- **Claude Code auto-memory**: facts about one directory stay there. The review's auto-memory sweep moves cross-project facts here.
- **claude-md-improver / `/revise-claude-md`** (official `claude-md-management` plugin): it maintains *project* `CLAUDE.md` files. When a lesson is promoted into a project's `CLAUDE.md`, that's a fine tool to do the edit; the lesson's history stays here.
- **`remember`** (official plugin, daily session logs): if it's installed, don't write a second journal. Treat its logs as the raw journal and only do the condensing (task Next, lessons, archive digest).
- **Compound engineering** (Every's plugin, `docs/solutions/` inside each project): project-level learnings belong there. Lessons here are personal and cross-project, and can be promoted *into* a project's `docs/solutions/`.

The task backend (a worktree manager, plain git branches, or none) changes a few steps. See `references/backends.md`; the repo's `CLAUDE.md` says which backend is in use.

## 4. Rules that apply everywhere

- **Never store what can be looked up.** That includes PR status, ticket state, branch lists and CI results. Store the *why*, decisions, gotchas and next steps, and look status up when it's asked for. Stored status goes stale and then misleads.
- **No secrets, credentials, hostnames/IPs or customer data.** Don't search the repo for access details either; it deliberately doesn't hold them. Ask the user or use the proper tool.
- **Timestamps come from the clock** (`home_repo.py now`). Never guess one.
- **Parallel sessions are normal.** Append to journal and pattern-log; edit only the task file you own; re-read a shared file just before you edit it.
- **Commit only on request or as a routine's final step**, and always through `routines/commit.md`. It guards against emptied files.
- **Side effects are part of every routine.** Each routine ends by appending to the journal, routing any lessons to `references/`, and adding a pattern-log line if the system itself caused friction. That's how the repo grows without the user remembering phrases.
- **The journal is raw material, not knowledge.** Closing a task condenses its journal into the archive, and old journal files expire during a review. What lasts lives in task files, archives and lessons.
- **Keep `CLAUDE.md` under ~40 lines.** It's loaded every time. Detail belongs in references; when you're tempted to add a line, add a pointer instead.
- **Auto-memory boundary.** Claude Code's per-directory auto-memory is for facts about that one directory only. Anything cross-project belongs here. If you see cross-project facts in auto-memory, suggest moving them during a review.

## 5. How knowledge builds up

Lessons carry their history (`repo; seen; last; from`), get **reinforced** rather than duplicated, are **recalled** automatically for the current repo at session start, and are **promoted** into rules, checks or skills once they've proven themselves (`seen ≥ 3` or `cost: high`, with the user's approval), and prose rules are **demoted** (deleted or moved out of always-loaded files) once they stop being needed. Read `references/knowledge.md` whenever you add, reinforce or review a lesson.

## 6. Templates

File formats are in `templates/`. Use them when creating files, so that archives and task files stay consistent and can be read by scripts later.
