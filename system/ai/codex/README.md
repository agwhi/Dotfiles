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
- Receive baseline assets from APM after the locked package source is corrected.
- Treat `using-superpowers` as approval-gated cleanup, not as baseline.
- Treat system, runtime, and plugin-provided skills as vendor or app state
  unless intentionally declared.

## APM Status

`system/ai/apm/apm.yml` and `system/ai/apm/apm.lock.yaml` now pin the public
`grill-with-docs` APM package. Scratch preview showed that the package is a
thin wrapper that invokes `/grilling` and `/domain-modeling`, while the current
live Codex skill is self-contained and includes the detailed workflow plus
format references.

Do not deploy the pinned public package over `~/.codex/skills/grill-with-docs`.
The 2026-07-03 expanded scratch test showed that `domain-modeling` exists, but
`mattpocock/skills/skills/engineering/grilling#v1.0.1` is absent at that path.
The current public package is therefore not equivalent to the desired live
skill.

APM's default Codex skill output is `.agents/skills/`. Codex desktop currently
discovers the live global skill from `~/.codex/skills`, and the scratch preview
confirmed APM can produce that layout with `--legacy-skill-paths`.

Do not run live Codex deployment yet. After the package source is corrected and
a later deployment gate approves target writes, APM should materialize the
Codex target output.

## Repo Ownership

This directory may contain only Codex-safe managed declarations, generated
adapters after review, and redacted templates. It should not contain a
repo-owned `skills/` tree as the primary model for global Codex skills.

Do not copy raw `~/.codex` trees, auth-adjacent state, histories, caches,
vendor plugin contents, generated target output, or unrelated local skills into
the repo.
