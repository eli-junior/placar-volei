# Decisions

One record per file in `records/`: open questions and decisions future work must respect. Each record's `status` owns its state; this index only explains the format.

## Files

`records/YYYY-MM-DDTHHMMZ-short-slug.md` (UTC). Create a record when forgetting it would cause rework or repeated debate.

## Status

`Open`, `Decided`, `Superseded`, `Dropped`. Find open records by searching `status: Open`.

## Record Template

```markdown
---
status: Open
raised: YYYY-MM-DD
decided:
deciders:
  - name-or-role
supersedes:
related:
  - CV1.DS1.US1
---

# Question or decision

## Question

## Decision

Pending

## Rationale

## Consequences
```
