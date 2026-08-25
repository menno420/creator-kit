# Hook settings — customization contract

The kit **stages** `settings.template.json`; it never writes your
`.claude/` tree. Install by merging the template's `hooks` block into
your repo's `.claude/settings.json` yourself, after checking every
row below against your repo.

| field | what must match your repo |
| --- | --- |
| `interpreter` | the Python that runs the kit itself — every hook command below starts with it; set it to an interpreter available on your PATH |
| `interpreter_for_checks` | your *project's* verification interpreter (the version your CI pins, e.g. `python3.10`) — kept separate from `interpreter` on purpose |
| `bootstrap.py` path | each hook command assumes `bootstrap.py` sits at your repo root; rewrite the path inside every command if it lives elsewhere |
| `state_dir` | where kit state + staged artifacts live (default `.substrate`) — the post-edit generated-artifact warning keys off it |
| `docs_root` | your documentation root (default `docs`) — the post-edit badge warning and the SessionStart trigger scan key off it |
| `sessions_dir` | where per-session logs live (default `.sessions`) — the Stop-hook session-log advisory keys off it |
| cadence knobs | `cadence.*` in `substrate.config.json` (`compaction_sessions`, `reconciliation_sessions`, `staleness_days`, `critical_slot_grace_sessions`, `guided_practice_sessions`) drive the SessionStart triggers and Stop-hook advisories |

All four hooks are advisory and fail open: they always exit 0 and
never block a tool, an edit, or a session stop.
