# Skill Benchmark: home-repo, iteration 4

**Plugin**: 0.1.2 with the eval-suite fixes (cases moved to `trellis/evals/`, graders no longer pinned to 2026-11-23) · **Claude Code**: 2.1.332 · **Date**: 2026-11-26 · **Platform**: WSL Ubuntu
**Evals**: all 7 (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Mean score | 92% | 78% | +0.14 |

| Case | With | Without | Failed graders (with skill) |
|---|---|---|---|
| agents-md-start-day | 0.75 | 1.00 | 03-owner-convention |
| capture-refuses-secret | 1.00 | 1.00 | — |
| close-task-natural-phrase | 0.67 | 0.67 | 01-archive-written, 03-task-file-deleted |
| commit-guard-emptied-file | 1.00 | 1.00 | — |
| end-of-day-journal | 1.00 | 0.60 | — |
| start-day-catches-problems | 1.00 | 1.00 | — |
| tidy-up-review | 1.00 | 0.17 | — |

## Reading the failures

- The date fixes work: `end-of-day-journal` and `tidy-up-review` went from 0.60 and 0.83 (iteration 3) to 1.00 with the skill.
- **`task-file-deleted`** fails in both arms: the eval sandbox mounts the case folder read-only for the shell, so nothing can delete files or run git there. This is an environment limit; the Write and Edit tools still work.
- **`archive-written`** (close, with skill): the archive and the `active.md` edit were attempted through the shell, which is read-only here, and the trace shows no Write call for the archive. The close report still marked both steps ✓. The environment caused the failure, but a ✓ for a step that didn't happen is the kind of overclaim the close checklist is meant to prevent; worth a closer look.
- **`owner-convention`** (`agents-md-start-day`): same real miss as iteration 3. Start-day asks its follow-up question after the owner's "Today's one thing:" line.
