# Small file formats

## tasks/active.md
```
# Active
- [<task>](<task>.md): <what>. <blocked on … / note>
```

## tasks/backlog.md
```
# Backlog
## <area>
- **<name>** [<high|med|low|parked>]: <what>. Where: <repo/branch>. <note>
```

## journal/YYYY-MM-DD.md (append-only)
```
# YYYY-MM-DD
## <task or misc> HH:MM
- <what happened / decided / blocked>
```

## references/lessons.md
```
# Lessons
## <area>
- <lesson, as an instruction>. (repo: <repo|*>; seen: 1; last: YYYY-MM-DD; from: <task>)
```

## Pointer / index reference
```
- <YYYY-MM-DD> **<what>**: <path or location>. <contents / why it matters / how to restore>
```

## inbox.md (fallback only)
```
- YYYY-MM-DD: <note>
```

## meta/pending.md (written by the SessionEnd hook)
```
- YYYY-MM-DD HH:MM | cwd <dir> | transcript <path>
```
