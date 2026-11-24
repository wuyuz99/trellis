# How knowledge builds up

Built-in agent memory saves isolated facts and never revisits them: nothing records where a fact came from, whether it still holds, or whether it keeps mattering. The home repo goes further in four ways. The fourth, removing what isn't needed, matters as much as the first three: stale and contradicting instructions are the most common way agent memory goes wrong.

## 1. Every lesson carries its history

Lessons live in `references/lessons.md`, grouped by `## <area>`, one line each:

```
- <lesson, written as an instruction>. (repo: <repo or *>; seen: <N>; last: <YYYY-MM-DD>; from: <task>[; cost: <low|med|high> <what it cost>])
```

- `repo:` says where it applies. Use `*` for "anywhere", or several separated by commas. This drives recall (section 3).
- `seen:` is how many separate times it has mattered: it caused a problem, or knowing it prevented one.
- `last:` is the last date it mattered or was confirmed.
- `from:` is the task where it was first learned. Keep the first one; don't overwrite it.
- `cost:` (optional) is what the worst occurrence cost, e.g. `cost: high 2h debugging` or `cost: high broke a commit`. Add it when a lesson was expensive; leave it out for minor ones. A failure that's expensive once can justify a check without waiting for it to recur.

**Before adding a lesson, search for an existing one** (`home_repo.py lessons --find "<keywords>"`). If you find a match, **reinforce** it: increase `seen`, set `last` to today, and sharpen the wording if the new case adds something. Don't add a near-duplicate. Duplicates hide the fact that something keeps recurring, and that's the signal that matters most.

## 2. Knowledge moves up as it proves itself

```
journal bullet → task Gotcha → lesson (seen 1) → lesson (seen ≥3) → rule / check / skill
     raw            one task       cross-task       recurring        enforced
```

| Step | When | Who decides |
|---|---|---|
| journal → task Gotcha | it cost time on this task | agent |
| Gotcha → lesson | it would help on a *different* task (checked at close) | agent |
| lesson reinforced | it mattered again | agent |
| lesson → enforced | `seen ≥ 3`, or `cost: high` | **agent proposes, user approves** |

"Enforced" means the cheapest form that makes the mistake hard to repeat:
1. A line in the relevant project's `CLAUDE.md`, or the global hard rules if it applies everywhere (see `routines/capture.md`).
2. A check in a script or hook. For example, the commit guard here exists because a commit once emptied a file.
3. A step in a routine checklist, or a new skill if it's a multi-step workflow. A new skill goes in the home repo's `skills/` folder if it has one (Home Repo pattern), so it's versioned with the lesson that produced it. Claude Code doesn't load skills from that folder on its own, so also link it into `~/.claude/skills/` (or follow the repo's own install step if it has one). Without a `skills/` folder, write it to `~/.claude/skills/` directly.

After promoting a lesson, mark it `(…; promoted: <where>)`. Keep it in lessons.md, since it still explains *why* the rule exists.

Checks are earned, not assumed: if a lesson has `seen: 1` and low cost, keep it as a lesson. A check that nothing ever trips is maintenance with no payoff.

## 3. Recall at the right moment

The agent shouldn't have to remember to search. The SessionStart hook works out the current repo from the working directory and lists the lessons tagged for it (or `*` with a matching area), up to a short limit. A matching task file is pointed to the same way. Before starting work in a repo, skim those lessons. When one of them saves you from a mistake, reinforce it.

## 4. Demotion: remove what isn't needed

Every line in an always-loaded file (the repo's `CLAUDE.md`, the global home-repo section, a project `CLAUDE.md` a lesson was promoted into) costs context in every session. Over time, rules contradict each other and crowd out the task at hand. Prose rules have to keep earning their place.

| Candidate | Why | Usual action |
|---|---|---|
| A promoted **prose rule** whose lesson hasn't come up for 90+ days (`lessons --demote`) | Either the model now does this unprompted, or the situation no longer arises | Delete the line, or move it to a reference file the map points to |
| A rule the agent follows correctly **without** it | Instruction that changes nothing | Delete |
| A prose rule that's still ignored sometimes | Prose isn't working | Convert it to a check or hook (that's promotion, not demotion) |
| Two rules that conflict | Conflicts are resolved randomly per session | Keep the newer one and delete the other; note it in the pattern log |

**Checks and hooks cost no context, so they are not demotion candidates** just because they never fire. A check that never trips is doing its job. Remove one only if it's noisy or the thing it guards no longer exists.

**How to decide.** The best evidence is a with-and-without test: run a representative task with the rule and without it (e.g. two fresh sessions, or the plugin's eval cases). If the result doesn't change, the rule goes. Without that, ask the user, showing the rule, when it was last needed, and what removing it risks.

Mark the lesson `(…; demoted: <YYYY-MM-DD> <what was done>)` and add a pattern-log `Design:` line. The lesson stays in lessons.md as history; only the always-loaded copy goes.

## Checking during a review
- `home_repo.py lessons --promote` lists candidates (`seen ≥ 3` or `cost: high`, not yet promoted). Propose each one to the user with a suggested form.
- `home_repo.py lessons --demote` lists promoted lessons that haven't mattered for 90+ days. Apply section 4.
- `home_repo.py lessons --stale` lists lessons seen once and untouched for 90+ days. Ask whether each one still holds. Keep it, reword it, or delete it. Don't delete silently.
- If a lesson names a command, path or setting, check that it still exists. If it doesn't, update or retire the lesson.
- `home_repo.py lessons --lint` lists lines missing the metadata. Add it, using the source task if it's known, or today's date with `from: unknown`.
