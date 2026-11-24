#!/usr/bin/env python3
"""Mechanical helpers for the home-repo skill. Standard library only.

Usage:
  home_repo.py locate                 print the home repo path (exit 1 if not found)
  home_repo.py now                    print local date and time for journal headings
  home_repo.py status                 health summary: active tasks, pending, uncommitted, budget, empty files
  home_repo.py check-commit           inspect the STAGED diff for emptied/deleted files and likely secrets
  home_repo.py lessons [--find WORDS | --repo [DIR] | --promote | --demote | --stale | --lint]
                                      search, recall, and maintain references/lessons.md
  home_repo.py usage [DAYS]           reads vs writes per home-repo file from session transcripts (default 30 days),
                                      plus lesson reinforcement counts from git history
  home_repo.py journal-expire [WEEKS] list journal files older than WEEKS (default 6) whose tasks are all closed
  home_repo.py rules [DAYS]           standing rules the user stated in recent sessions (default 14 days): capture candidates
  home_repo.py hook-session-start     (hook) print a short context note for a new session
  home_repo.py hook-session-end       (hook) record an unjournaled session in meta/pending.md
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CLAUDE_MD_BUDGET = 40
CONFIG = Path.home() / ".claude" / "home-repo.json"

SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"), "GitHub token"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "API key (sk-)"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), "JWT"),
    (re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*['\"]?[^\s'\"<>]{8,}"), "credential assignment"),
]


# ---------- helpers ----------

def locate() -> Path | None:
    explicit = []  # (where the setting came from, path)
    env, has_config = os.environ.get("HOME_REPO"), CONFIG.is_file()
    configured = bool(env) or has_config
    if env:
        explicit.append(("$HOME_REPO", Path(env).expanduser()))
    if has_config:
        try:
            explicit.append((str(CONFIG), Path(json.loads(CONFIG.read_text(encoding="utf-8"))["path"]).expanduser()))
        except (ValueError, KeyError, OSError, TypeError):
            print(f"home-repo: cannot read {CONFIG}", file=sys.stderr)
    candidates = [p for _, p in explicit]
    cwd = Path.cwd()
    if (cwd / "tasks" / "active.md").is_file():
        candidates.append(cwd)  # running inside a home repo
    if not configured:
        # default locations only when nothing is configured: a configured repo that isn't valid
        # must not silently hand over to another repo (e.g. an old one in ~/projects/home-repo)
        candidates += [Path.home() / "home-repo", Path.home() / "projects" / "home-repo"]
    for c in candidates:
        if map_file(c) is not None:
            return c.resolve()
    for src, p in explicit:
        print(f"home-repo: {p} (from {src}) has no CLAUDE.md or AGENTS.md; not falling back to a default location",
              file=sys.stderr)
    return None


def map_file(repo: Path) -> Path | None:
    """The repo's always-loaded map: CLAUDE.md, or AGENTS.md (Home Repo pattern / other agents).

    When CLAUDE.md is only an `@AGENTS.md` import, AGENTS.md is the real map."""
    claude, agents = repo / "CLAUDE.md", repo / "AGENTS.md"
    if agents.is_file():
        if not claude.is_file():
            return agents
        try:
            if "@AGENTS.md" in claude.read_text(encoding="utf-8", errors="replace"):
                return agents
        except OSError:
            pass
    return claude if claude.is_file() else None


def is_git_repo(repo: Path) -> bool:
    """True only if the home repo is its own git repo (never fall through to a parent repo)."""
    return (repo / ".git").exists()


def git(repo: Path, *args: str, check: bool = False) -> str:
    if not is_git_repo(repo):
        if check:
            raise RuntimeError(f"{repo} is not a git repository")
        return ""
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def count_lines(text: str) -> int:
    return len(text.splitlines())


def require_repo() -> Path:
    repo = locate()
    if not repo:
        print("home repo not found (set HOME_REPO or ~/.claude/home-repo.json)", file=sys.stderr)
        sys.exit(1)
    return repo


def active_tasks(repo: Path) -> list[str]:
    return [l.strip() for l in read(repo / "tasks" / "active.md").splitlines() if l.strip().startswith("- ")]


def pending_lines(repo: Path) -> list[str]:
    return [l for l in read(repo / "meta" / "pending.md").splitlines() if l.startswith("- ")]


# ---------- commands ----------

def cmd_locate() -> int:
    repo = locate()
    if not repo:
        return 1
    print(repo)
    return 0


def cmd_now() -> int:
    now = dt.datetime.now().astimezone()
    print(f"{now:%Y-%m-%d} {now:%H:%M} ({now:%a}, {now.tzname()})")
    return 0


def cmd_status() -> int:
    repo = require_repo()
    print(f"home repo: {repo}")

    tasks = active_tasks(repo)
    print(f"active tasks: {len(tasks)}")
    for t in tasks:
        print(f"  {t}")

    pend = pending_lines(repo)
    if pend:
        print(f"pending unjournaled sessions: {len(pend)} (see meta/pending.md)")

    porcelain = git(repo, "status", "--porcelain").splitlines()
    if porcelain:
        last = git(repo, "log", "-1", "--format=%cd", "--date=short").strip() or "never"
        print(f"uncommitted changes: {len(porcelain)} files (last commit {last})")
        stray = [l[3:].strip('"') for l in porcelain
                 if l.startswith("?? ") and "/" not in l[3:] and not l[3:].strip('"').endswith(".md")]
        if stray:
            print(f"stray untracked files in repo root (tool output?): {', '.join(stray)}")

    mf = map_file(repo) or repo / "CLAUDE.md"
    cm = count_lines(read(mf))
    flag = "  << over budget" if cm > CLAUDE_MD_BUDGET else ""
    print(f"{mf.name}: {cm}/{CLAUDE_MD_BUDGET} lines{flag}")

    journals = sorted((repo / "journal").glob("*.md"))
    print(f"latest journal: {journals[-1].stem if journals else 'none'}")

    suspicious = []
    for p in list(repo.glob("*.md")) + list((repo / "tasks").glob("*.md")) + list((repo / "references").glob("*.md")):
        non_blank = [l for l in read(p).splitlines() if l.strip()]
        if len(non_blank) <= 1 and p.name not in ("inbox.md",):
            suspicious.append(p.relative_to(repo).as_posix())
    if suspicious:
        print("possibly emptied files: " + ", ".join(suspicious))
    return 0


def cmd_check_commit() -> int:
    repo = require_repo()
    if not is_git_repo(repo):
        print(f"check-commit: {repo} is not a git repository; nothing to check")
        return 1
    findings: list[str] = []
    has_head = git(repo, "rev-parse", "--verify", "HEAD").strip() != ""

    # -z: paths come unquoted (non-ASCII names stay usable). -M30%: a moved file that lost most of its
    # lines still shows as a rename (at git's default 50% it would show as a plain deletion).
    # Entries are status\0path\0, or status\0old\0new\0 for renames/copies.
    tokens = git(repo, "diff", "--cached", "--name-status", "-z", "-M30%").split("\0")
    i = 0
    while i < len(tokens) and tokens[i]:
        status = tokens[i]
        if status[0] in "RC":
            old, path = tokens[i + 1], tokens[i + 2]
            i += 3
        else:
            old = path = tokens[i + 1]
            i += 2
        label = path if old == path else f"{old} -> {path} ({'renamed' if status[0] == 'R' else 'copied'})"
        if status[0] == "D":
            findings.append(f"DELETED: {path}")
            continue
        if status[0] in "MRC" and has_head:
            before = count_lines(git(repo, "show", f"HEAD:{old}"))
            after_text = git(repo, "show", f":{path}")
            after = count_lines(after_text)
            if before >= 3 and len([l for l in after_text.splitlines() if l.strip()]) <= 1:
                findings.append(f"EMPTIED: {label} ({before} -> {after} lines)")
            elif before >= 10 and after < before / 2:
                findings.append(f"SHRANK: {label} ({before} -> {after} lines)")

    for line in git(repo, "diff", "--cached", "-U0").splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            for rx, label in SECRET_PATTERNS:
                if rx.search(line):
                    findings.append(f"POSSIBLE SECRET ({label}): {line[1:80].strip()}...")
                    break

    if findings:
        print("check-commit found problems; do not commit until the user confirms:")
        for f in findings:
            print(f"  - {f}")
        return 2
    print("check-commit: ok")
    return 0


# ---------- lessons ----------

LESSON_META = re.compile(r"\((?P<meta>[^()]*\b(?:seen|repo|last|from)\s*:[^()]*)\)\s*$")
STALE_DAYS = 90
PROMOTE_AT = 3
MAX_RECALL = 5


def parse_lessons(repo: Path) -> list[dict]:
    """Parse references/lessons.md into dicts: text, area, repo(list), seen, last, from, promoted, line, raw."""
    out, area = [], ""
    for i, raw in enumerate(read(repo / "references" / "lessons.md").splitlines(), 1):
        if raw.startswith("## "):
            area = raw[3:].strip()
            continue
        if not raw.startswith("- "):
            continue
        out.append({**parse_lesson_line(raw), "area": area, "line": i, "raw": raw})
    return out


def parse_lesson_line(raw: str) -> dict:
    """One "- text (meta)" lesson line: text, repo(list), seen, last, from, promoted, demoted, cost."""
    m = LESSON_META.search(raw)
    item = {"text": raw[2:m.start() if m else None].strip(), "repo": [], "seen": None, "last": None,
            "from": None, "promoted": None, "demoted": None, "cost": None}
    if m:
        # fields are split by ";" (or by "," when a "key:" follows, so "repo: a, b" stays whole)
        for part in re.split(r";|,(?=\s*[\w-]+\s*:)", m.group("meta")):
            if ":" not in part:
                continue
            k, v = (s.strip() for s in part.split(":", 1))
            k = k.lower()
            if k == "repo":
                item["repo"] = [r.strip().lower() for r in v.split(",") if r.strip()]
            elif k == "seen":
                n = re.match(r"\d+", v)  # leading number only: "3/5" is 3, not 35
                item["seen"] = int(n.group()) if n else 0
            elif k in ("last", "from", "promoted", "demoted", "cost"):
                item[k] = v
    return item


def current_repo_name(cwd: Path) -> str | None:
    top = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    if top.returncode == 0 and top.stdout.strip():
        return Path(top.stdout.strip()).name.lower()
    return None


def lessons_for(repo: Path, cwd: Path) -> list[dict]:
    """Lessons tagged for the current repo, then lessons tagged `*` (anywhere).

    Repo lessons: most-reinforced, then most recent. `*` lessons follow: those whose area matches
    an area of the repo's own lessons first, then high-cost ones, then most-reinforced."""
    name = current_repo_name(cwd)
    parts = {p.lower() for p in cwd.parts}
    hits, anywhere = [], []
    for l in parse_lessons(repo):
        tags = [t for t in l["repo"] if t != "*"]
        if (name and name in tags) or (parts & set(tags)):
            hits.append(l)
        elif "*" in l["repo"]:
            anywhere.append(l)
    hits.sort(key=lambda l: (l["seen"] or 0, l["last"] or ""), reverse=True)
    areas = {l["area"] for l in hits}
    anywhere.sort(key=lambda l: (l["area"] in areas, (l["cost"] or "").lower().startswith("high"),
                                 l["seen"] or 0, l["last"] or ""), reverse=True)
    return hits + anywhere


