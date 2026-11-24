# Close task

The most-used and most valuable routine. It's also where a skipped step happened in past use (a task was archived but its backend workspace was left running), so work through it as a checklist and report each step's result at the end.

The same steps apply to one task, a list ("close X, Y, Z"), or every merged task ("close merged tasks": find tasks whose PRs have merged, list them, and confirm the list before going ahead).

## Checklist (per task)

1. **Safety check (look it up, don't trust stored status).**
   - PR state: merged / open / none.
   - Unlanded work: local commits not pushed, and branches whose name differs from the upstream they track. Check the upstream itself, not just matching names.
   - Uncommitted changes in the worktree.
   - If anything is unlanded, stop and ask. Offer to push, to tag it (`git tag archive/<task>-<date>`), or to discard it, and record which in the archive.
2. **Write the archive summary** *before* cleanup, because session transcripts expire (~30 days). Use `templates/archive.md` at `tasks/archive/<task>.md`. Sources:
   - the task file (decisions, gotchas)
   - the PR(s): title, description, merge date
   - journal sections for this task. Condense them into the archive's `## Journal digest`: keep turning points, dead ends and why plans changed; drop routine progress. Once this is written, the raw journal sections are no longer the record of the task, so they can expire.
   - session transcripts, if available, for decisions that never got written down
3. **Route what was learned:**
   - Lessons and gotchas that apply beyond this task → `references/lessons.md`, using the format in `references/knowledge.md`. Run `home_repo.py lessons --find "<keywords>"` first; if a matching lesson exists, **reinforce** it (seen +1, last = today) instead of adding a duplicate.
   - If a lesson reaches `seen: 3`, or this task showed one was costly, mention it as a promotion candidate in the report (don't promote without the user's OK).
   - Follow-ups → `tasks/backlog.md`, not a new task, unless the user wants to start one now.
   - **Standing rules the user stated** while working on this task ("no commit without my approval", "never post PR comments automatically"): run `home_repo.py rules 3` and pick out the ones from this task's sessions. Propose where each belongs (`capture.md` placement table) and save the ones the user confirms. Users don't ask for these to be saved; past use showed them being lost.
4. **Update lists:** remove the task from `tasks/active.md`, and delete `tasks/<task>.md` now that the archive holds it.
5. **Clean up the backend** per `references/backends.md`. Some tools won't remove a task while it still has worktrees, so stop and clean those first. Run teardown commands from outside the home repo and never redirect their output into it (a teardown log once landed in the repo root).
6. **Verify.** Run `home_repo.py status`, and confirm the backend no longer lists the task **and** that its workspace directories are gone from disk. In past use, teardown ran but left workspaces behind in 2 of 5 closes, and the close still reported success. If anything remains, mark the step "needs attention" in the report; don't call the close done.
7. **Journal:** `## <task> HH:MM` with "closed; PR <ref>; <one-line outcome>".
8. **Pattern log:** if any step caused friction, add `- Friction: <one-liner>`.
9. **Commit** through `commit.md` (one commit for a bulk close).

## Report

End with a short table showing each task and each step's result (✓ / skipped / needs attention). Hiding a skipped step is worse than reporting it.
