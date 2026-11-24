# Trellis (v0.1.0)

*Your agent's lessons grow into rules, and get pruned when they stop paying off.*

> **Status: early.** Designed from one person's real usage (two de-identified usage reports), with a smoke test that passes on Linux and Windows and an eval suite last benchmarked on a pre-release build. macOS is untested, and the session hooks haven't yet been used in day-to-day work. Expect routines to change as more usage data comes in.

Trellis is a Claude Code plugin. It provides the **home-repo** skill, which manages your home repo (a **personal context repo**): a git-tracked folder of markdown that holds your tasks, decisions, lessons, journal and working style, so every agent session starts with the right context and nothing has to be explained twice.

It implements the [Home Repo pattern](https://aihero.dev/the-home-repo-pattern): one repo for your personal context, separate from your code repos. Most tools in this space help you *create* that folder or *capture* into it. Trellis focuses on keeping it useful: tasks carry context between sessions, lessons are promoted when they recur and pruned when they don't, and the routines do the upkeep so you don't have to.

It's built around how the pattern was actually used, not how it was first imagined:
- **The task is the unit.** Starting and closing work is when context gets written and passed on.
- **Side effects, not discipline.** Journal entries, lessons and system notes get written by the routines you already run, so you don't need to remember capture phrases.
- **Progressive disclosure.** Only the skill's description is always loaded; each routine's checklist loads when needed, and the repo's own `CLAUDE.md` is a ≤40-line map.
- **Checklists and scripts where steps get skipped.** Closing and committing are where things broke in practice.
- **Knowledge that proves itself, and gets removed when it doesn't.** Lessons record where they came from, how often they've mattered and what they cost. They get reinforced instead of duplicated, recalled automatically for the repo you're in, promoted into rules, checks or skills once they've recurred, and demoted out of always-loaded files once they stop being needed. Health is measured by what gets *read*, not written.

## What's inside

```
trellis/
├── .claude-plugin/plugin.json
├── hooks/hooks.json, run.sh         SessionStart: points at the matching task file, recalls lessons, pending journals
│                                    SessionEnd: records sessions that ended without a journal entry
├── tests/smoke.sh                   script + hooks smoke test (bash tests/smoke.sh)
└── skills/home-repo/
    ├── SKILL.md                     intent → routine map, layout, global rules
    ├── routines/                    one checklist per routine (loaded on demand)
    │   init · start-day · new-task · park-task · handoff · close-task
    │   end-session · review · capture · commit · system-report
    ├── templates/                   CLAUDE.md, task, archive, lists, pattern-log
    ├── references/backends.md       worktree tool / git branches / none
    ├── references/knowledge.md      lesson format, reinforce, recall, promotion path
    ├── scripts/home_repo.py         locate · now · status · check-commit · lessons · usage · journal-expire · rules · hooks
    └── evals/                       7 test cases with sample repos
```

Requires `git`, `bash` (Git Bash on Windows) and Python 3.9+ on PATH as `python3`, `python` or `py`. `gh` is optional, for PR lookups.

## Install

```
/plugin marketplace add wuyuz99/trellis
/plugin install trellis@trellis
```

Or try it for one session without installing: clone the repo and run `claude --plugin-dir /path/to/trellis`.

Then, in any session: "set up my home repo" (or "adopt my home repo" if you have one), and afterwards "what's on today?", "new task to …", "close this task".

If you already have a home repo, the skill **adopts** it. That includes Home Repo–pattern repos that keep their map in `AGENTS.md` and their skills in `skills/`, and Obsidian vaults. Your repo's `CLAUDE.md` conventions take precedence over the skill's defaults, so set `HOME_REPO=/path/to/it` or write `~/.claude/home-repo.json` as `{"path": "..."}`.

To use just the skill without the hooks, copy `skills/home-repo/` to `~/.claude/skills/home-repo/`.

## Privacy: what it reads and writes

Everything stays on your machine. Neither the script nor the hooks make network calls.
- **Reads:** your home repo, `~/.claude/home-repo.json`, and, for the `usage` and `rules` commands and the system report, Claude Code's local session transcripts (`~/.claude/projects/**/*.jsonl`), to count file reads and find rules you stated.
- **Writes:** only inside your home repo. The SessionEnd hook appends a line (time, working directory, transcript path) to `meta/pending.md`. The SessionStart hook writes nothing; it prints a short note into the new session.
- **Git:** routines commit to the home repo only through the commit routine, which checks for emptied files and secret patterns. They push only if your repo's `CLAUDE.md` allows it. Create its remote as **private**.
- **Never stored by design:** secrets, credentials, hostnames/IPs, customer data, and status that can be looked up (PR, ticket, CI).
- The system report shares only an allowlist (counts, file-structure names, trigger words), and you review it before it leaves the repo.

## Where each feature came from

**Backed by usage data** (first 2-day report, 2026-11-23):

| Feature | Evidence |
|---|---|
| Task lifecycle at the center | Tasks, decisions and links were the most-saved types; closing was the most-used, highest-value routine |
| Intent-based triggers | 9 undocumented phrasings ("clean this task up", "end the day"…), all correctly mapped |
| Close-task checklist + final report | A skipped cleanup step, caught only by a later review |
| `check-commit` guard | A bulk commit emptied a planning file |
| `now` for timestamps | A guessed journal time |
| Journal/lessons written as side effects | 25 journal sections, only 2 from the journal phrase; 0 explicit captures |
| SessionEnd → `pending.md` | Journaling depends on remembering a phrase, and sessions get cleared |
| SessionStart task pointer | Context was mostly loaded at the *end* of sessions; only 3/12 loaded it unprompted |
| "Never store look-up-able status" + no access details | A wrong-place status snapshot; 2 wasted searches for access info |
| Re-open instead of re-create | A closed task was re-created the same day, producing churn and a duplicate archive |
| Handoff prompts | "give me a prompt for that task" |
| Rule placement + restart warning | Rules moved to the global file didn't reach running sessions |
| Backend-specific close steps | The worktree tool refused to remove tasks that still had worktrees; local and upstream branch names differed |
| Auto-memory boundary + sweep | Auto-memory fragmented across ~90 directories |
| Archive before cleanup | Transcripts expire after ~30 days |
| `rules` command + rules step at close, end of session and review | Second report: two standing rules ("no commit without approval", "no automatic PR comments") the user wanted kept but had to set by hand |
| Close verifies workspaces are gone from disk | Second report: teardown didn't finish in 3 of 5 closes, and 2 of those still reported success |
| `status` flags stray files in the repo root | Second report: a close sent its teardown log into the repo root |
| "done / clean it up" in the shared-words table | Second report: "this is done, clean it up" got a project cleanup only; the task close came 9 min later |
| Adopting a hand-run repo (guide file, lessons without metadata) | Second report: the source repo runs on its own routine guide and has 33 lessons without metadata |

**Kept on judgment** (not exercised in a 2-day cycle; confirm or cut using later reports):

| Feature | Why keep it |
|---|---|
| Park / resume | Real work gets blocked; without it, the active list goes stale |
| Review (any time, no fixed schedule) | Useful after just 1 day; cadence is up to the user |
| Inbox as a fallback only | Unused so far; kept for "not sure where this goes" |
| `system-report` routine | Turns the manual de-identified report into a repeatable routine for improving the system |
| Backends for plain git / none | Needed for anyone without a worktree tool |
| Skill-candidate spotting in reviews | Cheap, and it's how this plugin's own routines were found |
| Pending-session catch-up | Depends on the hook; unproven |
| Lesson metadata (`repo; seen; last; from`) + reinforce instead of duplicate | Built-in memory can't tell a recurring lesson from a one-off; recurrence is the signal |
| Promotion path (lesson → rule / check / skill, user-approved) | Already happened by hand: an emptied-file commit became `check-commit`, a skipped step became the close checklist |
| Lesson recall in the SessionStart hook | Makes relevant lessons show up without the agent having to know to search |

## Related tools

| Tool | Overlap | How they fit together |
|---|---|---|
| Claude Code auto-memory (built in) | Per-directory notes | Directory facts stay there; review sweeps cross-project facts into lessons |
| `claude-md-management` (official plugin) | Captures session learnings into project `CLAUDE.md` | Use it as the editor when a lesson is promoted into a project `CLAUDE.md` |
| `remember` (official plugin) | Daily session logs | If installed, treat its logs as the raw journal; home-repo only condenses |
| [Compound engineering](https://github.com/EveryInc/compound-engineering-plugin) (Every) | Plan → Work → Review → Compound; `docs/solutions/` per project | Project-level learnings live there; home-repo is the personal, cross-project layer and can promote into it |
| [Home Repo pattern](https://aihero.dev/the-home-repo-pattern) (Matt Pocock) | One repo with your skills, `AGENTS.md` and shared docs; you run the agent there | Trellis implements it and adopts such repos as they are (`AGENTS.md` as the map, `skills/` as the target for promoted skills). It adds the task lifecycle and the lesson loop, and works from any project directory via hooks |
| Second-brain vault skills (e.g. skills.sh `second-brain/vault-setup`) | Vault scaffolding | Setup-focused; no task lifecycle or promote/demote loop |
| Obsidian + Claude Code vaults (e.g. [COG](https://github.com/huytieu/COG-second-brain), [claude-obsidian](https://github.com/agricidaniel/claude-obsidian), [Life.MD](https://github.com/hamza-menay/Life.MD)) | Markdown vault as an agent's memory | The home repo is plain markdown, so it can live inside a vault. Use the vault for notes and Trellis for tasks and lessons |
| Agent-memory stores (e.g. [agentkb](https://github.com/isaac-flath/agentkb), MCP memory servers) | Automatic capture and recall of session knowledge | They automate capture; Trellis is the curation layer (reinforce, promote, demote). Capture wasn't where things failed in practice, upkeep was |

## Changelog
- **0.1.0**: first public release. Task lifecycle (new, park, handoff, close with archive and journal digest), start-day / end-session / review / capture / commit routines, lessons with history that are reinforced, recalled at session start, promoted and demoted. Helper script (`locate`, `now`, `status`, `check-commit`, `lessons`, `usage`, `journal-expire`, `rules`), SessionStart/SessionEnd hooks, adoption of existing repos (including `AGENTS.md` / Home Repo pattern repos and Obsidian vaults), a de-identified `system-report` routine, 7 eval cases and a smoke test. Shaped by four private pre-release iterations and two usage reports; their findings are in the tables above.

## Known gaps / next questions
- Do recalled lessons actually get reinforced? The next report should count `seen` changes.
- `usage` counts from shell commands are heuristic and can misattribute files named in the same command.
- Demotion decisions still rely on the user's judgment; an automated with/without-rule eval would make them evidence-based.
- `rules` finds standing rules with a phrase heuristic ("never…", "without my approval", "from now on"…). It will miss rules phrased otherwise and list some one-off instructions; the routines confirm each one with the user.
- Second report (baseline: the original prompt-based setup the skill was designed from, not Trellis): task context loaded early in all 3 coding sessions but only at close in all 4 review/summary sessions; 33 lessons, 0 reinforced, read before work in 1 of 7 sessions; journal written only by closes. The first report after that machine switches to the skill should show whether the SessionStart pointer and lesson recall change those numbers.
- Ideas not built yet: a `## Tried` (what didn't work) section, decisions linked to the ones they replace.
- Does the SessionStart pointer actually move context loading to the start of work? The next report should measure this.
- `pending.md` uses a heuristic (≥3 user turns, no journal path written). It may be noisy.
- Matching a task to the current directory uses the task name and `Repos:` line; repo names that also appear as ordinary folder names may give false matches.
- Two archive formats existed in the source repo; the template sets one. Migrating old archives is not automated.
- Scopes (work / personal / family) are a recurring idea in personal-context writing, but every usage report so far is work tasks only. Not built; revisit if non-work use shows up.
- `[[wikilinks]]` between tasks, lessons and archives would make the repo browsable in Obsidian. Not built; only worth it if users open the repo as a vault.
- Description triggering hasn't been tuned yet (skill-creator's description optimizer is the next step).
