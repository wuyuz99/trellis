# billing-report: monthly billing report times out

Closed 2026-09-05 | PR orders-api#377 (merged 2026-09-05) | Ticket OPS-290 | Repos orders-api | Role author

## What and why
The monthly billing report hit the DB statement timeout.

## Outcome
- Report runs in 40s with a per-session statement_timeout.
