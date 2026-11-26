#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main
git -c user.name=eval -c user.email=eval@example.com add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm 'home repo (Home Repo pattern: AGENTS.md map, skills/ folder)'
