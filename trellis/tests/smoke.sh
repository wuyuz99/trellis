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
H="$HOME/projects/home-repo"
G="git -c core.autocrlf=false -c user.name=smoke -c user.email=smoke@example.com"
fail=0
# each check runs in a subshell, so a `cd` or variable in one check can't leak into the next
check() { if ( eval "$2" ) >/dev/null 2>&1; then echo "PASS  $1"; else echo "FAIL  $1"; fail=1; fi; }
# check-commit must exit 2 (blocked) and name the finding
guard_blocks() { local out; out=$($RUN check-commit); [ $? = 2 ] && printf '%s\n' "$out" | grep -qF -- "$1"; }
native() { cygpath -m "$1" 2>/dev/null || echo "$1"; }   # path as the native Python sees it (Windows)

echo "python: $( { python3 --version || python --version; } 2>/dev/null | head -1)  bash: $BASH_VERSION  git: $(git --version)"

# home repo in the default location, from the commit-guard sample (CLAUDE.md map)
mkdir -p "$H" && (cd "$H" && bash "$EV/commit-guard-emptied-file/place-files.sh" >/dev/null 2>&1)
cd "$T"

check "locate finds ~/projects/home-repo"   "$RUN locate | grep -qE 'projects[/\\]home-repo'"
check "now prints a timestamp"              "$RUN now | grep -qE '[0-9]{4}-[0-9]{2}-[0-9]{2}'"
check "status runs"                         "$RUN status | grep -q 'CLAUDE.md:'"
check "check-commit flags emptied file"     "cd $H && git add -A && guard_blocks 'EMPTIED: tasks/backlog.md'"
(cd "$H" && git reset -q && git checkout -q -- . && git clean -qfd)   # back to the committed sample
check "lessons --lint runs"                 "$RUN lessons --lint"
check "lessons --repo runs"                 "$RUN lessons --repo /work/orders-api"
check "journal-expire runs"                 "$RUN journal-expire"

# commit guard on non-ASCII and renamed paths (a repo of its own, via HOME_REPO)
U="$T/unicode" && mkdir -p "$U/tasks" && (cd "$U" && git init -q -b main && echo '# map' > CLAUDE.md && echo '# Active' > tasks/active.md \
  && seq 1 20 > "tasks/导出超时.md" && seq 1 20 | sed 's/^/backlog item /' > tasks/backlog.md && $G add -A && $G commit -qm init)
check "check-commit flags emptied non-ASCII file" \
  "cd $U && : > 'tasks/导出超时.md' && git add -A && HOME_REPO=$U guard_blocks 'EMPTIED: tasks/导出超时.md'"
(cd "$U" && git checkout -q HEAD -- . && git reset -q)
check "check-commit flags a renamed file that shrank" \
  "cd $U && mkdir -p tasks/archive && git mv tasks/backlog.md tasks/archive/backlog.md && sed -i '9,\$d' tasks/archive/backlog.md && git add -A \
   && HOME_REPO=$U guard_blocks 'SHRANK: tasks/backlog.md -> tasks/archive/backlog.md (renamed)'"
(cd "$U" && git reset -q --hard)

# lesson counts from git history: one lesson added, then reinforced + promoted, then reworded
(cd "$U" && mkdir -p references \
  && echo '- Old wording. (repo: x; seen: 1; last: 2026-11-01)' > references/lessons.md && $G add -A && $G commit -qm l1 \
  && echo '- Old wording. (repo: x; seen: 2; last: 2026-11-02; promoted: CLAUDE.md)' > references/lessons.md && $G commit -qam l2 \
  && echo '- New wording. (repo: x; seen: 2; last: 2026-11-03; promoted: CLAUDE.md)' > references/lessons.md && $G commit -qam l3)
check "usage counts each lesson change once" \
  "HOME_REPO=$U $RUN usage 30 | grep -q 'lessons in window: 1 new, 1 reinforced, 1 promoted, 0 demoted'"

# transcripts: one real 3-prompt session, one 1-prompt session with many tool results
P="$HOME/.claude/projects/proj"
PN=$(native "$P")
HN=$(native "$H")
TODAY=$(date +%F)
# transcript records: user PROMPT [TIMESTAMP]; tool NAME FILE [TIMESTAMP] (default: today 10:00 UTC)
user() { printf '{"type":"user","message":{"role":"user","content":"%s"},"cwd":"/work/orders-api","timestamp":"%s"}\n' "$1" "${2:-${TODAY}T10:00:00Z}"; }
tool() { printf '{"type":"assistant","timestamp":"%s","message":{"role":"assistant","content":[{"type":"tool_use","name":"%s","input":{"file_path":"%s"}}]}}\n' "${3:-${TODAY}T10:00:00Z}" "$1" "$2"; }
{ for m in "fix the export" "never push without my approval" "ok thanks"; do user "$m"; done; } > "$P/real.jsonl"
{ printf '{"type":"user","message":{"role":"user","content":"run the tests"},"cwd":"/work/orders-api"}\n'
  for i in 1 2 3 4; do printf '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"ok"}]},"cwd":"/work/orders-api"}\n'; done; } > "$P/toolheavy.jsonl"
{ for m in "where was I" "ok" "thanks"; do user "$m"; done; tool Read "$HN/journal/$TODAY.md"; } > "$P/readjournal.jsonl"
{ for m in "end of day" "ok" "thanks"; do user "$m"; done; tool Edit "$HN/journal/$TODAY.md"; } > "$P/wrotejournal.jsonl"
# last prompt before midnight; the assistant writes the next day's journal after it (local timestamps)
{ for m in "late fix" "ok" "wrap up"; do user "$m" 2026-01-01T23:55:00; done
  tool Write "$HN/journal/2026-01-02.md" 2026-01-02T00:05:00; } > "$P/midnight.jsonl"
{ user "x"; tool Read "${HN}-workspace/iteration-1/sibling.md"; tool Read "$HN/tasks/active.md"; } > "$P/sibling.jsonl"

