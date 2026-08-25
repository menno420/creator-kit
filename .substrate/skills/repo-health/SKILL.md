---
name: repo-health
description: "Audit doc + session-log hygiene (bootstrap check) and summarize drift."
---

# repo-health

Audit creator-kit's documentation + session-log hygiene.

1. Run `python3 bootstrap.py check` — badges, link resolution, doc
   reachability, and the required session-log markers.
2. Summarize the drift: orphaned docs, missing badges, incomplete logs.
3. Fix the small ones (link the orphan, badge the doc); capture the rest as ideas.

Declared capabilities: run.
