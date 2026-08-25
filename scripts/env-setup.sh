#!/usr/bin/env bash
# scripts/env-setup.sh — this repo's environment setup hook (kit-planted).
#
# THE SETUP-SCRIPT CONTRACT (EAP program review 2026-07-10 §6.5; rendered
# from the fleet-manager archetype material — environments/archetypes.md +
# templates/setup-universal.sh, the shim every archetype script derives
# from). Every fleet environment's setup shim prefers THIS file when it
# exists, so repo-specific setup lives here — one durable per-repo hook
# instead of divergent hand-rolled environment scripts. Four rules, paid
# for in dead sessions across 4+ lanes:
#
#   1. ALWAYS exit 0. A failing setup script = dead session, no signal —
#      the worker never even reports. Worst case is a session with missing
#      deps that can still report and self-repair; that beats no session.
#   2. NO SECRET VALUES — ever. Variable NAMES may be referenced; real
#      values live only in the environment panel (owner-side). If it is
#      not a name or a placeholder, it does not go in this file.
#   3. Defensive posture: set +e (no -e / -u / pipefail), and every
#      install step guarded by an existence check — one missing manifest
#      must never block the rest.
#   4. Run from the repo root: the environment shim invokes this as
#      `cd <repo> && bash scripts/env-setup.sh`.
#
# HOST-OWNED after planting: add repo-specific steps (interpreter pins,
# extra manifests, toolchains) in the marked section below, keeping the
# contract. The kit's `check` validates the contract (advisory-only):
# no fatal shell posture, no secret-shaped literals, and an unconditional
# `exit 0` as the last effective line.

set +e

log() { echo "[env-setup] $*"; }

PY=python3

# Guarded dependency installs — each manifest only if present, never fatal.
for req in requirements.txt requirements-dev.txt; do
  if [ -f "$req" ]; then
    log "$PY -m pip install -r $req"
    "$PY" -m pip install --quiet -r "$req" \
      || log "$req install failed (non-fatal, continuing)"
  fi
done

if [ -f pyproject.toml ]; then
  log "$PY -m pip install -e . (pyproject.toml present)"
  "$PY" -m pip install --quiet -e . \
    || log "editable install failed (non-fatal, continuing)"
fi

# --- repo-specific steps go below (keep every step guarded + non-fatal) ----

# Contract rule 1 — the single most important line. Do not "improve" this.
log "env-setup complete (defensive: always exit 0)"
exit 0