check "usage runs, ignores a sibling folder" "out=\$($RUN usage 30) && echo \"\$out\" | grep -q 'tasks/active.md' && ! echo \"\$out\" | grep -q 'sibling'"
check "rules finds the stated rule"         "$RUN rules 30 | grep -q 'never push without my approval'"

# hooks
start() { echo "{\"cwd\":\"$1\",\"session_id\":\"s1\"}" | $RUN hook-session-start; }
end() { echo "{\"cwd\":\"/work/orders-api\",\"transcript_path\":\"$PN/$1\"}" | $RUN hook-session-end; }
check "SessionStart points at tasks for the repo" \
  "start /work/orders-api | grep -q 'Open tasks in this repo: tasks/export-timeout.md'"
check "SessionStart ignores a task name inside a longer folder name" \
  "! start /work/export-timeout-notes | grep -q 'tasks/export-timeout.md'"
# a workspace named after its task: only that task, even though another task lists the same repo
printf '# Other\n\nTicket: none | Backend: none | Repos: orders-api (base main)\n' > "$H/tasks/other-orders.md"
check "SessionStart prefers the task named by the folder" \
  "out=\$(start /work/orders-api/export-timeout) && echo \"\$out\" | grep -q 'This directory is task tasks/export-timeout.md' && ! echo \"\$out\" | grep -q other-orders"
rm "$H/tasks/other-orders.md"
# recall: 2 fixed slots + 3 rotating, stable within a session, varying across sessions
cp "$H/references/lessons.md" "$T/lessons.bak"
for i in $(seq 1 12); do printf -- '- Rotating lesson %02d. (repo: orders-api; seen: 1; last: 2026-11-%02d)\n' "$i" "$i" >> "$H/references/lessons.md"; done
recall() { echo "{\"cwd\":\"/work/orders-api\",\"session_id\":\"$1\"}" | $RUN hook-session-start | grep '^  - '; }
check "SessionStart recall is stable within a session" "[ \"\$(recall a)\" = \"\$(recall a)\" ]"
check "SessionStart recall rotates across sessions" \
  "[ \$(for s in a b c d e f; do recall \$s; done | sort -u | wc -l) -gt 5 ] && [ \$(recall a | wc -l) = 5 ]"
cp "$T/lessons.bak" "$H/references/lessons.md"
printf -- '## git\n- Check the staged diff for emptied files before committing. (repo: *; seen: 1; last: 2026-11-20; cost: high)\n' >> "$H/references/lessons.md"
check "SessionStart recalls lessons tagged repo: *" \
  "start /work/orders-api | grep -q 'staged diff for emptied files'"
check "SessionEnd records a real unjournaled session" \
  "end real.jsonl && grep -q real.jsonl $H/meta/pending.md"
check "SessionEnd ignores a 1-prompt session with tool results" \
  "end toolheavy.jsonl && ! grep -q toolheavy.jsonl $H/meta/pending.md"
check "SessionEnd records a session that only read today's journal" \
  "end readjournal.jsonl && grep -q readjournal.jsonl $H/meta/pending.md"
check "SessionEnd skips a session that wrote today's journal" \
  "end wrotejournal.jsonl && ! grep -q wrotejournal.jsonl $H/meta/pending.md"
check "SessionEnd skips a session that journaled after midnight" \
  "end midnight.jsonl && ! grep -q midnight.jsonl $H/meta/pending.md"
mkdir -p "$T/empty/cwd"
check "hooks exit 0 with no home repo" \
  "cd $T/empty/cwd && out=\$(HOME=$T/empty USERPROFILE=$T/empty $RUN hook-session-start </dev/null) && [ -z \"\$out\" ]"
check "invalid HOME_REPO does not fall back to the default repo" \
  "! HOME_REPO=$T/empty $RUN locate"

# AGENTS.md repo via HOME_REPO
mkdir -p "$T/agents" && (cd "$T/agents" && bash "$EV/agents-md-start-day/place-files.sh" >/dev/null 2>&1)
check "AGENTS.md repo located via HOME_REPO" "HOME_REPO=$T/agents $RUN status | grep -q 'AGENTS.md:'"

cd / && rm -rf "$T"
[ $fail = 0 ] && echo "all checks passed" || echo "some checks FAILED"
exit $fail
