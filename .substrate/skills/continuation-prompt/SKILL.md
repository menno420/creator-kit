---
name: continuation-prompt
description: "Carry a session into a fresh one — verify state at HEAD, commit what belongs in the repo, and emit a paste-ready prompt that transfers intent without narrowing it."
---

# continuation-prompt

Carry a creator-kit session into a fresh one: emit a paste-ready prompt
that points at the repo and carries only what the repo cannot.

A handoff's job is to transfer INTENT, not to summarize work. The failure
mode is a prompt that reads authoritative while quietly narrowing what the
owner asked for — the next session executes the prompt, not the conversation.

## Instructions

1. Verify state at HEAD before writing a word —
   `git fetch origin main && git log -1 --oneline origin/main`. Every PR
   number, SHA, count and "X is blocked" in your draft was true when the
   chat said it; re-derive or mark it uncertain.
2. Split what only this chat knows from what the repo already holds. Commit
   the second kind FIRST — a decision that belongs in a doc goes in the doc,
   not in the prompt. If the prompt is getting longer than the doc it should
   have pointed at, stop and commit instead.
3. Write it in this shape. Drop any section that would be empty; never pad.

   - **CONTINUE** — one line: what this session picks up.
   - **BEFORE YOUR FIRST TOOL CALL** — **mandatory, and it goes in the
     prompt verbatim, never as a link.** Emit this block:

         BEFORE YOUR FIRST TOOL CALL — state back what you think this task
         is. Inline in your first reply, not as a question, in a few
         sentences: the goal in your own words, the specs and constraints it
         implies, the scope you take it to cover, and the follow-on the
         owner probably wants but did not spell out. Then begin. This is the
         owner's one cheap chance to correct your aim; a first reply that
         only announces your first action spends it.

     Why in the prompt rather than a pointer: the receiving session has
     invoked no skill yet, so a rule living in one cannot bind it. Measured
     2026-08-06 — a session opened from one of these prompts and its whole
     first response was *"I'll start by getting oriented — checking the
     environment, then landing #602 as instructed."* That is a first
     **action**, not an **understanding**; there was nothing in it the owner
     could correct. Two traps: it is not a summary of the prompt (a plan is
     not an understanding — say what the goal *implies* and what it probably
     extends to), and it is not a question (state it inline and proceed;
     blocking for approval spends the owner's attention instead of saving
     it).
   - **WHERE THINGS STAND** — verified state only, each item checked at HEAD.
   - **READ FIRST** — 2-4 paths, most specific first. The minimum to act
     correctly, and **say that it is a floor, not a boundary**, so it cannot
     be read as sufficient. See the exception below.
   - **DECIDED (do not re-litigate)** — each with its reason clause.
   - **REJECTED, AND WHY** — what stops the next session re-proposing it.
   - **OPEN** — genuinely undecided, and what would settle it.
   - **YOUR FIRST STEP** — one concrete action that verifies the state above
     rather than trusting it.
   - **DONE WHEN** — acceptance plus this repo's real verify command,
     `${verify_command}`.
   - **OUT OF SCOPE** — always present; the cheapest correction available.

4. **The comprehension exception — when reading IS the job.** Default READ
   FIRST to the minimum. INVERT it when the owner asked for understanding
   rather than an outcome. The tell is his words: *"fully understand"*,
   *"read the required order and more"*, *"everything it should know is
   documented there"*, *"and only after it has fully read"*. Then:
   - **Name the corpus, not a file list.** A list of paths reads as complete;
     a corpus reads as a floor.
   - **Do not delegate completeness to the boot file.** Check its read path
     against the repo yourself and name what it omits. A boot file that
     omitted the repo's own most-important document is exactly how this
     exception came to exist.
   - **Give the reading an acceptance test** — "you are oriented when you can
     state this repo's purpose, live state and next step from its own docs" —
     or the next session picks its own depth, which is the failure this
     prevents.
   - **Budget it as work.** Comprehension of a large repo is most of a
     session; if a build task rides along, say which yields.

5. Adapt to the target surface: if its network is restricted, move installs
   into a prerequisite line rather than a step. Carry the landing discipline
   the repo actually uses.

## Traps

- **Never let the operational list contradict the goal.** If READ FIRST says
  four paths and the job section says "understand the repo completely", the
  next session does the four paths. An imperative beats an aspiration every
  time. Reconcile them, or the narrower one silently wins.
- **Do not restate the project** — the repo's boot file does that, and prose
  goes stale the moment the repo moves. But do not assume that file is
  complete either (see step 4).
- **Do not invent a next step to sound finished.** "Confirm the state below,
  then ask which branch to take" is a real instruction.

Declared capabilities: read, edit, run.
