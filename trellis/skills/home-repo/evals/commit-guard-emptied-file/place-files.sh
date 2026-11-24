#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main
git -c user.name=eval -c user.email=eval@example.com add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm 'home repo before the session'
# the session's changes: one legitimate lesson, one accidentally emptied file
printf -- '- Use EXPLAIN ANALYZE before adding an index. (repo: orders-api; seen: 1; last: 2026-11-23; from: export-timeout)\n' >> references/lessons.md
: > tasks/backlog.md
