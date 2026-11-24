# export-timeout

Ticket: OPS-311 | Backend: none | Repos: orders-api (base main)
Why: CSV export for accounts with >200k orders hits the 30s gateway timeout.

## Decisions
- 2026-11-20: stream rows with a server-side cursor instead of building the file in memory, because memory spiked to 2GB.

## Gotchas
- The ORM's default iterator prefetches everything; use the raw cursor with fetchmany(5000).

## Next
- Address review comments on PR #412, then merge.

## Links
- PR orders-api#412: the streaming change.
