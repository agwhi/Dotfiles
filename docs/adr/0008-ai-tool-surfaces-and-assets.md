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

The current `/usr/local/bin/apm` install is a managed exception until its own
installer provenance is declared. No APM install, update, prune, uninstall, or
self-update command should run without an explicit Reset Approval Gate.

The repo should not invent an APM manifest until the canonical
`grill-with-docs` package source and target surfaces are chosen. The expected
future source-of-truth files are `system/ai/apm/apm.yml` and
`system/ai/apm/apm.lock.yaml`, with read-only or non-deploying APM checks run
before any target files are written.
