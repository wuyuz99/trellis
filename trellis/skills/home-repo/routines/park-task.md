# Park or resume a task

*Kept on judgment; this wasn't needed in the first use cycle.* Real work gets blocked, deprioritized or interrupted. Without a park step, `active.md` fills with stale entries, or the context is lost when the task is dropped.

## Park ("park this", "put X on hold", "blocked on Y")

1. Update the task file's `## Next` with exactly where things stand, and add `Parked <date>: <reason / what it's waiting on>`.
2. Leave the task file and the backend workspace in place. Parking isn't closing.
3. Move the line from `tasks/active.md` to the top of `tasks/backlog.md`: `- **<task>** [parked]: <why parked>. File: tasks/<task>.md`.
4. Journal: `## <task> HH:MM` with "parked; <reason>".

## Resume ("pick X back up", "unpark X")

1. Read the task file. Check the backend's live state, since the base branch may have moved on and PRs may have changed.
2. Move the line back to `tasks/active.md`, and remove the `Parked` note or mark it as resumed.
3. Summarize for the user: why the task exists, decisions so far, and the next step.
