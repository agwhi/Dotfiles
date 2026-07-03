# Symlink APM Project Files Into User APM

The Orchestrator Repo owns the APM project files for the Global AI Baseline:

- `system/ai/apm/apm.yml`
- `system/ai/apm/apm.lock.yaml`

The live user APM project consumes those files through the normal dotfiles
symlink model:

- `~/.apm/apm.yml` -> `system/ai/apm/apm.yml`
- `~/.apm/apm.lock.yaml` -> `system/ai/apm/apm.lock.yaml`

## Consequences

APM remains the AI Asset Manager. It should materialize generated modules and
target output after the locked package source is corrected and a later
deployment gate approves writing target files.

The Orchestrator Repo should not keep a repo-owned Codex skill tree as the
primary source of truth. Do not symlink `system/ai/codex/skills/grill-with-docs`
into `~/.codex`.

Running the normal symlink setup on a machine may back up existing
`~/.apm/apm.yml` or `~/.apm/apm.lock.yaml` before replacing them with symlinks.
This is acceptable because the repo files are the source of truth for APM's
baseline project.

Live Codex deployment remains blocked. The currently locked public
`grill-with-docs` package is not equivalent to the desired live skill, and
`using-superpowers` remains intentionally excluded from the Global AI Baseline.
