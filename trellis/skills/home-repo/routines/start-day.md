# Start day / resume

Goal: in under a minute, the user knows what's on, and the agent has loaded the context for the one task they pick.

1. Run `home_repo.py status`. It reports active tasks, pending unjournaled sessions, uncommitted changes, `CLAUDE.md` size, and files that are suspiciously empty.
2. **Handle problems first, briefly:**
   - Pending sessions in `meta/pending.md`: offer to draft journal entries for them (see `end-session.md`, "Catching up").
   - Uncommitted changes from an earlier day: offer to commit them through `commit.md`.
   - Empty or truncated files: say so before anything else. In past use this caught a commit that had emptied a planning file.
3. Read `tasks/active.md` and the **latest** journal file only. Don't read older journals unless asked.
4. If the backend has live state (open PRs, the worktree tool's task list), look it up now rather than trusting anything stored.
5. Reply with: active tasks with the next step for each (from each task file's `## Next`), anything blocked, and one suggested focus. Keep it short. If the repo's map sets a format for this reply (such as a closing "Today's one thing:" line), follow it exactly: a line the owner wants at the end stays the last line, so put any question ("which one do you want to pick up?") before it, or leave the question out.
6. When the user picks a task, read **that task file** before starting work. This is the main point: context should load at the start of work, not at the end.
7. Append a journal line: `## start-of-day HH:MM` and a bullet listing the chosen focus.
