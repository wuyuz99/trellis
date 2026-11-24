# Commit

Every commit to the home repo goes through this, including the commits other routines make. In past use, a bulk commit silently emptied a planning file.

1. `git -C <home-repo> add -A`
2. Run `python3 <skill-dir>/scripts/home_repo.py check-commit`. It looks at the staged diff for:
   - files deleted, or reduced to zero or near-zero lines
   - files that lost more than half their lines
   - likely secrets (keys, tokens, private keys, passwords in assignments)
3. If it reports anything, **stop**, show the findings, and ask. Don't commit "to fix later".
   - **Deletions the user already approved** in this session (e.g. journal files they agreed to expire during a review) are expected. Don't ask about them a second time; commit them in their own commit with a message that says what was removed and why (`review: expire journals 2026-09-02 (task closed, digest in archive)`). Ask only about findings that weren't part of what they approved.
   - If some files pass and one doesn't, you can unstage the flagged file (`git restore --staged <file>`), re-run the check, and commit the rest. Say clearly what was held back.
4. **If git has no author identity** (the commit fails with "Please tell me who you are"), don't change the user's git config. Ask the user for a name and email to set in *this repo only* (`git -C <home-repo> config user.name …`). If they're unavailable, reuse the author of the repo's existing commits for this one commit with `git -c user.name=… -c user.email=…`, and say so.
5. Commit message: `<routine>: <summary>`, e.g. `close: export-timeout, flaky-ci`, or `day: 2026-11-24 journal + lessons`.
6. Push only if a remote exists **and** the user has said pushing is fine (record that in the repo's `CLAUDE.md`). Never create a public remote.
