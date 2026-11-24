# Handoff prompt

Produce a prompt the user can paste into a fresh session (or another machine) so that session starts with the right context loaded.

1. Make sure the task file is current: update `## Next` with where things stand right now.
2. Output one code block:
   ```
   Task: <task> — <one-line why>.
   First read <home-repo>/tasks/<task>.md (decisions, gotchas, next steps) and <home-repo>/references/<only the relevant file>.
   Work in <repo/worktree path>, base <branch>.
   Next step: <the first item from ## Next>.
   When we finish or stop, use the home-repo skill to update the task file and journal.
   ```
3. Keep it short. The task file carries the detail; the prompt only points to it.
4. Append a journal bullet saying a handoff was generated.