def _days_since(date: str | None) -> int | None:
    try:
        return (dt.date.today() - dt.date.fromisoformat((date or "")[:10])).days
    except ValueError:
        return None


def cmd_lessons(args: list[str]) -> int:
    repo = require_repo()
    items = parse_lessons(repo)
    mode = args[0] if args else "--all"

    def show(l):
        meta = (f"seen {l['seen']}, last {l['last']}, repo {','.join(l['repo']) or '-'}"
                + (f", cost {l['cost']}" if l["cost"] else "")) if l["seen"] is not None else "no metadata"
        print(f"  L{l['line']} [{l['area']}] {l['text'][:140]}  ({meta})")

    if mode == "--find":
        words = [w.lower() for w in " ".join(args[1:]).split() if len(w) > 2]
        scored = [(sum(w in l["text"].lower() for w in words), l) for l in items]
        scored = [s for s in scored if s[0] > 0]
        scored.sort(key=lambda s: -s[0])
        print(f"{len(scored)} possible match(es):" if scored else "no similar lesson; add a new one")
        for _, l in scored[:5]:
            show(l)
    elif mode == "--repo":
        cwd = Path(args[1]) if len(args) > 1 else Path.cwd()
        hits = lessons_for(repo, cwd)
        print(f"{len(hits)} lesson(s) for {current_repo_name(cwd) or cwd.name}:")
        for l in hits:
            show(l)
    elif mode == "--promote":
        c = [l for l in items if not l["promoted"] and
             ((l["seen"] or 0) >= PROMOTE_AT or (l["cost"] or "").lower().startswith("high"))]
        print(f"{len(c)} promotion candidate(s) (seen >= {PROMOTE_AT} or cost: high, not yet promoted):")
        for l in c:
            show(l)
    elif mode == "--demote":
        c = [l for l in items if l["promoted"] and not l["demoted"] and (_days_since(l["last"]) or 0) >= STALE_DAYS]
        print(f"{len(c)} demotion candidate(s) (promoted, not needed for {STALE_DAYS}+ days):")
        for l in c:
            show(l)
            print(f"      promoted: {l['promoted']}")
    elif mode == "--stale":
        c = [l for l in items if (l["seen"] or 0) <= 1 and not l["promoted"] and (_days_since(l["last"]) or 0) >= STALE_DAYS]
        print(f"{len(c)} stale lesson(s) (seen once, untouched {STALE_DAYS}+ days):")
        for l in c:
            show(l)
    elif mode == "--lint":
        c = [l for l in items if l["seen"] is None or not l["repo"] or not l["last"]]
        print(f"{len(c)} lesson(s) missing metadata (repo/seen/last):")
        for l in c:
            show(l)
    else:
        print(f"{len(items)} lesson(s)")
        for l in items:
            show(l)
    return 0


