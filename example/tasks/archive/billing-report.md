# billing-report: monthly billing report times out

Closed 2026-09-05 | PR orders-api#377 (merged 2026-09-05) | Ticket OPS-290 | Repos orders-api | Role author

## What and why
The monthly billing report hit the database statement timeout once the largest accounts passed a year of history.

## Outcome
- Report runs in 40s with a per-session statement_timeout. An index on (account_id, billed_at) was tried and dropped: it didn't change the plan.

## Decisions
- 2026-09-02: set statement_timeout per session for the report only, because raising the global timeout would hide slow queries elsewhere.

## Gotchas
- Set statement_timeout per session for long-running queries. (Also in references/lessons.md.)

## Journal digest
- 2026-09-01: reproduced on a copy of the largest account; the query plan was fine, the timeout was the limit.
- 2026-09-02: index experiment showed no gain; switched to the per-session timeout.

## Follow-ups
- none

## Unlanded work
- none
