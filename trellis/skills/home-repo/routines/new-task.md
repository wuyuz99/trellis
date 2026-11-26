# New task

Users describe the *work* ("I have a new task to fix the export timeout"), not a name and repo list, so work those out from what they said.

1. **Check for an existing entry.** Look through `tasks/active.md`, `tasks/backlog.md` and recent `tasks/archive/`.
   - If it's in the backlog, promote it: remove it from backlog.md and create the task file from its notes.
   - If it's a recently closed task (re-opened for follow-ups), don't create a near-duplicate. Re-open the existing one: move the archive file back to `tasks/<task>.md`, add a `## Reopened <date>` note, and archive it again at the end. Past use showed churn when a closed task was re-created separately.
2. **Propose, then confirm:** a short kebab-case name, the repos involved, the base branch, and ticket if any. Ask only for what you can't infer.
3. **Create `tasks/<task>.md`** from `templates/task.md`, *before* the workspace. Fill in `Why` from the user's description. Leave `Decisions` empty rather than inventing any. Order matters: a tool that opens a session in the new workspace runs the SessionStart hook at once, and in past use every such session started before its task file existed, so the hook couldn't point at it (0 of 10).
4. **Create the backend workspace** (worktree tool task or branch) per `references/backends.md`, with the same name as the task file so the hook can match them. Work with no branch goes in one shared scratch task, not a new task file.
5. **Add one line to `tasks/active.md`.**
6. Append a journal entry: `## <task> HH:MM` with "created; <one-line why>".
7. Offer a handoff prompt if the work will happen in another session (see `handoff.md`).