# ---------- usage (reads, not writes) ----------

READ_TOOLS = {"Read", "Grep", "Glob", "NotebookRead"}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}
# Repo-relative files named in a shell command, and signs that the command writes rather than reads.
SHELL_FILE = re.compile(r"(?<![\w.-])((?:tasks|journal|references|meta)/[\w./-]+?\.md|CLAUDE\.md|inbox\.md|GUIDE\.md)\b")
JOURNAL_FILE = re.compile(r"journal/(\d{4}-\d{2}-\d{2})\.md")
TIMESTAMP = re.compile(r'"timestamp"\s*:\s*"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})[^"]*?(Z|[+-]\d{2}:\d{2})?"')
SHELL_WRITE = re.compile(r"(?<![<2&])>{1,2}(?!&)|\btee\b|\bsed\s+-i|\b(?:mv|rm|cp)\s|Set-Content|Add-Content|Out-File|Remove-Item|Move-Item")


def _norm(p: str) -> str:
    """Lowercase, forward slashes, runs of slashes collapsed (JSON-escaped backslashes, UNC paths)."""
    return re.sub(r"/+", "/", p.replace("\\", "/")).rstrip("/").lower()


def _tool_uses(obj):
    """Yield (name, input) for every tool_use block in a transcript record."""
    msg = obj.get("message") if isinstance(obj, dict) else None
    content = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                yield block.get("name", ""), block.get("input") or {}


