---
name: backport-failed
description: Recover from a patchback auto-backport failure. Given a merged PR number, parse the patchback comments to find which target branches failed, cherry-pick the merge commit onto each failed branch, resolve conflicts, push to the user's fork, and open backport PRs that exactly match patchback's title and body shape so they look indistinguishable from successful auto-backports.
user-invocable: true
allowed-tools:
  - Bash(git:*)
  - Bash(gh:*)
  - Read
  - Edit
  - AskUserQuestion
---

# /backport-failed — Manual recovery for failed patchback backports

When patchback (the auto-backport bot used by aio-libs) fails to cherry-pick a merged PR onto a stable branch, it leaves a comment with a heading like `### Backport to 3.13: 💔 cherry-picking failed — conflicts found` and the exact recovery steps (branch name, cherry-pick command, push target). This skill executes those steps and opens a PR whose shape is byte-identical to a successful patchback PR.

Arguments: `$ARGUMENTS` — the merged PR number. If empty, ask via `AskUserQuestion`.

## Procedure

1. **Read the patchback failure comments** to get the failed-branch list and the per-branch recovery recipe verbatim:

   ```bash
   gh pr view <num> --comments
   gh pr view <num> --json mergeCommit,title,body,labels,url
   ```

   Each `💔 cherry-picking failed` comment names the target branch and gives the recovery commands — follow them. Squash merges (the aio-libs default) use plain `git cherry-pick -x <sha>`; true merge commits (`git cat-file -p <sha>` shows >1 `parent`) use `git cherry-pick -m1 -x <sha>`.

2. **Skip target branches that already have a backport PR** (patchback may have succeeded since, or a human may have done it):

   ```bash
   gh pr list --search "[PR #<orig_num>/<short_sha> backport]" --state all
   ```

3. **Per failed branch (sequential — they share the working tree):** run the recovery steps from patchback's comment, resolve any conflicts, push to your fork, then open the PR using the shape below.

   News fragments (`CHANGES/*.rst`) usually don't exist on the stable branch — take the master version. If any other conflict can't be resolved confidently, stop and ask the user.

## Required PR shape

Patchback's comment doesn't specify the PR title/body it would have used, so apply this verbatim (canonical example: any `patchback[bot]`-authored PR, e.g. aio-libs/aiohttp#12574):

- **Title:** `[PR #<orig_num>/<short_sha> backport][<branch>] <original PR title>`
  - `<short_sha>` is the first 8 chars of the merge commit on master
- **Body first line:** `**This is a backport of PR #<orig_num> as merged into master (<full_sha>).**`
- **Body remainder:** the original PR body verbatim — do not strip HTML comments, do not edit the checklist, do not summarize
- **Base:** the stable branch (e.g. `3.13`)
- **Head on fork:** `patchback/backports/<branch>/<full_sha>/pr-<orig_num>`

**Do not** add a `Drafted with Claude Code` footer or a `Co-Authored-By` trailer. This is the one place in this repo where the [AGENTS.md](../../../AGENTS.md) disclosure rule does *not* apply — the PR must be byte-for-byte indistinguishable from a successful patchback PR.

## Output

One line per branch: the new PR URL, `skipped (already exists)`, or `paused for user (conflict in <file>)`.
