# AI Tool Surfaces And Assets

APM is the selected AI Asset Manager for the Development Ecosystem. This fills
the tool-choice gap left by ADR-0002: custom and third-party AI Assets should be
declared, locked, installed, audited, and adapted through APM, while
tool-specific CLI binaries such as Codex, Claude Code, opencode, and Pi remain
separate AI Tool Surfaces with their own install provenance. ADR-0003 still
sets the Global AI Baseline to only `grill-with-docs`; selecting APM does not
promote `using-superpowers`, Pi, opencode, or project-specific assets into the
global baseline.

AI harness binaries and apps should be reproducible from the package manifests
where possible. Codex, Claude Desktop, and the stable Claude Code terminal
harness are Homebrew cask-owned surfaces; APM owns shared AI Assets installed
into those surfaces after separate target-write gates.

## Consequences

The active `apm` command resolves through the Homebrew formula
`microsoft/apm/apm`, declared in the Brewfile and installed from the official
Microsoft tap. The old `/usr/local/bin/apm` ->
`/usr/local/lib/apm/apm` manual install remains only as an approval-gated
cleanup candidate until a separate task removes the root-owned duplicate. No
APM update, prune, uninstall, or self-update command should run without an
explicit Reset Approval Gate.

The APM package evidence files are `system/ai/apm/apm.yml` and
`system/ai/apm/apm.lock.yaml`. The lockfile pins the public
`mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1` wrapper plus its
public `grilling` and `domain-modeling` dependency skills at the same
`v1.0.1` tag. ADR-0009 exposes the repo APM project to `~/.apm` with symlinks,
and the approved Codex deployment has materialized the split baseline. Claude
Code, opencode, Pi, and future target surfaces still require separate
target-write gates before APM materializes assets for them.
