# Skill Benchmark: home-repo, iteration 3

**Plugin**: 0.1.2 · **Claude Code**: 2.1.332 · **Date**: 2026-11-25 (local) · **Platform**: WSL Ubuntu (the eval CLI refuses a Bash grant on Windows)
**Evals**: all 7, including the first run of `agents-md-start-day` (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Mean score | 84% | 71% | +0.13 |

| Case | With | Without | Failed graders (with skill) |
|---|---|---|---|
| agents-md-start-day | 0.75 | 1.00 | 03-owner-convention |
| capture-refuses-secret | 1.00 | 1.00 | — |
| close-task-natural-phrase | 0.67 | 0.67 | 03-task-file-deleted, 05-journal-timed |
| commit-guard-emptied-file | 1.00 | 1.00 | — |
| end-of-day-journal | 0.60 | 0.20 | 01-journal-timed, 04-lesson-reinforced |
| start-day-catches-problems | 1.00 | 0.75 | — |
| tidy-up-review | 0.83 | 0.33 | 05-review-logged |

## Reading the failures

- **Graders pinned to 2026-11-23** (`journal-timed` ×2, `lesson-reinforced`, `review-logged`). The agent took today's date from `home_repo.py now` and wrote `journal/2026-11-25.md`, `last: 2026-11-25` and a `## 2026-11-25` section, which is correct. The graders expect the fixture's date, so they only passed in iteration 2 because it ran on that day. This is an eval-suite bug, not a skill one.
- **`task-file-deleted`**: in the sandbox the agent couldn't delete files from the shell. It failed in both arms the same way, so it's an environment limit.
- **`owner-convention`** (`agents-md-start-day`, first run): a real miss. The reply had the "Today's one thing:" line but then added a follow-up question after it, so the line wasn't last. The without-skill arm passed. The start-day routine's "ask which task" step should come before the owner's closing line.
- No failure touches what 0.1.2 changed (the task pointer, new-task ordering, recall rotation, close from inside a workspace). Those are covered by `tests/smoke.sh`.
- Not comparable with iteration 2: a different CLI (read-only tools by default, a sandboxed shell) and a different run date.
