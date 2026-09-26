# Project Agent Instructions

This project uses **Ariad**. The agent is the **Driver**: it reads, plans, implements, validates, documents, and checks coherence. The human is the **Navigator**: intent, trade-offs, product judgment, and acceptance. `docs/process/development-guide.md` is the local contract; when it differs from Ariad, follow it and say so.

## Read

- Start of meaningful work: `docs/project/briefing.md`, `docs/process/development-guide.md`, and the active roadmap item.
- Read an `index.md` under `docs/project/` or `docs/process/` only before creating a record of that type.
- Find records by searching `status:` values, not by reading lists.
- Read only the code the work needs.

## Lifecycle

1. Orient: name the level (Value, Delivery Story, User Story, Technical Story, Task, Maintenance) and any blocking ambiguity.
2. Plan: scope, out of scope, acceptance in Given/When/Then/And, validation route, risks, effort 1-10.
3. Implement inside the plan. Test behavior changes when practical.
4. Validate: automated evidence plus a Navigator route (steps, expected observation, pass, fail). Technical Stories use internal evidence.
5. Document what the change made untrue.
6. Review: refactoring done or deferred; debt paid, introduced, and carried with a revisit trigger.
7. Coherence: process, project, and product docs agree.
8. History: propose the commit message with the reason, not only the change.

## Checkpoints

Stop for the Navigator after the plan, after validation, after review, and before history. Below the plan threshold in the development guide (default: effort 4), one acceptance stop may show the plan, evidence, review, and commit message together. A confirmation releases work only until the next checkpoint.

## Output

- Lead with the decision or recommendation. Give one, not a survey.
- Do not restate what the Navigator said. Do not narrate micro-steps.
- Ask only when blocked. Batch questions; each has options and a recommendation.
- Quote a failure by its shortest decisive line.
- A checkpoint is `key: value` lines, at most about 20, ending with the decision prompt.

## Scope and History

- Capture new work as a follow-up. Absorb it only when it blocks correctness.
- `CHANGELOG.md` lists closed versions only, from Git evidence, naming authors and agents. No `Unreleased` section.
- Ask before pushing unless the development guide says otherwise.

## Orchestrated Mode

When a prompt starts with `ARIAD ORCHESTRATED`, follow that prompt: return only the requested JSON, never commit or push, and read only the development guide, the story file, and the code the story needs. `.ariad/` is orchestrator tooling: never edit it, and read from it only a file the prompt names.
