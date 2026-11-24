# Task backends

The home repo stores *why / decisions / next*. The backend holds the actual workspace. The repo's `CLAUDE.md` names the backend; follow its section here.

## Worktree manager (a tool that creates one task = one or more git worktrees)
- **New task:** create the tool's task first, and name the task file after it so the two can be matched.
- **No-branch work** (reading, reviews without changes, research): use one shared scratch task rather than creating tasks.
- **Close:** many tools refuse to remove a task that still has worktrees or running processes, so stop it, remove or clean its worktrees, then remove the task. Verify it no longer appears in the tool's list.
- **Review:** list the tool's tasks and find any without a task file or backlog entry.
- Don't use the tool's own note feature for context. Keeping it in the home repo avoids splitting context across two places.

## Plain git branches
- **New task:** `git switch -c <task>` (or `git worktree add ../<repo>-<task> -b <task>`) in each repo.
- **Close:** check each branch's upstream (`git rev-parse --abbrev-ref <branch>@{upstream}`, then `git log @{u}..<branch>`). The local name can differ from the pushed name. Delete local branches and worktrees only after the archive is written and unlanded work is handled.
- **Review:** `git for-each-ref refs/heads` per repo, and list branches with no task.

## None (notes only)
- Skip the workspace steps. A task is just its file. Close = archive + route lessons + remove from active.

## Status sources (look these up; never store them)
- PRs: `gh pr list --author @me`, `gh pr view <n> --json state,mergedAt,title`
- Tickets: whatever tracker the user names. Ask once and record the tool, not the status.
