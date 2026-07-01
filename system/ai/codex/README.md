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
- Reinstall or adapt the baseline through APM after an APM manifest exists.
- Treat `using-superpowers` as approval-gated cleanup, not as baseline.
- Treat system, runtime, and plugin-provided skills as vendor or app state
  unless intentionally declared.

## Repo Ownership

This directory may contain only Codex-safe managed declarations, generated
adapters, and redacted templates. Do not copy raw `~/.codex` files into the
repo.

Future APM output should target Codex only after the target path is reviewed and
existing local skills are snapshotted.
