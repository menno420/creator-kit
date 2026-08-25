# Fleet coordination protocol — `control/`

> **Status:** `binding`
>
> Local copy for creator-kit. Canonical spec: `menno420/superbot` →
> `docs/planning/fleet-coordination-protocol-2026-07-09.md` (§1). Projects cannot talk to each
> other directly — committed git files are the only shared medium; this directory is the bus.

## The two files

- `control/inbox.md` — ORDERS to this Project. **One writer: the manager** (appends via the
  GitHub Contents API). Never edit this file.
- `control/status.md` — STATE from this Project. **One writer: this Project** (overwrite it each
  session).

## The one rule that keeps it conflict-free

**One writer per file.** The manager is the sole writer of `inbox.md`; this Project is the sole
writer of its own `status.md`. Two writers never touch the same file, so there are no merge
conflicts. Everything is append-only / overwrite-own — forward-only git.

## Multi-Project repos — per-lane heartbeats (optional extension)

A SHARED repo can host several Projects ("lanes" — e.g. a mining lane and an exploration lane
cohabiting one game repo). The one-writer rule scales by **splitting the heartbeat, never by
sharing it**:

- **One status file per lane** — `control/status-<lane>.md` (e.g. `control/status-mining.md` +
  `control/status-exploration.md`). Each lane is the sole writer of its own file and overwrites
  it as its session's deliberate LAST step; no lane ever edits another lane's heartbeat.
- **`control/inbox.md` stays single** — the manager remains its one writer; a lane-specific
  order names its lane in `do:`.
- **Declare every lane heartbeat to the kit** — `substrate.config.json` →
  `"heartbeat_files": ["control/status-mining.md", "control/status-exploration.md"]` (default
  when unset: `["control/status.md"]`). The status checker then gates each listed file
  independently (missing / heartbeat-less lane = strict RED; per-lane staleness warns), and the
  Stop hook's overwrite reminder clears when any lane's heartbeat is fresh (it cannot know which
  lane a session belongs to). An empty list falls back to the default — misconfiguration never
  silently disables the gate.
- **One command, not hand-edits** — a Project joining a SHARED repo runs
  `bootstrap adopt --lane <name>`: it plants `control/status-<name>.md` (skip-if-exists),
  declares it in `heartbeat_files`, and leaves `inbox.md`/`README.md` single — a second lane
  never re-plants the first Project's files (the double-adoption fix).

## Delegated tally — coordinator-written heartbeats (multi-repo seats)

A coordinator seat that spans several repos may legitimately write the authoritative
tally in ITS status file, leaving the member repos' own heartbeats stale **by design**
(live precedent: the 2026-07-12→13 night run — the mineverse coordinator wrote the whole
SuperBot World tally while the member seats' heartbeats sat hours stale, and a
staleness-only sweep would have misclassified shipping seats as stalled). Two conventions
keep the delegation legible instead of looking like a dead lane:

1. **The delegated write is MARKED.** A coordinator overwriting a member repo's status
   (or carrying its tally) states so on the heartbeat it writes, first line after
   `updated:`:

   ```markdown
   COORDINATOR-DELEGATED heartbeat write — the coordinator seat authorized this status
   overwrite; authoritative tally for this repo lives here.
   ```

   One-writer-per-file is preserved as *one writer at a time*: the delegation line names
   the current writer, so a sweep never sees two silent writers.

2. **The member repo POINTS to its live tally.** A seat whose tally is delegated keeps
   its own `status.md` from going silently stale by carrying a standing pointer in
   `notes:` (or directly under `updated:`):

   ```markdown
   notes: tally DELEGATED to the coordinator seat — live status lives in
   <coordinator-repo> control/status.md; this heartbeat updates only on this seat's own
   sessions.
   ```

**Sweep rule (for managers and roll-up readers):** classify a seat by its **PR record +
the coordinator's status file**, never by seat-heartbeat staleness alone. A stale member
heartbeat carrying the delegation pointer is a healthy delegated lane; a stale heartbeat
with no pointer and no PR activity is the actual dark-lane signal.

## Per-session ritual (every session, and every routine wake)

- **FIRST:** git pull (a stale clone reads stale orders); read `control/inbox.md`; execute any
  order whose status is `new`, in priority order (P0 before P1) — **claim it first** (see
  "Claiming an order" below). An order's `do:` is a pointer to
  a committed doc — read it. If an order is ambiguous or you disagree, do NOT guess: write it in
  your status under `⚑ needs-owner` and proceed with the rest.