def _tool_target(name: str, inp: dict) -> tuple[str, bool] | None:
    """(what a tool call acts on, whether it writes): the command for shell tools, else the file path."""
    if name in SHELL_TOOLS:
        cmd = str(inp.get("command") or "")
        return cmd, bool(SHELL_WRITE.search(cmd))
    path = inp.get("file_path") or inp.get("path") or inp.get("notebook_path")
    return (str(path), name in WRITE_TOOLS) if path else None


def lesson_changes(log: str) -> tuple[int, int, int, int]:
    """Count (new, reinforced, promoted, demoted) lesson changes in `git log -p` output.

    Each added lesson line is paired with the line it replaced in the same hunk (same text first,
    then in order, which covers rewording), and only fields that changed are counted."""
    new = reinforced = promoted = demoted = 0
    hunks, cur = [], ([], [])
    for line in log.splitlines() + ["@@"]:
        if line.startswith(("@@", "diff --git")):
            if cur[0] or cur[1]:
                hunks.append(cur)
            cur = ([], [])
        elif line.startswith("-- "):
            cur[0].append(parse_lesson_line(line[1:]))
        elif line.startswith("+- "):
            cur[1].append(parse_lesson_line(line[1:]))
    for removed, added in hunks:
        pairs, left = [], []
        for a in added:
            match = next((r for r in removed if r["text"].lower() == a["text"].lower()), None)
            if match:
                removed.remove(match)
                pairs.append((match, a))
            else:
                left.append(a)
        pairs += zip(removed, left)
        new += max(0, len(left) - len(removed))
        for old, a in pairs:
            reinforced += (a["seen"] or 0) > (old["seen"] or 0)
            promoted += a["promoted"] is not None and old["promoted"] is None  # "promoted:" with no value counts
            demoted += a["demoted"] is not None and old["demoted"] is None
    return new, reinforced, promoted, demoted


