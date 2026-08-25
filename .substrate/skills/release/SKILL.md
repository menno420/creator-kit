---
name: release
description: "Cut + publish a substrate-kit release — version bump PR, workflow_dispatch publish, three-way asset verification, adopter distribution wave."
---

# release

Cut and publish a substrate-kit release — the kit cut runbook, executable
(canonical prose: `docs/operations/release-runbook.md`). Kit-repo-specific
by nature: the commands below run in the kit repo, the source of the
releases creator-kit consumes.

## What this does

Takes `CHANGELOG.md` `[Unreleased]` to a published GitHub Release with
byte-verified assets: version bump PR (born-red), workflow_dispatch publish,
three-way post-release verification, then adopter notification via
distribution PRs.

## Instructions

1. Preconditions — every shipped PR has its entry under `[Unreleased]` in
   `CHANGELOG.md`; decide the semver class (MAJOR = planted-doc / state /
   config / CLI break · MINOR = new capability · PATCH = fixes).
2. Claim, then bump PR born-red — claim `control/claims/` (one file, e.g.
   release-vX.Y.Z.md) on main first; cut the bump branch from post-claim
   main; born-red card as first commit; open the PR READY; land it on green
   (merge directly or via the enabler).
3. Version bump, one commit set — BOTH version homes in the SAME commit:
   `src/engine/lib/config.py` (`KIT_VERSION`) and `pyproject.toml`
   (`version`). CHANGELOG: rename `[Unreleased]` to the new `[X.Y.Z]`
   dated section, add a fresh empty `[Unreleased]` above it, and keep the
   machine comment (breaking / state_migration / min_upgrade_from)
   accurate — the release workflow refuses a version with no CHANGELOG
   section.
4. Dist regen + byte-pin — `python3 src/build_bootstrap.py`, then
   `git diff --exit-code dist/bootstrap.py` must be clean; commit the
   regenerated dist (CI rebuilds and byte-compares).
5. Verify locally, then flip — `python3 -m pytest tests/ -q` green ·
   `python3 -m ruff check src/engine/` clean ·
   `python3 src/build_release_json.py --version X.Y.Z --verify-only`
   reports preconditions green ·
   `python3 dist/bootstrap.py check --strict` (only acceptable red = own
   card's designed hold). Flip the card `complete` as the last commit; the
   server-side enabler merges on green.
6. Publish — dispatch the release workflow on main at the bump-merge SHA:
   `gh workflow run release.yml -f version=X.Y.Z`. The run creates the
   annotated tag `vX.Y.Z` in-Actions and publishes the Release with three
   assets: `bootstrap.py`, `bootstrap.py.sha256`, `release.json`.
7. Post-release verification (never skip) — the tag exists:
   `git fetch --tags && git tag -l vX.Y.Z`; the assets are published:
   `gh release view vX.Y.Z`; independently download the released
   `bootstrap.py` and its sha256 must equal BOTH the `sha256` field in
   `release.json` AND the committed `dist/bootstrap.py` at the bump SHA
   (three-way, byte-identical). Record run id, tag, commit SHA, and hash
   in the release record.
8. Aftermath — adopter notification via distribution PRs: run the
   `upgrade-distribution` skill per adopter (one born-red PR each);
   registry regen `python3 dist/bootstrap.py currency` refreshes
   `docs/adopters.md`; write the `control/status.md` release record;
   delete the claim.

## Report format (release record)

`vX.Y.Z · bump PR #<n> merged @ <sha> · release run <id> · tag vX.Y.Z @ <sha> · sha256 <hash> (3-way ✔) · adopters: <one outcome line per repo>`

Known failure modes + fixes:

- Tag pushes can 403 where branch pushes work — the workflow_dispatch path
  creates the tag in-Actions; never hand-push a tag first.
- The workflow refuses when `KIT_VERSION` / dist header / CHANGELOG
  disagree — fix the version homes, never the guard.
- Published releases are never deleted — supersede a bad cut with a fixed
  one whose `release.json` carries the yank note.

Declared capabilities: edit (version homes + CHANGELOG + docs), run (build +
git + gh).
