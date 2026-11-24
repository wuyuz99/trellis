# End session / end of day

Journaling is the routine people forget most. Do it quickly, and draft it yourself; don't ask the user to dictate.

1. **Get the time** from `home_repo.py now`.
2. **Draft from the session itself.** What was worked on, decisions made, problems hit, and where things stand. Write 1–10 bullets, each something a future session would want to know. Skip routine actions ("ran tests").
3. **Append** to `journal/YYYY-MM-DD.md` (create it with `# YYYY-MM-DD` if it's missing) under `## <task or "misc"> HH:MM`. Append only; other sessions may be writing too.
4. **Update the task file's `## Next`** if a task was worked on. This is what the next session will read first.
5. **Lessons:** if something reusable came up (a gotcha, a command that worked), add it to `references/lessons.md` (format: `references/knowledge.md`). Search first and reinforce a match rather than duplicating it. If a recalled lesson (from the session-start note) helped this session, reinforce it too.
6. **Standing rules:** if the user stated a rule this session ("don't X without my approval", "from now on…"), offer to save it (`capture.md` placement). `home_repo.py rules 1` lists candidates.
7. **Pattern log:** if the home-repo system itself got in the way, add a `Friction:` line.
8. **End of day** (as opposed to end of a single session): also offer to commit, through `commit.md`.
9. Never save a status snapshot (PR states, ticket lists) instead of a journal entry. In past use that wrong-place save happened when the routine wasn't loaded.

## Catching up (pending sessions)

The SessionEnd hook adds a line to `meta/pending.md` for sessions that ended without a journal entry. When asked (or from start-day):
1. For each pending line, look at that session's transcript if it's available (the path is in the line) and draft a short journal section, marked `(drafted later)`.
2. Show the drafts. Append the ones the user approves, and drop the rest.
3. Remove the handled lines from `meta/pending.md`.
