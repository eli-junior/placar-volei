# Roadmap

Meaningful progress, not every task. Each item lives in its own folder, and its frontmatter owns its state. This index explains the structure only.

## Levels and Codes

- `CV<N>` Value: a major capability boundary.
- `DS<N>` Delivery Story: a coherent arc inside a Value, with a done condition.
- `US<N>` User Story: observable behavior the Navigator can validate.
- `TS<N>` Technical Story: internal capability, validated by automated evidence.
- Tasks live inside stories. Maintenance stays out of the roadmap; record it in the worklog.

## Folders

```text
docs/project/roadmap/
  cv<N>-<slug>/index.md
  cv<N>-<slug>/cv<N>-ds<M>-<slug>/index.md
  cv<N>-<slug>/cv<N>-ds<M>-<slug>/cv<N>-ds<M>-us<K>-<slug>/index.md
```

A story is one `index.md` with the sections Intent, Acceptance, Plan, Validation Route, Review, History. Add `plan.md` or `test-guide.md` only for a large story.

## States

`Planned`, `Active`, `Blocked`, `Validated`, `Done`, `Deferred`, `Dropped`. Give `Blocked`, `Deferred`, and `Dropped` a `status_reason`. Find work by searching `status: Active`.

## Effort

Stories carry `effort` from 1 to 10: 1-2 trivial, 3-4 small, 5-6 moderate, 7-8 large, 9-10 critical (prefer splitting).

## Item Template

```markdown
---
code: CV1.DS1.US1
level: User Story
status: Planned
status_reason:
effort: 5
effort_reason:
order: 1
writer:
updated: YYYY-MM-DD
---

# Title

## Intent

## Acceptance

Given ...
When ...
Then ...
And ...
```
