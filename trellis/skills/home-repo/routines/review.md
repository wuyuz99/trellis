# Review (tidy up)

Goal: bring the repo back in line with reality and keep it small. There's no schedule; run it whenever the user asks ("review", "tidy up the home repo", "weekly review"), or suggest it when `status` shows drift (untracked backend tasks, pending sessions, `CLAUDE.md` over budget, an inbox with items in it). It's cheap, so running it often is fine.

Work through these steps and report a short summary at the end. If the user asks for just one part ("just reconcile tasks"), do only that part.

1. **Reconcile tasks with reality.** Compare `tasks/active.md` and `tasks/backlog.md` with the backend's live list (worktree tasks / branches / open PRs).
   - Backend tasks with no task file or backlog entry: list them and ask whether to track, close or ignore each one.
   - Active tasks whose PR has merged: offer to close them (`close-task.md`, bulk mode).
   - Look for skipped steps from earlier closings (e.g. archived tasks whose workspace still exists).
2. **Catch up pending sessions** in `meta/pending.md` (see `end-session.md`).
3. **Sort the inbox**, if one exists. Move each item to references or backlog, or delete it.
4. **Lessons** (see `references/knowledge.md`):
   - `lessons --lint`: add missing metadata.
   - Merge duplicates: combine their `seen` counts, keep the earliest `from`.
   - `lessons --promote`: propose each candidate to the user with a concrete form (a CLAUDE.md line, a check in a script or hook, a routine step, a skill). Apply only what they approve, and mark it `promoted: <where>`.
   - `lessons --demote` and the always-loaded files: propose deleting or moving prose rules that are no longer needed, and resolve conflicting rules (section 4 of `references/knowledge.md`). Removing is as much the point of a review as adding.
   - `lessons --stale`: ask whether each still holds; keep, reword or retire.
   - Check that commands, paths and settings named in lessons still exist.
5. **Retire what nobody reads.** Run `home_repo.py usage 60`. A reference or index that was written but never read in 60 days is a candidate to shrink, merge or delete; ask before deleting. (Task files and the active list are exempt, since they're read when the task is worked on.)
6. **Auto-memory sweep:** look at Claude Code auto-memory folders for cross-project facts, and offer to move them into references.
   **Rules sweep:** run `home_repo.py rules 14` (or since the last review). It lists sentences where the user stated a standing rule. Drop the ones already captured or only about one moment, and propose a place for the rest (`capture.md` placement table).
7. **Expire old journals.** Run `home_repo.py journal-expire` (default 6 weeks, or the retention set in the repo's `CLAUDE.md`). Files whose tasks are all closed have already been condensed into archives; delete them after confirming with the user (git history keeps them). Files that still mention an open task stay.
8. **Budget check:** keep `CLAUDE.md` at ≤40 lines. Move detail to references, and remove lines that duplicate the global file.
9. **Skill candidates:** scan recent journals for repeated multi-step work. List them as ideas, but don't build them unasked.
10. **Pattern log:** add a `## <date>` section summarizing what the review found and changed.
11. **Commit** through `commit.md`.

Improving the system itself over time is a separate job: `system-report.md` produces a de-identified usage report, and comparing reports shows what's working.