def cmd_usage(args: list[str]) -> int:
    repo = require_repo()
    days = int(args[0]) if args and args[0].isdigit() else 30
    since = dt.datetime.now().timestamp() - days * 86400
    base = _norm(str(repo))
    root = base + "/"
    # the whole repo path, not a sibling folder such as home-repo-workspace
    whole_base = re.compile(re.escape(base) + r"(?![\w.-])")
    name_hint = re.compile(re.escape(repo.name), re.I).search  # no-copy gate before normalizing a line

    def mentions_repo(text: str) -> bool:
        return bool(name_hint(text)) and bool(whole_base.search(_norm(text)))

    reads: dict[str, set] = {}
    writes: dict[str, int] = {}
    sessions_total = sessions_touching = 0

    projects = Path.home() / ".claude" / "projects"
    for t in projects.rglob("*.jsonl") if projects.is_dir() else []:
        try:
            if t.stat().st_mtime < since:
                continue
        except OSError:
            continue
        sessions_total += 1
        touched = False
        for line in read(t).splitlines():
            if not mentions_repo(line):
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            for name, inp in _tool_uses(obj):
                target = _tool_target(name, inp)
                if not target:
                    continue
                what, is_write = target
                if name in SHELL_TOOLS:
                    if not mentions_repo(what):
                        continue
                    rels = {m.lower() for m in SHELL_FILE.findall(what.replace("\\", "/"))}
                else:
                    n = _norm(what)
                    if not (n == base or n.startswith(root)):
                        continue
                    rels = {n[len(root):] or "."} if is_write or name in READ_TOOLS else set()
                touched = True
                for rel in rels:
                    if is_write:
                        writes[rel] = writes.get(rel, 0) + 1
                    else:
                        reads.setdefault(rel, set()).add(t.stem)
        sessions_touching += touched

    print(f"window: last {days} days; transcripts scanned: {sessions_total}; touching home repo: {sessions_touching}")
    files = sorted({*reads, *writes}, key=lambda f: (-len(reads.get(f, ())), f))
    print(f"{'file':55} {'read in N sessions':>18} {'writes':>7}")
    for f in files:
        print(f"{f[:55]:55} {len(reads.get(f, ())):>18} {writes.get(f, 0):>7}")

    tracked = [p.relative_to(repo).as_posix().lower() for p in repo.rglob("*.md")
               if ".git" not in p.parts and "archive" not in p.parts]
    never = [f for f in tracked if f not in reads]
    if never:
        print(f"never read in window ({len(never)}): " + ", ".join(sorted(never)))

    log = git(repo, "log", f"--since={days}.days", "-p", "--format=", "--", "references/lessons.md")
    new, reinforced, promoted, demoted = lesson_changes(log)
    if is_git_repo(repo):
        print(f"lessons in window: {new} new, {reinforced} reinforced, {promoted} promoted, {demoted} demoted (from git history)")
    else:
        print("lessons in window: unknown (home repo is not a git repository)")
    return 0


