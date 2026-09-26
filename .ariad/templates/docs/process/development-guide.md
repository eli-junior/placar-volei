# Local Development Guide

Project facts for the Driver. Ariad's rules live in `AGENTS.md`; this file records what is specific to this project and overrides Ariad where it says so.

## Commands

<!-- One fenced command each: install, test, lint or format, run locally. -->

## Verification

<!-- What proves a change works here: automated checks, manual routes, URLs, sample data, data safety rules. -->

## Documentation Surfaces

- `docs/project/briefing.md`: stable context.
- `docs/product/principles.md`: product trade-offs.
- `docs/project/roadmap/`: one folder per item; state in frontmatter `status`.
- `docs/project/decisions/records/`, `docs/project/debt/items/`, `docs/process/worklog/entries/`: one file per record.
- `CHANGELOG.md`: closed versions only.

## Navigator Preferences

Ariad defaults apply unless changed here.

- Commit: after a validated, accepted story.
- Push: ask first.
- Checkpoints: one acceptance stop below effort 4; separate plan stop from effort 4.
- Documentation: the smallest update that keeps the project coherent.
- Worklog: one entry per meaningful milestone.
- Branches and pull requests: work on the current branch unless stated here.

## Commit and Release

<!-- Branch, pull request, versioning, and release rules. Ariad default: a closed Value is MAJOR, a Delivery Story MINOR, a story or maintenance fix PATCH. -->

## Local Exceptions

<!-- Deliberate deviations from Ariad, each with its reason and revisit trigger. -->
