# Ariad sidecar

This folder holds the Ariad orchestrator for this project. It needs Python 3.11+ and Git.

```bash
python .ariad/ariad.py init      # copy the Ariad templates into the project (never overwrites)
python .ariad/ariad.py setup     # interview: briefing, principles, commands, roadmap with effort
python .ariad/ariad.py run       # stories: writer and reviewers work, you validate at checkpoints
python .ariad/ariad.py run --automode # continue development; human acceptance remains pending
python .ariad/ariad.py validate  # validate automode stories individually
python .ariad/ariad.py status    # roadmap and the active story
python .ariad/ariad.py agents    # installed, logged in, usage left
python .ariad/ariad.py check     # test every agent CLI in every effort band
python .ariad/ariad.py export    # build a new sidecar zip for another project
```

- `ariad.toml`: docs language, verify commands, plan threshold, agents, and effort bands. Run `check` after editing it.
- `state.json`, `setup.json`, `logs/`: runtime files, ignored by Git.
- Everything else in this folder is versioned with the project.

Full guide: Ariad site, Adoption > Sidecar Installation.

## Interactive and automatic execution

`run` asks before starting another story. `run --automode` authorizes the plan and implementation
without waiting for human input, keeps automated verification and independent reviews, and makes
local checkpoint commits marked `Ariad-Human-Validation: pending`. It continues through eligible
roadmap stories until work ends, a required quality gate fails, or available agent quota runs out.
`--max N` bounds the number of stories. Automode uses remaining quota below the usual 10% reserve;
it does not manufacture work to burn tokens or guarantee an exact token count.

Automatic stories use `status: Validated`, `execution_mode: automode`, and `human_validation: pending`.
They are not Done and do not close their parents. Run `validate` (or `validate --story CODE`) to read
the evidence and test route, accept, skip, or report a failure. Failure returns the story to Planned
with human feedback retained. Acceptance records a separate commit and can close eligible parents.
Run `run` without `--automode` to restore interactive checkpoints; the mode is never enabled implicitly.

Every five implemented stories, including across restarts, a mandatory cumulative review uses
`[strong_review]`: by default Claude Opus with high effort, regardless of the story effort band.
It examines the full cumulative diff and records a report in `docs/process/worklog/entries/`.
Missing quota, errors or requested changes keep the gate pending before a sixth story can start.
Fix the reported issues, commit them and run again to repeat the review. Human acceptance remains separate.

`init`, `setup`, `run`, `agents` and `check` check installed CLI versions against official release sources
before their usual evaluations. An available update is shown; unavailable network/version information
is reported as unknown and does not prevent evaluation. These checks do not install software.
Custom agents can set `version_url` to a JSON endpoint returning `version` or `tag_name`.
Set `ARIAD_OFFLINE=1` to check local versions without network access; update status remains unknown.

Python renders structured results as terminal panels; raw CLI output stays in `.ariad/logs/`.
Copilot Auto is called without `--reasoning-effort`, which Auto does not support. Existing configs
with that combination are adapted in memory. Nonzero CLI failures show the underlying error immediately.
