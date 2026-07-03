# AI Tool Surfaces And Assets

APM is the selected AI Asset Manager for the Development Ecosystem. This fills
the tool-choice gap left by ADR-0002: custom and third-party AI Assets should be
declared, locked, installed, audited, and adapted through APM, while
tool-specific CLI binaries such as Codex, Claude Code, opencode, and Pi remain
separate AI Tool Surfaces with their own install provenance. ADR-0003 still
sets the Global AI Baseline to only `grill-with-docs`; selecting APM does not
promote `using-superpowers`, Pi, opencode, or project-specific assets into the
global baseline.

## Consequences

The current `/usr/local/bin/apm` install is a managed exception. Official APM
documentation includes a Homebrew tap formula, so this repo declares
`microsoft/apm/apm` in the Brewfile as the intended binary installer. The
manual binary stays in place until a separate task installs/verifies the
Homebrew formula and confirms PATH precedence. No APM update, prune, uninstall,
or self-update command should run without an explicit Reset Approval Gate.

The APM package evidence files are `system/ai/apm/apm.yml` and
`system/ai/apm/apm.lock.yaml`. The lockfile pins the public
`mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1` wrapper plus its
public `grilling` and `domain-modeling` dependency skills at the same
`v1.0.1` tag. ADR-0009 exposes the repo APM project to `~/.apm` with symlinks,
while live Codex target placement remains blocked until a later deployment gate
approves target writes and reviews the generated split-skill layout.
