#!/usr/bin/env bash
# Smoke test for Trellis: every script command and both hooks, against sample repos in a throwaway HOME.
# Usage: bash tests/smoke.sh [path-to-trellis]   (default: this checkout). Exit 0 = all checks passed.
# Needs bash, git and Python 3.9+. Never touches your real ~/.claude or home repo.
set -u
SRC="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
T=$(mktemp -d)
export HOME="$T/home" USERPROFILE="$T/home"   # Python reads USERPROFILE on Windows
unset HOME_REPO
mkdir -p "$HOME/.claude/projects/proj"
cp -R "$SRC" "$T/trellis"
RUN="bash $T/trellis/hooks/run.sh"
EV="$T/trellis/skills/home-repo/evals"
fail=0
check() { if eval "$2" >/dev/null 2>&1; then echo "PASS  $1"; else echo "FAIL  $1"; fail=1; fi; }

echo "python: $( { python3 --version || python --version; } 2>/dev/null | head -1)  bash: $BASH_VERSION  git: $(git --version)"

# home repo in the default location, from the commit-guard sample (CLAUDE.md map)
mkdir -p "$HOME/projects/home-repo" && cd "$HOME/projects/home-repo"
bash "$EV/commit-guard-emptied-file/place-files.sh" >/dev/null 2>&1
cd "$T"

check "locate finds ~/projects/home-repo"   "$RUN locate | grep -qE 'projects[/\\]home-repo'"
check "now prints a timestamp"              "$RUN now | grep -qE '[0-9]{4}-[0-9]{2}-[0-9]{2}'"
check "status runs"                         "$RUN status | grep -q 'CLAUDE.md:'"
check "check-commit flags emptied file"     "cd $HOME/projects/home-repo && git add -A && ! $RUN check-commit"
check "lessons --lint runs"                 "$RUN lessons --lint"
check "lessons --repo runs"                 "$RUN lessons --repo /work/orders-api"
check "journal-expire runs"                 "$RUN journal-expire"

# transcripts: one real 3-prompt session, one 1-prompt session with many tool results
P="$HOME/.claude/projects/proj"
PN=$(cygpath -m "$P" 2>/dev/null || echo "$P")   # path as the native Python sees it (Windows)
{ for m in "fix the export" "never push without my approval" "ok thanks"; do
    printf '{"type":"user","message":{"role":"user","content":"%s"},"cwd":"/work/orders-api","timestamp":"2026-11-23T10:00:00Z"}\n' "$m"; done; } > "$P/real.jsonl"
{ printf '{"type":"user","message":{"role":"user","content":"run the tests"},"cwd":"/work/orders-api"}\n'
  for i in 1 2 3 4; do printf '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"ok"}]},"cwd":"/work/orders-api"}\n'; done; } > "$P/toolheavy.jsonl"

check "usage runs"                          "$RUN usage 30"
check "rules finds the stated rule"         "$RUN rules 30 | grep -q 'never push without my approval'"

# hooks
check "SessionStart prints repo + task pointer" \
  "echo '{\"cwd\":\"/work/orders-api\",\"session_id\":\"s1\"}' | $RUN hook-session-start | grep -q 'related to'"
check "SessionEnd records a real unjournaled session" \
  "echo '{\"cwd\":\"/work/orders-api\",\"transcript_path\":\"$PN/real.jsonl\"}' | $RUN hook-session-end && grep -q real.jsonl $HOME/projects/home-repo/meta/pending.md"
check "SessionEnd ignores a 1-prompt session with tool results" \
  "echo '{\"cwd\":\"/work/orders-api\",\"transcript_path\":\"$PN/toolheavy.jsonl\"}' | $RUN hook-session-end && ! grep -q toolheavy.jsonl $HOME/projects/home-repo/meta/pending.md"
check "hooks exit 0 with no home repo"      "HOME=$T/empty USERPROFILE=$T/empty $RUN hook-session-start </dev/null"

# AGENTS.md repo via HOME_REPO
mkdir -p "$T/agents" && (cd "$T/agents" && bash "$EV/agents-md-start-day/place-files.sh" >/dev/null 2>&1)
check "AGENTS.md repo located via HOME_REPO" "HOME_REPO=$T/agents $RUN status | grep -q 'AGENTS.md:'"

rm -rf "$T"
[ $fail = 0 ] && echo "all checks passed" || echo "some checks FAILED"
exit $fail
