# Init: set up a home repo

Goal: a working repo in about 10 minutes, with nothing the user has to maintain by hand.

1. **Location.** Default to `~/projects/home-repo`. If the folder exists and isn't empty, show its contents and ask before touching anything. If the user already has a home repo or second brain, offer to adopt it: map their folders to this layout in their `CLAUDE.md` instead of moving files. Common shapes:
   - **Home Repo pattern** (an `AGENTS.md`, a `skills/` folder, shared docs, pointers to code repos): keep `AGENTS.md` as the map and add the Map/Ownership/Rules sections there. Don't create a second map; if Claude Code needs a `CLAUDE.md`, make it the single line `@AGENTS.md`. Keep `skills/` where it is; promoted skills go there.
   - **Obsidian vault or other second brain:** put the home repo in a subfolder of the vault, or point the `CLAUDE.md` map at the vault's existing folders. Don't rename or move their notes.
   - **A hand-run home repo** (its own routine guide such as `GUIDE.md`, an inbox, lessons without metadata): read the guide and copy any convention that differs from this skill's routines into the map as a one-line owner override; then offer to retire the guide, since the routines replace it (keep it until the user agrees). Run `lessons --lint` and offer to add metadata to existing lessons (`seen: 1`, `last:` from `git log` for that line). Leave the inbox as is.
2. **Look before asking.** Skim the folders under `~/projects`, the global `~/.claude/CLAUDE.md`, `~/.claude/skills`, and existing auto-memory. That tells you their tools and projects without asking.
3. **Ask at most 5 short questions:** role, current focus, task backend (worktree tool / git branches / none; see `references/backends.md`), working style, and anything that must never be stored. If step 2 showed other agents in use (Codex, Cursor, `AGENTS.md` files in their projects), ask whether the repo should be readable by them too; if so, the map goes in `AGENTS.md` and `CLAUDE.md` is the single line `@AGENTS.md`.
4. **Scaffold** with `git init`:
   - `CLAUDE.md` from `templates/CLAUDE.md`, under ~40 lines (or `AGENTS.md` + a one-line `CLAUDE.md`, per step 3)
   - `tasks/active.md`, `tasks/backlog.md`, `tasks/archive/.gitkeep`
   - `journal/`, `references/style.md` (from their answers), `references/lessons.md` (empty, with the format header)
   - `meta/pattern-log.md` from `templates/pattern-log.md`
   - `.gitignore`: `*.env`, `.env*`, `secrets/`, `*.key`, `*.pem`, `credentials*`, `.DS_Store`
   - Don't create tasks for old work. Task files exist only for current focus; others get one when they're touched.
5. **Record the location:** write `~/.claude/home-repo.json` with `{"path": "<absolute path>"}` so the hooks and script can find it.
6. **Global pointer.** Add a short section to `~/.claude/CLAUDE.md` (create the file if it's missing) and show the diff:
   ```
   ## Home repo
   My personal context lives at <path>. Use the home-repo skill for starting/ending days and sessions,
   creating/closing tasks, and anything to remember across projects.
   Hard rules: <the 1–3 rules that must hold in every session>.
   ```
   Hard rules go here, not in the repo, because every session loads this file. Tell the user that sessions already running won't see it until they restart.
7. **Commit** through `routines/commit.md`. Then ask whether to create a **private** remote (`gh repo create --private`). Never create a public one.
8. **Finish:** journal entry "Initial setup", and a pattern-log `Design:` line for each choice made. Show the tree and a 3-line cheat sheet of phrases.
