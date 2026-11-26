# Trellis

*Your agent's lessons grow into rules, and get pruned when they stop paying off.*

Trellis is a Claude Code plugin for keeping a **home repo**: one private, git-tracked folder of markdown with your tasks, decisions, lessons, journal and working style, which every agent session can draw on from any project. It implements the [Home Repo pattern](https://aihero.dev/the-home-repo-pattern) and focuses on what most setups skip: keeping that folder useful over time.

- **Tasks carry context between sessions.** Starting, handing off and closing a task is when context is written and passed on.
- **Upkeep happens as a side effect.** The routines you already run write the journal, lessons and notes, so there are no capture phrases to remember.
- **Lessons earn their place.** They're reinforced when they recur, promoted into rules, checks or skills once proven, and pruned from always-loaded files when they stop paying off.

```
/plugin marketplace add wuyuz99/trellis
/plugin install trellis@trellis
```

Then say "set up my home repo" (or "adopt my home repo"). Full documentation, privacy notes and the evidence behind each feature: [`trellis/README.md`](trellis/README.md).

## What a day looks like

An illustrative session, using the fictional repo in [`example/`](example/) (shortened):

```text
you:    what's on today?
claude: Active:
        - export-timeout (orders-api): address the review comments on PR #412, then merge.
          (I looked the PR up: 2 comments, both small.)
        - dashboard-filters (web): convert the selected range to UTC before the API call.
        Suggested focus: finish export-timeout, since it's one step from done.

        ── later, in a new session started in the export-timeout workspace ──
[home-repo] This directory is task tasks/export-timeout.md. Read it before starting work.
[home-repo] Lessons for this repo (references/lessons.md; reinforce any that help):
  - For large exports use the raw cursor with fetchmany(5000); the ORM iterator prefetches…

you:    PR's merged, close this
claude: Closed export-timeout:
        Safety check   ✓ merged; nothing unpushed or uncommitted
        Archive        ✓ tasks/archive/export-timeout.md (decisions, gotchas, journal digest)
        Lessons        ✓ reinforced the fetchmany lesson (seen 1 → 2), no duplicate
        Lists          ✓ removed from tasks/active.md, task file deleted
        Workspace      ✓ worktree removed; verified the folder is gone from disk
        Journal        ✓ ## export-timeout 16:42
        Commit the home repo?
```

You never ask it to write the journal or save lessons: closing the task does it. The next session that touches `orders-api` gets the reinforced lesson.

## Repository layout

| Path | What |
|---|---|
| `trellis/` | The plugin: skill, routines, templates, helper script, hooks, evals, smoke test. |
| `.claude-plugin/marketplace.json` | Lets Claude Code install the plugin straight from this repo. |
| `example/` | A small fictional home repo showing what Trellis keeps (not part of the plugin). |
| `home-repo-workspace/` | Benchmark summary for each eval iteration, with and without the skill (raw run outputs are kept out of git). |

## Development

- Smoke test (script and hooks, throwaway HOME): `bash trellis/tests/smoke.sh`
- Evals: `claude plugin eval ./trellis --scaffold --allow-tools Bash Write Edit` runs the cases in `trellis/evals/` with and without the plugin (results go to `trellis/evals/results/`, which git ignores). The cases need a shell, and the eval CLI only grants one where it can sandbox it, so run them on Linux or macOS (on Windows, use WSL with `bubblewrap` and `socat` installed). `--scaffold` runs each case's own `place-files.sh`.
- Validate manifests: `claude plugin validate .` and `claude plugin validate trellis`.

The design is driven by de-identified usage reports (counts, trigger words and friction, never work content), produced by the skill's `system-report` routine. Those reports are kept out of this repo; `trellis/README.md` summarizes what each one showed.

## License

MIT, see [LICENSE](LICENSE).
