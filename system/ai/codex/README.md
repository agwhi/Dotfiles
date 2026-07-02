# Codex

Codex is a canonical AI Tool Surface installed through Homebrew and also runs
inside the Codex desktop app runtime.

Current local state:

- Homebrew binary: `/opt/homebrew/bin/codex`
- App runtime binary: `/Applications/Codex.app/Contents/Resources/codex`
- Version observed: `0.142.4`
- Homebrew declaration: `cask "codex"` in `system/packages/Brewfile`
- Local config root: `~/.codex`

Homebrew metadata reported a newer cask version during this pass, but this task
does not upgrade Codex.

## Classification

The Homebrew cask is the canonical install surface for the Codex CLI. Codex app
runtime helper commands, temporary wrappers, and bundled runtime tools are
execution context, not package-manager drift.

`~/.codex` is Sensitive Local State by default. It contains auth-adjacent state,
history, logs, local databases, trusted-project state, plugin caches, runtime
assets, generated files, and current local skills.

## Assets

Current global skills include:

- `grill-with-docs`
- `using-superpowers`
- Codex system skills
- Codex runtime/plugin skills

Target state:

- Keep `grill-with-docs` as the only Baseline AI Asset.
- Reinstall or adapt the baseline through APM only after the package source
  mismatch is resolved.
- Treat `using-superpowers` as approval-gated cleanup, not as baseline.
- Treat system, runtime, and plugin-provided skills as vendor or app state
  unless intentionally declared.

## APM Status

`system/ai/apm/apm.yml` and `system/ai/apm/apm.lock.yaml` now pin the public
`grill-with-docs` APM package. Scratch preview showed that the package is a
thin wrapper that invokes `/grilling` and `/domain-modeling`, while the current
live Codex skill is self-contained and includes the detailed workflow plus
format references.

Do not deploy the pinned public package over `~/.codex/skills/grill-with-docs`
until one of these is true:

- the dependent `grilling` and `domain-modeling` assets are deliberately added
  to the Global AI Baseline
- a self-contained `grill-with-docs` package source is chosen

APM's default Codex skill output is `.agents/skills/`. Codex desktop currently
discovers the live global skill from `~/.codex/skills`, and the scratch preview
confirmed APM can produce that layout with `--legacy-skill-paths`.

## Repo Ownership

This directory may contain only Codex-safe managed declarations, generated
adapters, and redacted templates. Do not copy raw `~/.codex` files into the
repo.

Future APM output should target Codex only after the target path is reviewed,
the source mismatch is resolved, and existing local skills are snapshotted.
