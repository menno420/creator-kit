---
name: review
description: "Review the branch diff against the binding contracts; comment with a verdict and fixes, no edits."
---

# review

Review the current branch's diff against creator-kit's binding contracts.

1. Read the contracts first (architecture / ownership / runtime), then the diff.
2. For each change check layer boundaries, mutation ownership, and the project's
   invariants. Flag violations with file:line and the rule they break.
3. Produce a verdict (approve / request-changes) + concrete fixes.
4. Do not edit — comment only. (The `review` stance pairs with this skill.)

Declared capabilities: comment.
