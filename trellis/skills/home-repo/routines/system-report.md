# System report (de-identified)

*Kept on judgment.* This produces a report on **how the system is used**, never on what the user worked on, so it can be shared to improve this skill or compare setups. It turns the manual process used to design v0 into a routine.

Write only `meta/system-report-YYYY-MM-DD.md`. Don't commit or push it; the user moves it themselves.

## Allowlist (the only kinds of thing the report may contain)
- Structure: the system's own file and folder names. Other files become generic labels ("reference-file-3").
- Counts and sizes: files, entries, lines, approximate tokens, commits, routine use.
- Categories: each saved item gets one type: fact | decision | command/snippet | preference | task | troubleshooting | link | other
- Trigger phrases: only the trigger words the user typed.
- System events, described generically: unprompted loads, misfires, corrections, duplicates, wrong-place saves.
- Template shapes, with values replaced by placeholders (<project>, <decision>).
- An assessment of the system: friction, gaps, skill candidates, described abstractly.

## Never, not even in paraphrase
Content of journals, tasks or references; project, client, employer or people names; code, commands, URLs, hosts, IPs, paths outside the repo's own structure; secrets or account names. If you're unsure, leave it out. Paraphrase can leak too: "switched the billing service's DB" is a leak.

## Sections
0. **Run context and hypotheses** (first, because they are why the report exists). Context: plugin version, date range, sessions analyzed, active days, which file is the map (`CLAUDE.md`, `AGENTS.md`, or an import). Then, for each question below, the numbers, how they were measured, and a verdict: supported / not supported / not enough data. Never estimate; say what couldn't be measured.
   - **H1. Context loading.** When a task file was relevant, was it read early and unprompted / only when asked / late / never? How often did the SessionStart hook point at a task?
   - **H2. Lesson reuse.** Lessons recalled at session start, and how many of those were later reinforced; lessons new / reinforced / promoted / demoted (from `usage`); near-duplicates.
   - **H3. Unjournaled sessions.** `pending.md` entries classified as real / trivial (false alarm) / journaled later; whether start-day caught up on them.
   - **H4. Task matching.** Hook pointed at the right task / the wrong task / no pointer when a matching task existed (wrong cases described generically).
   - **H5. Triggering.** Missed (a routine was meant but not used) and false (used for code review, project commits, the agent's todo list…), by trigger word and count.
   - **H6. Upkeep.** How often review, demotion, `journal-expire` and archive digests ran, and which were declined.

   Keep this list in step with the README's "Known gaps": add a question when a feature ships on judgment, and drop one once two reports agree.
1. Structure (generic tree + sizes) · 1b. Reads vs. writes per file, never-read files, lesson flow (from `usage`) · 2. Always-loaded cost (repo `CLAUDE.md` + global section) · 3. `CLAUDE.md` skeleton · 4. Activity (commits/day, entries per folder, most-changed files) · 5. Saved items by type · 6. Triggers (phrase → count, undocumented flagged) · 7. Context loading (unprompted vs. asked, which file) · 8. Misfires and corrections · 9. Per-routine use and friction · 10. pattern-log rewritten generically · 11. Skill candidates · 12. User answers. Ask these one at a time: reused? useless? wanted to save but skipped? slow or forgotten routine? surprises? did anything the hooks showed at session start feel wrong or get in the way?

## Process
- Start with `home_repo.py usage 30`: reads vs. writes per file and lesson new/reinforced/promoted/demoted counts. Report it with generic labels for non-system files. **The health metric is reads, not writes**: what fraction of what was saved got read again, and how many recalled lessons were reinforced. Writes alone only show that the system is busy.
- Counts from shell commands are heuristic (a command that mentions the repo path is attributed to the files it names), so present them as approximate.
- Read session logs (`~/.claude/projects/**/*.jsonl`) only to count and classify. Never copy from them.
- Before showing the report, check every line against the allowlist, then say how many lines were removed or rewritten.
- Show the full report and wait for approval. The user may ask for more removals.
- If a previous report exists, add a short "Changes since <date>" section comparing the numbers.
