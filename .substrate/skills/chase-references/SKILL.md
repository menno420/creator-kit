---
name: chase-references
description: "Resolve every reference in the ask before acting — inventory, resolve or search each one, report unfindables explicitly, state the assembled picture back (Q-0273 seed skill)."
---

# chase-references

Resolve every reference in a creator-kit ask before acting on it.

> **Owner-directed (Q-0273, 2026-07-12).** Founding incident: the owner opened
> a session with a comprehensive message containing a direct link to the
> previous session's brief and multiple sibling repos by name — and the session
> still oriented on the local repo only, costing ~3 turns of re-discovery. The
> lesson graduates as an on-demand method (his words: "baked into a method,
> like a skill, that prevents it from taking up too much storage in the
> claude.md itself, but is still always loadable on demand"). superbot carries
> the founding copy; this is the kit's generalized template, inherited by
> every adopter.

## When this runs

At the start of ANY substantive ask — an opening message, an ORDER, a brief —
and again whenever a mid-task message introduces new references. Trigger
especially on: URLs · file paths · doc titles · repo names · PR/issue numbers ·
question-router IDs · "as discussed in / the plan says / the brief covers"
phrasings.

## The method

1. **Inventory first.** Before any substantive work, list every reference the
   ask contains or implies (explicit links, named files, named repos, named
   plans, "the X doc"). The ask's references ARE its context spec — the author
   included them because reading them is cheaper than re-deriving them.
2. **Resolve each one, in this order:**
   - a local path → read it;
   - a project doc named fuzzily → find it (glob/grep across the doc roots);
   - a **sibling repo or its file** → fetch it read-only via the repo's
     documented reading path / sibling registry, where one exists;
   - a PR/issue number → pull it from the forge (own repo) or from the
     sibling's committed heartbeat/pointer files;
   - a router question ID → grep `docs/question-router.md`.
3. **An unfound reference is a search task, never a skip.** Guess the
   most-logical homes and look there before proceeding: the planted doc set
   under `docs/` (orientation, current-state, plans, reports) → `.sessions/`
   (recent session records) → `docs/ideas/` → the named sibling's committed
   status and docs, where a sibling registry exists. If it is genuinely absent
   after that, SAY so explicitly ("the brief references X; I could not find it
   in A/B/C") — silent omission is how wrong pictures get built.
4. **State the assembled picture back** (the understand-and-reflect step —
   pair with the `intake` skill on owner asks): one short paragraph of what
   the references collectively establish, before the work starts. A wrong
   assumption corrected here costs one line; discovered later it costs the
   session.

## The bar

You are done chasing when every reference is either **read**, **fetched**, or
**explicitly reported unfindable with the places you looked**. "I'll read it
if it becomes relevant" fails the bar for anything the owner linked or named
directly — he already decided it was relevant.

Declared capabilities: read-only.
