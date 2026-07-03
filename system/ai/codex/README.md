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

- `.system`
- `codex-primary-runtime`
- `domain-modeling`
- `grill-with-docs`
- `grilling`

Target state:

- Keep the APM-managed public `grill-with-docs` workflow as the only Baseline
  AI Asset, materialized as the split Codex skills `grill-with-docs`,
  `grilling`, and `domain-modeling`.
- Keep `using-superpowers` absent.
- Treat `.system`, `codex-primary-runtime`, and plugin-provided skills as
  vendor or app state unless intentionally declared.

## APM Status

`system/ai/apm/apm.yml` and `system/ai/apm/apm.lock.yaml` now pin the public
`grill-with-docs` APM package plus the public dependency skills it invokes:

- `mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1`
- `mattpocock/skills/skills/productivity/grilling#v1.0.1`
- `mattpocock/skills/skills/engineering/domain-modeling#v1.0.1`

Scratch preview showed that `grill-with-docs` is a thin wrapper that invokes
`/grilling` and `/domain-modeling`. The 2026-07-03 source investigation found
that `grilling` lives under
`skills/productivity/grilling`, not `skills/engineering/grilling`, and a frozen
scratch install generated all three public skills without `using-superpowers`.

APM's default Codex skill output is `.agents/skills/`. Codex desktop currently
discovers the live global skill from `~/.codex/skills`, and the scratch preview
confirmed APM can produce that layout with `--legacy-skill-paths`.

After the approved APM deployment, the live canonical Codex baseline is the
split output under `~/.codex/skills`: `grill-with-docs/SKILL.md`,
`grilling/SKILL.md`, and the `domain-modeling` skill plus its format
references. Old format references under `grill-with-docs/` and
`using-superpowers` should remain absent.

## Repo Ownership

This directory may contain only Codex-safe managed declarations, generated
adapters after review, and redacted templates. It should not contain a
repo-owned `skills/` tree as the primary model for global Codex skills.

Do not copy raw `~/.codex` trees, auth-adjacent state, histories, caches,
vendor plugin contents, generated target output, or unrelated local skills into
the repo.
