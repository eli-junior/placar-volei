# Ariad sidecar

This folder holds the Ariad orchestrator for this project. It needs Python 3.11+ and Git.

```bash
python .ariad/ariad.py init      # copy the Ariad templates into the project (never overwrites)
python .ariad/ariad.py setup     # interview: briefing, principles, commands, roadmap with effort
python .ariad/ariad.py run       # stories: writer and reviewers work, you validate at checkpoints
python .ariad/ariad.py status    # roadmap and the active story
python .ariad/ariad.py agents    # installed, logged in, usage left
python .ariad/ariad.py check     # test every agent CLI in every effort band
python .ariad/ariad.py export    # build a new sidecar zip for another project
```

- `ariad.toml`: docs language, verify commands, plan threshold, agents, and effort bands. Run `check` after editing it.
- `state.json`, `setup.json`, `logs/`: runtime files, ignored by Git.
- Everything else in this folder is versioned with the project.

Full guide: Ariad site, Adoption > Sidecar Installation.
