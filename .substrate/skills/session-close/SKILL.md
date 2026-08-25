---
name: session-close
description: "Land the session — claim, born-red card first, READY PR, batched work, close-out docs, flip complete last; land on green."
---

# session-close

Land creator-kit's session correctly — the full landing path, claim to
merged-on-green. Playbook-grade: a session reading this executes without
improvising (grounded-skills plan §7.2).

## What this does

Drives the session's work to a terminal, verified state on two rails:
the born-red gate (card first, flip last) and landing your own green PR
(merge it directly once required checks pass, or let the server-side
auto-merge-enabler land it — either is fine). Everything else is ordered
steps.

## Instructions

1. Claim first (session start — verify it happened) — one file per claim,
   `control/claims/<branch-or-scope>.md`, a single bullet: backticked
   branch/scope token · **scope** — one-line detail · expected files/area ·
   ISO date (the shape `check_claims` parses). Land the claim on main fast,
   then re-read `control/claims/` at HEAD before building.
2. Born-red card as the FIRST commit — `.sessions/<date>-<slug>.md` whose
   Status badge line declares `in-progress` (the born-red hold token), plus
   a one-line "what is about to happen". Push, then open the PR READY (not
   draft) immediately: the open PR + the claim are the in-flight signal
   parallel sessions collide without.
3. Land your own green PR — merging is normal agent work. Once the required
   checks are green, merge it directly (MCP/REST), or let the server-side
   auto-merge-enabler land it; either is fine. Only a `do-not-automerge`-
   labelled PR waits for the owner. Read a red on a born-red head as the
   designed hold, not a CI failure: verify any red against the job log
   before diagnosing — alias/mirror jobs echo the required check without
   running anything (kit repo example: the two legacy jobs mirroring
   `kit-quality`), and "HOLD (by design)" means nothing to investigate.
4. Batch the work — push when a batch is meaningfully complete, never every
   commit (superseded CI runs are the dominant Actions cost).
5. Close-out docs, into the SAME card: what shipped (paths + commits);
   Capability delta — new capability or wall discovered? Append it to
   `docs/CAPABILITIES.md` (dated, with its venue token, exact error or
   proof, workaround — below the seed fence, never inside it); every
   ⚑ needs-owner ask carries the OWNER-ACTION fields (WHAT / WHERE / HOW /
   WHY-IT-MATTERS / UNBLOCKS / VERIFIED-NEEDED — attempted, or the exact
   wall; see `control/README.md`) — Withdraw stale asks; groom one idea
   forward; add one new 💡 idea you genuinely believe in; write the ⟲
   previous-session review.
6. Verify — `${verify_command}` and `python3 bootstrap.py check --strict`;
   if those are the same command, also run the repo's other boot-file gates
   (the collision otherwise drops a gate silently).
   The only acceptable pre-flip red is the designed born-red hold naming
   this session's own card.
7. Flip as the deliberate LAST step — flip the card badge to `complete`,
   delete your own claim file, push. Green then merges server-side; a
   flipped-early card merges a partial PR (the failure the gate exists
   for), and an unpushed flip leaves the PR red forever.

## Report format (card close-out)

- Shipped: one line per artifact, with paths + commit SHAs.
- Verify: each command + its tail, verbatim.
- ⚑ decide-and-flag lines · 💡 session idea · ⟲ previous-session review.
- PR: #<n> + terminal state, probed against the tree/checks — not a stale
  PR read.

Declared capabilities: edit (the log + docs), run (the checks + git).
