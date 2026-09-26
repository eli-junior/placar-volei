# Technical Debt Ledger

Structural cost the project consciously carries, one item per file in `items/`. Record only debt that may affect delivery, safety, maintainability, validation, operation, or product coherence; small imperfections stay in the story review.

## Files

`items/YYYY-MM-DDTHHMMZ-short-slug.md` (UTC). Each item's `status` owns its state; do not move files to change it.

## Status

`Carried`, `Paying`, `Paid`, `Dropped`. Find current debt by searching `status: Carried` or `status: Paying`.

## Item Template

```markdown
---
status: Carried
kind: design | test | docs | architecture | operations | process
severity: low | medium | high
source: CV1.DS1.US1
revisit_trigger:
closure_condition:
---

# Debt title

## Description

## Carrying Reason

## Impact
```
