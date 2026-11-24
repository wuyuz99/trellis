# Lessons
## database
- Set statement_timeout per session for long-running queries. (repo: orders-api; seen: 2; last: 2026-11-18; from: billing-report)
- For large exports use the raw cursor with fetchmany(5000); the ORM iterator prefetches every row. (repo: orders-api; seen: 1; last: 2026-11-20; from: export-timeout)
## frontend
- Convert dates to UTC ISO strings before sending them to the API; the API assumes UTC. (repo: web; seen: 3; last: 2026-11-19; from: invoice-page)
- Run the snapshot tests with TZ=UTC or they fail on laptops. (repo: web; seen: 1; last: 2026-06-02; from: unknown)
## tooling
- Prefer pnpm over npm in web
