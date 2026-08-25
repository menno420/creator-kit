# `control/claims/` — claim before build, one file per claim

> **Status:** `binding`
>
> Local copy for creator-kit. The kit-owned work-claim convention
> (EAP program review 2026-07-10 §6.4 — the fleet's forked claim mechanisms
> unified on the measured winner). Order claims are different and stay on
> your heartbeat — see `control/README.md` § "Claiming an order".

## What this is

A lightweight **claim ledger** so parallel agent sessions don't duplicate each
other's work. Several sessions can run at once; two of them picking up the
same task is pure waste. This directory makes "is someone already on this?"
answerable **before a PR exists** — the claim is the early in-flight signal,
the PR is the late one.

## Why one file per claim (measured, not vibes)

A shared "active work" list that every session appends to and prunes is a
merge-conflict machine: a real-`git merge` simulation
(menno420/superbot `tools/sim/claim_layout_sim.py`) measured the shared-append
pattern at a **~98% conflict rate** under concurrent sessions; splitting by
sector only halved it. **One file per claim is structurally conflict-free —
0% at every concurrency level** — because two sessions never touch the same
file. The rule that preserves that 0%: **no hand-edited shared index**.
Discover claims with `ls control/claims/` — this README never lists them.

## How to use it

1. **Before starting work**, scan this directory AND the open PRs. If your
   task is already claimed or in flight, coordinate or pick something else.
2. **Create one claim file** — `control/claims/<branch-or-scope>.md` — with a
   single bullet:
   `` - `branch-or-scope` · **scope** — one-line detail · expected files/area · YYYY-MM-DD ``
   (Keep the backticks around the branch/scope token and the ISO date — the
   `check_claims` checker parses both; an unparseable claim is invisible to
   its duplicate scan.)
   Grammar source of truth: the bullet's regexes (backticked token + ISO date) are kit-owned constants in the kit's `src/engine/grammar.py` (EAP §6.8) — the SAME module `check_claims` consumes; agreement is pinned by the kit's `tests/test_grammar.py`.
   **Don't hand-write it** — `bootstrap claim <slug> --scope "<scope>"
   [--area "<files/area>"] [--order NNN]` renders the bullet from those same
   constants (round-trip verified, current UTC date last; `--dry-run`
   previews), so the claim can never be invisible to the duplicate scan.
   **Serving an inbox ORDER? Pass `--order NNN`** — it renders the
   structured ` · order NNN` segment the cross-branch overlap scan keys on,
   and the verb REFUSES to write when another live claim on a different
   branch already names that order (two branches building one ORDER is the
   twin-execution waste this guard exists for; `--force` overrides for a
   deliberate split of one order across branches).
3. **Land the claim on main FAST** (claims are `control/**` traffic — they
   ride the CI control fast lane), then re-read this directory at HEAD before
   you build: if both lanes do this, the second claimer always sees the first.
4. **Delete your own claim file at session close** — `bootstrap claim
   <slug> --delete` (it refuses to touch a foreign claim). The durable
   record is the PR and the living ledger — a claim is a whiteboard note,
   not an audit trail.

## Arbitration + expiry

- **First claim merged to main wins** a collision — a deterministic tiebreak
  beats re-litigating every race; the loser deletes its file and stands down.
- **Claims expire**: a claim file older than ~72h with no visible build
  activity may be treated as abandoned — prune it on sight (the checker nags
  with `claims-stale`).

## What the checker enforces (all advisory, never exit-affecting)

`check` warns on: `claims-format` (no parseable bullet), `claims-stale`
(older than the ~72h horizon), `claims-duplicate` (two files, one
branch/scope token), `claims-order-collision` (two live claims on DIFFERENT
branches naming the same `order NNN` / free-text `ORDER NNN` on the bullet
— likely duplicate work; confirm one owner), and `claims-legacy-location`
(claims living in a
pre-unification home — `docs/owner/claims/` or root `claims/`; move them
here, or pin your deliberate location via `substrate.config.json` →
`claims_dir`).

## Not for inbox ORDERS

An inbox ORDER is claimed on your OWN heartbeat's `orders:` line
(`claimed-by: <ids> <lane> <ISO8601>` — `control/README.md` § "Claiming an
order"), never here: the heartbeat annotation preserves one-writer-per-file
for the order lifecycle the manager reconciles. This directory is for
**work** — coordinator-assigned slices, self-initiated builds, anything that
isn't an ORDER id.
