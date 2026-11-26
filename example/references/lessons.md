# Lessons
## database
- Set statement_timeout per session for long-running queries. (repo: orders-api; seen: 2; last: 2026-11-18; from: billing-report)
- For large exports use the raw cursor with fetchmany(5000); the ORM iterator prefetches every row. (repo: orders-api; seen: 1; last: 2026-11-20; from: export-timeout)
## frontend
- Convert dates to UTC ISO strings before sending them to the API; the API assumes UTC. (repo: web; seen: 4; last: 2026-11-24; from: invoice-page, dashboard-filters)
## git
- Compare branches by their upstream (git rev-parse @{upstream}), not by name. (repo: *; seen: 4; last: 2026-07-01; from: branch-triage; promoted: CLAUDE.md rule)
- Check the staged diff for emptied files before committing. (repo: *; seen: 1; last: 2026-11-20; from: planning-cleanup; cost: high, broke a commit and lost the backlog for a day)