def cmd_journal_expire(args: list[str]) -> int:
    repo = require_repo()
    weeks = int(args[0]) if args and args[0].isdigit() else 6
    cutoff = dt.date.today() - dt.timedelta(weeks=weeks)
    live = {p.stem.lower() for p in (repo / "tasks").glob("*.md")} - {"active", "backlog"}
    # an open task named anywhere in a file (heading or bullet), as a whole word
    named = re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, sorted(live, key=len, reverse=True))) + r")(?![\w-])") if live else None
    expirable, kept = [], []
    for j in sorted((repo / "journal").glob("*.md")):
        try:
            day = dt.date.fromisoformat(j.stem)
        except ValueError:
            continue
        if day >= cutoff:
            continue
        still_open = sorted(set(named.findall(read(j).lower()))) if named else []
        (kept if still_open else expirable).append((j.relative_to(repo).as_posix(), still_open))
    print(f"journal files older than {weeks} weeks: {len(expirable) + len(kept)}")
    for f, _ in expirable:
        print(f"  expirable: {f}")
    for f, open_tasks in kept:
        print(f"  keep (open tasks: {', '.join(open_tasks)}): {f}")
    return 0


def _hook_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}


def cmd_hook_session_start() -> int:
    repo = locate()
    if not repo:
        return 0
    data = _hook_input()
    cwd = Path(data.get("cwd") or os.getcwd())
    lines = [f"[home-repo] Personal context repo: {repo}. Use the home-repo skill for day/session/task routines."]

    # Does this directory belong to a task? Match whole cwd path components against task names
    # and "Repos:" lines (a substring test would match task "api" in /work/orders-api).
    hits = []
    cwd_parts = {p.lower() for p in cwd.parts}
    for tf in (repo / "tasks").glob("*.md"):
        if tf.name in ("active.md", "backlog.md"):
            continue
        head = "\n".join(read(tf).splitlines()[:4]).lower()
        names = {tf.stem.lower()}
        m = re.search(r"repos:\s*([^\n(|]+)", head)
        if m:
            names |= {n.strip(" `").lower() for n in m.group(1).split(",") if n.strip()}
        if names & cwd_parts:
            hits.append(tf.relative_to(repo).as_posix())
    if hits:
        lines.append(f"[home-repo] This directory looks related to: {', '.join(hits[:3])}. Read it before starting work.")

    recalled = lessons_for(repo, cwd)
    if recalled:
        lines.append(f"[home-repo] Lessons for this repo (references/lessons.md; reinforce any that help):")
        for l in recalled[:MAX_RECALL]:
            lines.append(f"  - {l['text'][:180]}")
        if len(recalled) > MAX_RECALL:
            lines.append(f"  … {len(recalled) - MAX_RECALL} more: home_repo.py lessons --repo")

    pend = pending_lines(repo)
    if pend:
        lines.append(f"[home-repo] {len(pend)} earlier session(s) ended without a journal entry; offer to catch up at a natural pause.")
    print("\n".join(lines))
    return 0


def cmd_hook_session_end() -> int:
    repo = locate()
    if not repo:
        return 0
    data = _hook_input()
    transcript = data.get("transcript_path") or ""
    cwd = data.get("cwd") or ""
    if cwd and Path(cwd).resolve() == repo:
        return 0  # sessions maintaining the repo itself journal in-line
    try:
        lines = open(transcript, encoding="utf-8", errors="replace") if transcript else []
    except OSError:
        lines = []

    user_turns = 0  # prompts the user typed; tool results are also "user" records, so don't count those
    stamps: set[tuple[str, str]] = set()  # (minute, offset) of every record: the dates the session spanned
    journal_writes: set[str] = set()  # dates of journal files the session wrote
    for l in lines:  # one pass, one line in memory at a time
        m = TIMESTAMP.search(l)
        if m:
            stamps.add(m.groups(""))
        # only typed prompts and journal-related tool calls need parsing; tool results are the bulk
        if not ('"user"' in l and '"tool_result"' not in l) and not ('"tool_use"' in l and "journal" in l):
            continue
        try:
            obj = json.loads(l)
        except ValueError:
            continue
        user_turns += sum(1 for _ in _user_texts(obj))
        for name, inp in _tool_uses(obj):
            target = _tool_target(name, inp)
            if target and target[1]:  # reading today's journal is not writing one
                journal_writes |= set(JOURNAL_FILE.findall(target[0].replace("\\", "/")))
    if hasattr(lines, "close"):
        lines.close()
    days = {dt.date.today().isoformat()}
    for minute, tz in stamps:  # to the minute: enough for the local date
        try:
            ts = dt.datetime.fromisoformat(minute + ("+00:00" if tz == "Z" else tz))
            days.add(ts.astimezone().date().isoformat())  # no offset: taken as local time
        except ValueError:
            pass
    if user_turns < 3:
        return 0  # trivial session; not worth journaling
    if journal_writes & days:
        return 0  # the session already wrote a journal entry

    now = dt.datetime.now()
    entry = f"- {now:%Y-%m-%d %H:%M} | cwd {cwd} | transcript {transcript}\n"
    pend = repo / "meta" / "pending.md"
    pend.parent.mkdir(parents=True, exist_ok=True)
    if not pend.exists():
        pend.write_text("# Pending sessions (ended without a journal entry)\n\n", encoding="utf-8")
    with pend.open("a", encoding="utf-8") as f:
        f.write(entry)
    return 0


