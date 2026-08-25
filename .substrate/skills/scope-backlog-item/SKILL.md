---
name: scope-backlog-item
description: "Turn a raw backlog item into a turnkey recipe or an owner ask — chase its origin, state the fuller picture, classify buildable/owner-gated/dead, write the sized recipe with acceptance + traps, and retarget the baton. Makes the standing 'when no executable work is left, plan' order turnkey."
---

# scope-backlog-item

When the executable backlog is empty and the standing order is "when no
executable work is left, plan," this skill turns a raw backlog item into a turnkey recipe the next
session can build cold without re-deriving anything. It is the planning counterpart to `intake`:
`intake` reasons a fresh owner ask forward; this reasons an existing backlog item forward into a
buildable slice — chase its origin, state the fuller picture, classify it, and write the recipe or
the owner ask.

## What this does

Takes one backlog item (an ideas file, a friction flag on a session card, a baton entry, a routed
order) and produces exactly one of:
- a sized, turnkey recipe a session can pick up cold and build to green,
- a six-field owner ask (WHAT / WHERE / HOW / WHY / UNBLOCKS / VERIFY, plus RISK) when the item is
  owner-gated,
- a dead / superseded disposition with the reason, or
- a needs-planning split into a smallest-buildable first slice plus the remainder.

Then it retargets the baton so the next session lands on the freshly-scoped slice.

## Invocation

`/scope-backlog-item <the item — a path, a baton entry, or a one-line description>`

## Instructions

1. CHASE THE ORIGIN. Follow every reference the item names to its source — the session card that
   raised it, the ideas file, the friction flag, the order — and read them at HEAD, not from memory.
   The origin holds the real constraint the one-line item compresses away; scoping without it
   reproduces the near-miss the item came from. If the item names no origin, say so and scope from
   the text you have.

2. STATE THE FULLER PICTURE (understand-and-reflect). In two or three sentences, reason the item
   forward to the fuller shape its origin implies — the surrounding constraints, the likely intended
   scope, the follow-on it points at. A wrong assumption stated here costs one line to correct; the
   same assumption found after an hour of building costs the hour.

3. CLASSIFY into exactly one bucket:
   - buildable-now — contained, reversible, test-coverable in one session; go to step 4.
   - needs-planning — real but too big for one slice; split into the smallest buildable first slice
     plus the remainder, and scope the first slice through step 4.
   - owner-gated — irreversible / external / product-intent / console-or-secret; write it as a
     six-field owner ask (WHAT / WHERE / HOW / WHY / UNBLOCKS / VERIFY, RISK marker, paste-ready) and
     stop — do not build.
   - dead — superseded, already shipped, or wrong; record the disposition plus a one-line reason.

4. WRITE THE RECIPE so a cold session needs nothing else:
   - Size — S / M / L against a single session.
   - Steps — the ordered build path (files to touch, the seam, the guard).
   - Acceptance — the exact command(s) that prove it green (the repo's verify line plus any gate).
   - Traps — the specific footguns this item will hit. Always check these three, which bite every
     new-doc recipe:
     - badge token — a new doc placed under `docs/` needs a Status badge in its first 12 lines, and
       the token must come from the docs-gate's allowed set (binding, reference, plan, historical,
       ideas, audit, owner-guidance, living-ledger, archive); an invented token reds the gate.
     - reachability — a new doc must be reachable by a markdown link from a read-path root
       (`docs/AGENT_ORIENTATION.md` or `docs/current-state.md`, or a README they reach) or it fails
       the reachable leg, unless it is badged historical or archive.
     - docs-gate — run the kit gate before pushing; it catches both of the above plus dead links.

5. RETARGET THE BATON. Update the coordinator's Next-2 baton in `control/status.md` so the next
   session's first slice is this freshly-scoped item, naming the recipe (or its planning-doc path).
   Leave the baton pointing at real, cold-startable work — that is the whole output.

## Report format

Report the item, its origin trail, the fuller picture, the classification with reason, and the
recipe or owner ask verbatim, plus the baton line you wrote.

Declared capabilities: read (the origin refs, the backlog, the docs-gate rules).
