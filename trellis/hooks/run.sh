#!/usr/bin/env bash
# Run home_repo.py with the first working Python >= 3.9 (python3 on macOS/Linux, python or py on Windows).
# Hooks must never break a session, so exit 0 quietly if no Python is found.
script="$(dirname "$0")/../skills/home-repo/scripts/home_repo.py"
for p in python3 python py; do
  if command -v "$p" >/dev/null 2>&1 && "$p" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
    exec "$p" "$script" "$@"
  fi
done
exit 0
