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

## Repository layout

| Path | What |
|---|---|
| `trellis/` | The plugin: skill, routines, templates, helper script, hooks, evals, smoke test. |
| `.claude-plugin/marketplace.json` | Lets Claude Code install the plugin straight from this repo. |
| `home-repo-workspace/` | Benchmark summary for each eval iteration, with and without the skill (raw run outputs are kept out of git). |

## Development

- Smoke test (script and hooks, throwaway HOME): `bash trellis/tests/smoke.sh`
- Evals: `claude plugin eval ./trellis --scaffold --allow-tools Bash Write Edit` runs the cases in `trellis/evals/` with and without the plugin (results go to `trellis/evals/results/`, which git ignores). The cases need a shell, and the eval CLI only grants one where it can sandbox it, so run them on Linux or macOS (on Windows, use WSL with `bubblewrap` and `socat` installed). `--scaffold` runs each case's own `place-files.sh`.
- Validate manifests: `claude plugin validate .` and `claude plugin validate trellis`.

The design is driven by de-identified usage reports (counts, trigger words and friction, never work content), produced by the skill's `system-report` routine. Those reports are kept out of this repo; `trellis/README.md` summarizes what each one showed.

## License

MIT, see [LICENSE](LICENSE).