- **LAST (deliberate final step):** overwrite `control/status.md` — updated timestamp, current
  phase, health (green / red-by-design+why / broken+what), last-shipped PR, blockers, orders
  acked/done, `⚑ needs-owner`. You report order progress ONLY here; never edit `inbox.md`
  (the manager owns it — one writer per file).

The kit enforces this loop: `check` flags a missing or heartbeat-less `status.md`
(strict = red), warns when the heartbeat goes stale, and the Stop hook reminds you when
`status.md` was not overwritten this session.

## Claiming an order — one executor per order (claim FIRST, build second)

An order's `status: new` is visible to every session that wakes, so two readers can both
believe they are its executor — a realized failure, not a theoretical one (substrate-kit
PRs #50/#51: two lanes independently executed the same ORDER 005 the same day, and a whole
session's work had to be reconciled as twins). The manager only flips `new→done` after
seeing the status report; the claim covers the gap in between.

Before executing any `new` order:

1. **Re-read the bus at origin/main HEAD** — `control/inbox.md` AND every sibling status
   file (`control/status*.md`). If another lane's status already claims the order
   (`claimed-by:` naming its id) or reports it in `done=`, stand down and pick other work.
2. **Claim FIRST, on your own status file's orders line** — append
   `claimed-by: <order-ids> <lane-or-session> <ISO8601>` — and land it on **main** BEFORE
   any build work (a control-only fast-lane PR, or a direct commit where your rules allow
   one). A claim that exists only on a branch is invisible; only main counts.
3. **Re-read once more after the claim merges** — two claims can race in flight; the
   tiebreak is the earliest claim merged to main. The loser withdraws its claim line in
   its next status overwrite and stands down.
4. **Claims expire** — a claim with no visible build activity (no open PR, no fresh
   heartbeat referencing the order) after ~24h may be treated as abandoned and re-claimed;
   note the takeover in your status `notes:`. A dead lane must never deadlock an order.

With an active claim the `orders:` line reads e.g.:
`orders: acked=001-008 done=001-006 claimed-by: 007+008 coordinator-lane 2026-07-09T18:38Z`
— the executor drops the `claimed-by:` annotation in the overwrite that moves those ids
into `done=`. One writer per file is preserved: you only ever claim on your OWN status.
(Shipped by inbox ORDER 007 — the root-cause fix for the twin-execution failure; the
ritual was live-proven manually on this repo's own orders before graduating here.)

## Claiming work (not an ORDER) — one file per claim under `control/claims/`

Order claims cover the inbox; **work claims** cover everything else two
parallel sessions could both pick up — a coordinator-assigned slice, a
self-initiated build, a shared-surface change. Before starting such work,
create **one file per claim** — `control/claims/<branch-or-scope>.md`, a
single bullet `` - `branch-or-scope` · **scope** — detail · YYYY-MM-DD `` —
land it on main FAST (claims are `control/**` traffic and ride the CI fast
lane), re-read the directory at HEAD, build, then **delete the file at
session close**. Per-file is the measured winner over any shared list (~98%
merge-conflict rate for shared-append vs 0% per-file — superbot
`tools/sim/claim_layout_sim.py`); first claim merged to main wins a
collision; ~72h with no activity = abandoned, prune on sight. Full
convention + checker contract: `control/claims/README.md`. (`check` nags —
advisory-only — on unparseable, stale, duplicate, or legacy-located claims;
legacy homes `docs/owner/claims/` and root `claims/` are auto-detected
during the migration window, and a deliberate different home is pinned via
`substrate.config.json` → `claims_dir`.)

## `status.md` format (what you write every session — your heartbeat)

```markdown
# <project> · status
updated: <ISO8601>            # heartbeat — stale = the manager treats the Project as dark
phase: <what I'm doing right now, one line>
health: green | red-by-design (<why>) | broken (<what>)
kit: v<X.Y.Z> · check: green|red · engaged: yes|no   # kit self-report — see below
last-shipped: #<PR> — <one line>
blockers: <what's stopping me, or `none`>
orders: acked=<ids> done=<ids> [claimed-by: <ids> <lane-or-session> <ISO8601>]
⚑ needs-owner: <a decision/action only the owner can give, or `none`>
notes: <anything the manager should know>
```

Grammar source of truth: the tokens, field lists, and regexes of this format are kit-owned constants in the kit's `src/engine/grammar.py` (EAP §6.8) — the SAME module the `check` enforcers consume, so writer and enforcer cannot drift; agreement is pinned by the kit's `tests/test_grammar.py`.

The `kit:` line is the **substrate-coordinator visibility** channel (kit-lab reads it via the
manager relay — zero write access to this repo): `v<X.Y.Z>` = the vendored kit version this
repo actually runs (update it in the same session as every `bootstrap upgrade`); `check:` =
the latest `check --strict` verdict on this tree; `engaged:` = the post-adopt engagement gate
(`yes` once no UNRENDERED banner/slot remains, live CI runs the gate, and the session loop
has engaged).

**Exact grammar or invisible — keep the `kit:` token PLAIN.** The parser accepts a bold label
*before* a plain token (`- **kit heartbeat:** kit: v1.2.3 · check: green · engaged: yes` is a
live valid shape), but bolding the token itself does NOT parse — the fleet registry then reads
the row as "no `kit:` line" and the lane's engaged signal silently vanishes (a live adopter
incident, not a hypothetical). The taught negative example:

```markdown
- **kit:** v1.2.3 · check: green · engaged: yes
```

← does NOT parse (`KIT_LINE_RE`, kit `src/engine/grammar.py` — the optional bold group cannot
contain the `kit:` token). If your heartbeat wants a bold label, put it *before* a plain
`kit:` token.

**Version truth defers to the generated registry, never to this line.** Heartbeat `kit:`
lines are self-reports and chronically lag 1–3 releases behind the tree (the fleet's
recurring self-report DRIFT class); the kit repo's generated `docs/adopters.md` —
regenerated from each adopter's committed tree — is the fleet's version truth, and your own
committed tree (the vendored dist) is yours. Never hand-assert a fleet version spread from
heartbeat lines; keep this line in sync as a courtesy signal, not as proof.

## ⚑ needs-owner — the OWNER-ACTION item format (quality contract)

The owner is the scarcest resource in the program: every ask routed to the owner costs
attention, and an unclear or unnecessary ask stalls your own lane on top of burning his.
**Before routing ANYTHING to the owner, try it yourself or cite the exact wall** — an
assumption-based ask ("agents probably can't do X") is banned; the bar is the capability
ledger (`docs/CAPABILITIES.md`) plus one real attempt with the captured error.

Every ⚑ needs-owner item carries ALL of these REQUIRED fields — inline on the item, or as a
structured block the item links to:

```markdown
⚑ OWNER-ACTION
WHAT: <one plain sentence, zero jargon — the thing the owner does>
WHERE: <exact click path or URL>
HOW: <paste-ready text/values where applicable, or "click only">
RISK: <one class per manual step — ✅ safe / read-only · ↩️ reversible (say how to undo) · ⚠️ irreversible / destructive>
WHY-IT-MATTERS: <one sentence, in product terms>
UNBLOCKS: <what starts moving the moment it's done>
VERIFIED-NEEDED: <the attempt you made + the exact error/wall proving only the owner can do
this — never an assumption>
```

Hygiene: **expire or withdraw stale asks every session** (an answered or obsolete ask left in
the list is drift), and **fewer, clearer asks beat complete lists**. `check` warns — advisory,
never exit-affecting — when a non-`none` ⚑ needs-owner list lacks these fields.

Grammar source of truth: the tokens, field lists, and regexes of this format are kit-owned constants in the kit's `src/engine/grammar.py` (EAP §6.8) — the SAME module the `check` enforcers consume, so writer and enforcer cannot drift; agreement is pinned by the kit's `tests/test_grammar.py`.

## Owner-assist output standard — every owner-facing output, not just asks

The OWNER-ACTION block above covers the *needs-owner ask*; this standard
covers ALL output routed to the owner — reports, questions, values to paste,
links. The contract in one line: **the owner never derives anything** — an
output that requires the owner to parse, derive, or transform anything is a
drafting defect, not an owner task.

1. **Paste-ready, finished values.** Every value the owner must enter is
   computed and printed final — `NAME=value`, the full command, the full
   file body — never a recipe for deriving it. When the owner must paste
   something, give the exact link to where it goes; a full file goes in ONE
   copyable fenced block, directly in chat.
2. **Exact destination, always.** Every action names its exact destination:
   a deep URL, a console path to the exact field (surface → section →
   field, e.g. `Railway → project → service → Variables`), or a repo path +
   line. Never a bare "go to settings" — `check` nags that class (advisory).
3. **Risk class on every manual step:** ✅ safe / read-only · ↩️ reversible
   (say how to undo) · ⚠️ irreversible / destructive. One class per step,
   stated on the step (the `RISK:` line in an OWNER-ACTION block).
4. **Structured choices, recommendation first.** A decision put to the
   owner is options A/B(/C) with a **bolded recommendation** and a one-line
   rationale, answerable with one letter — never an ask that requires the
   owner to parse, derive, or transform anything.
5. **Large outputs: digest + rendered link, never a wall of text.** Default
   delivery is a control-plane rendered link plus a 3-line digest in chat;
   the fallback — full text in one copyable block directly in chat — applies
   where the control plane cannot render the repo yet. Link rules: deep-link
   the exact file, never the repo root; the rendered view for things the
   owner should *read*, the GitHub blob URL for things the owner should
   *edit*; post-merge, link `ref=main`; the control-plane render cache is
   180 s — append `&refresh=1` when the owner must see a just-pushed change.

Worked example — digest + rendered deep link + a six-field ask carrying its
risk class (every rule above in one output):

```
📄 Adopter-outcomes report — shipped (PR #247, merged b862e9a)

Digest: before/after adoption is unmeasurable (9/10 adopters born <20h
before their kit-install PR); false-claim audit near-clean (1 confirmed,
self-corrected in 6 min); post-adoption time-to-ship baselines recorded.

Full report (rendered, phone-readable):
https://control-plane-production-abb0.up.railway.app/journal/substrate-kit/file?path=docs/reports/2026-07-11-adopter-outcomes-measurement.md

⚑ OWNER-ACTION — set GITHUB_TOKEN on the control-plane service
WHAT: paste one variable into Railway so private-repo pages stop degrading.
WHERE: railway.app → project `websites` → service `control-plane` →
       Variables → New Variable.
HOW (paste-ready): name `GITHUB_TOKEN`, value = the fine-grained PAT you
       created for the fleet's repos (contents: read). One paste, Save.
RISK: ↩️ reversible — delete the variable to undo.
WHY-IT-MATTERS: private-repo renders show "not-configured" banners until
       this is set.
UNBLOCKS: rendered file links + queue items for private repos.
VERIFIED-NEEDED: attempted 2026-07-11 — raw fetch of a private path
       returns 404 without a token (token-on-raw also verified NOT to
       work, so the API fallback is the only private path).
```

Grammar source of truth: the risk-class tokens, the structured-choice phrases, and the vague-destination scan of this standard are kit-owned constants in the kit's `src/engine/grammar.py` — the SAME module the `check` enforcers AND the `/intake` skill pins consume, so writer, skill, and enforcer cannot drift; agreement is pinned by the kit's `tests/test_owner_assist.py`.

## `inbox.md` order format (manager-written, append-only)

```markdown
## ORDER <nnn> · <ISO8601> · status: new     # manager flips new→done after seeing status done=
priority: P0 | P1 | P2
do: <pointer to a committed doc/section + the ask, kept short>
why: <one line>
done-when: <acceptance test>
```

Grammar source of truth: the tokens, field lists, and regexes of this format are kit-owned constants in the kit's `src/engine/grammar.py` (EAP §6.8) — the SAME module the `check` enforcers consume, so writer and enforcer cannot drift; agreement is pinned by the kit's `tests/test_grammar.py`.

## CI + auto-merge notes (learned live, 2026-07-09)

- **Heartbeat commits ride a fast lane, not a `paths-ignore`.** A control-only diff (only
  `control/**` files changed) must still *report* every required status check, or GitHub treats
  the missing contexts as pending and auto-merge jams forever. The kit's planted
  `substrate-gate.yml` therefore short-circuits GREEN inside the job on control-only diffs
  instead of skipping the workflow — copy that pattern (an in-job early exit) into any other
  heavy suite rather than adding `paths-ignore: [control/**]` to a workflow whose check is
  required.
- **API-authored PRs may not trigger CI.** A PR created purely through an app/integration token
  (e.g. the GitHub Contents API + a REST PR create) can sit with **zero check runs** — required
  checks then never report and the PR cannot auto-merge. The manager's canonical write path is
  therefore a **direct Contents-API commit to the default branch of `inbox.md`** (it is the sole
  writer, so no PR is needed). When this Project ships control changes by PR, push the branch
  over git (a real `git push` triggers `pull_request`/`push` events) before or after creating
  the PR, and verify the PR shows check runs before relying on auto-merge.
