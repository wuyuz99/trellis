# dashboard-filters

Ticket: none | Backend: worktree dashboard-filters | Repos: web (base main)
Why: support wants to filter orders by date range.

## Decisions
- 2026-11-24: date picker = react-day-picker (range mode), because it's already a dependency of `web`.

## Gotchas
- The picker returns local-time dates; the API assumes UTC (see lessons, frontend).

## Next
- Convert the selected range to UTC before the API call, then add tests for a range that crosses midnight.