RULE_PATTERNS = re.compile(
    r"(?i)\b(from now on|going forward|in (the )?future|every time|whenever"
    r"|without (my|me|asking|your asking)|unless i (say|ask|approve)"
    r"|(never|always) [a-z]+"
    r"|(don'?t|do not) (ever|again)"
    r"|no (auto(matic)?|more) [a-z]+"
    r"|remember (that|to)"
    r"|stop [a-z]+ing)\b")


def _user_texts(obj):
    """Yield text the user typed (not tool results, commands, or injected context)."""
    if not isinstance(obj, dict) or obj.get("type") != "user":
        return
    if obj.get("isMeta") or obj.get("isSidechain") or obj.get("isCompactSummary"):
        return
    content = (obj.get("message") or {}).get("content")
    blocks = [content] if isinstance(content, str) else [
        b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text"]
    for text in blocks:
        if text and not text.lstrip().startswith("<") and not text.startswith("This session is being continued"):
            yield text


def cmd_rules(args: list[str]) -> int:
    """Standing rules the user stated in recent sessions: candidates to capture, not facts."""
    days = int(args[0]) if args and args[0].isdigit() else 14
    since = dt.datetime.now().timestamp() - days * 86400
    projects = Path.home() / ".claude" / "projects"
    seen: set[str] = set()
    found = []
    for t in projects.rglob("*.jsonl") if projects.is_dir() else []:
        try:
            if t.stat().st_mtime < since:
                continue
        except OSError:
            continue
        for line in read(t).splitlines():
            if '"user"' not in line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            for text in _user_texts(obj):
                for sent in re.split(r"(?<=[.!?])\s+|\n+", text):
                    sent = " ".join(sent.split())
                    if 8 <= len(sent) <= 300 and RULE_PATTERNS.search(sent) and sent.lower() not in seen:
                        seen.add(sent.lower())
                        where = Path(str(obj.get("cwd") or "")).name or "?"
                        found.append((str(obj.get("timestamp", ""))[:10], where, sent[:200]))
    found.sort()
    for day, where, sent in found[-60:]:
        print(f"{day}  [{where}]  {sent}")
    print(f"{len(found)} candidate(s) in the last {days} days. Heuristic: confirm each with the user before saving.",
          file=sys.stderr)
    return 0


COMMANDS = {
    "locate": cmd_locate,
    "now": cmd_now,
    "status": cmd_status,
    "check-commit": cmd_check_commit,
    "hook-session-start": cmd_hook_session_start,
    "hook-session-end": cmd_hook_session_end,
}

if __name__ == "__main__":
    ARG_COMMANDS = {"lessons": cmd_lessons, "usage": cmd_usage, "journal-expire": cmd_journal_expire,
                    "rules": cmd_rules}
    if len(sys.argv) >= 2 and sys.argv[1] in ARG_COMMANDS:
        sys.exit(ARG_COMMANDS[sys.argv[1]](sys.argv[2:]))
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(64)
    try:
        sys.exit(COMMANDS[sys.argv[1]]())
    except Exception as e:  # hooks must never break a session
        if sys.argv[1].startswith("hook-"):
            sys.exit(0)
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
