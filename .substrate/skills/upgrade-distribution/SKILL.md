---
name: upgrade-distribution
description: "Roll a kit release out to one adopter repo — download, sha256 three-way, banked rollback, carve-out scan, born-red PR, tree-verified merge."
---

# upgrade-distribution

Roll a substrate-kit release out to creator-kit — one target repo of the
distribution wave. Playbook-grade wave runbook (grounded-skills plan §7.2).

## What this does

Moves the target's vendored `bootstrap.py` to the released version with the
sha256 three-way proof, the banked rollback path, a carve-out scan for local
modifications, and a born-red PR — then verifies MERGED MAIN against the
tree, never a registry line or a PR read.

## Instructions

1. Preflight — sync the clone before reading anything:
   `git fetch origin main && git reset --hard origin/main`. A stale clone
   reads stale orders and re-executes finished work.
2. Download the release next to the vendored copy:
   `gh release download vX.Y.Z --repo menno420/substrate-kit --pattern 'bootstrap.py*' --pattern 'release.json'`
   then move the downloaded dist to `bootstrap.py.new` (the consumer flow
   `release.json` names).
3. sha256 three-way compare (never skip) — `sha256sum bootstrap.py.new`
   must equal BOTH the `sha256` field in `release.json` AND the kit repo's
   committed `dist/bootstrap.py` at the release's bump SHA. Any mismatch:
   stop and report; do not upgrade.
4. Born-red PR first — claim file + `.sessions/` card declaring
   `in-progress` as the first commit on the wave branch; open the PR READY;
   land it on green — merge directly or via the enabler (the session-close
   rails apply verbatim).
5. Upgrade — `python3 bootstrap.py.new upgrade`. It banks the OLD dist to
   `.substrate/backup/` (verify the banked `bootstrap-<old-version>.py`
   exists — that is the rollback path) and consumes its own inputs.
6. Carve-out scan — read `.substrate/upgrade-report.md`: `consumer-edited`
   and `diverged` docs are LOCAL MODIFICATIONS the upgrade must not
   clobber; list them verbatim in the PR body. `template-improved` applies
   only under `--apply-docs` and only to consumer-untouched docs.
7. Verify + flip — `${verify_command}` and
   `python3 bootstrap.py check --strict` green
   — if those are the same command, run the repo's other boot-file gates too (own card's designed hold
   excepted); flip the card `complete`, delete the claim, push.
8. Verify merged main afterward — TREE over registries:
   `git fetch origin main && git log -1 --oneline origin/main` and read the
   vendored dist's version header at origin/main. Never trust an MCP PR
   read alone for merge/CI state (~25-min-stale data) — cross-check the
   tree or the Actions runs.

## Report format — one outcome line per target repo

`<repo>: vOLD → vNEW · sha256 3-way ✔ · bank ✔ · carve-outs: <n or none> · PR #<n> merged @ <sha> · tree-verified ✔`

Known failure modes + fixes:

- A `do-not-automerge` label applied seconds after MCP PR-create misses the
  opened-event label snapshot and reds the first CI round — cure with one
  empty commit (`git commit --allow-empty`) to re-fire the enabler.
- MCP PR reads can serve ~25-minute-stale merge/CI state — probe the tree,
  not the PR object.
- A born-red head red-pings "failed checks"; job-log truth is the designed
  hold plus alias jobs that mirror the required check — verify against the
  job log, don't chase.

Declared capabilities: edit (the vendored dist + docs), run (git + gh + the
checks).
