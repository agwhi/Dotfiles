# Use APM For Shared AI Assets And Manifests For AI Tool Surfaces

Status: accepted.
Date: 2026-07-01.
Amended: 2026-07-07. Reconstructed decision history and ADR quality structure.
Refines: ADR-0002, ADR-0003.
Implemented by: ADR-0009.
Related: ADR-0001, ADR-0002, ADR-0003, ADR-0009,
docs/plans/ai-tooling-stabilization-plan.md,
docs/plans/ai-tool-surface-stabilization-plan.md, system/ai/README.md,
system/ai/apm/README.md, system/ai/apm/apm.yml,
system/ai/apm/apm.lock.yaml, system/packages/Brewfile.

## Context

The AI audit found several separate concerns that had been mixed together:
AI harness binaries, shared AI assets, generated target output, plugin caches,
tool-specific local state, and sensitive state. Codex, Claude Code, opencode,
Pi, APM, ChatGPT, and Ollama are tool surfaces. Skills, commands, prompts,
agents, and reusable workflows are assets. Auth, sessions, histories, caches,
provider config, and local databases are local state.

ADR-0002 says custom AI assets can live outside dotfiles but must be consumed
through the same declared asset flow as third-party assets. ADR-0003 keeps the
Global AI Baseline minimal. This ADR selects the asset manager and defines the
boundary between assets and harness binaries.

## Decision Drivers

- Codex, Claude Code, and opencode should receive the same shared baseline
  assets where their targets support it.
- AI harness binaries should be reproducible through package manifests where
  possible, but the asset manager should not own those binaries.
- Shared AI assets need source declarations, lock evidence, auditability, and
  target-write gates.
- Sensitive AI state must remain local and out of git.
- Project-specific AI assets should not become global baseline assets without
  an explicit promotion decision.

## Considered Options

- Manual per-tool skills and prompts: rejected because it creates drift between
  Codex, Claude Code, opencode, and future harnesses.
- Repo-owned Codex skill tree symlinked into `~/.codex`: rejected because it
  makes Codex output the source of truth instead of using a harness-neutral
  asset package flow.
- Use only the skill installer for Codex: rejected because it does not cover the
  cross-harness package, lock, and target model needed for Claude Code and
  opencode.
- Use APM for everything, including harness binaries: rejected because APM
  manages AI assets and target output, while binaries such as Codex, Claude
  Code, opencode, and Pi still need separate install provenance.
- Use APM for shared AI assets and package manifests for harness binaries:
  selected.

## Decision

APM is the selected AI Asset Manager for the Development Ecosystem.

APM owns declaration, lock evidence, audit, install, generated modules, and
target output for shared AI assets after package sources and target writes are
approved. The repo-owned APM project files are:

- `system/ai/apm/apm.yml`
- `system/ai/apm/apm.lock.yaml`

AI harness binaries and apps remain separate AI Tool Surfaces with their own
install provenance. Codex, Claude Desktop, Claude Code, opencode, ChatGPT,
ChatGPT Atlas, Ollama, and APM are declared through package manifests where
possible. Pi is declared through the canonical pnpm global path because Alex
uses it.

The Global AI Baseline remains the `grill-with-docs` workflow. The current APM
lockfile pins the public `grill-with-docs` wrapper plus its `grilling` and
`domain-modeling` dependency skills at `v1.0.1`.

## Consequences

- Shared AI assets should be added through APM package sources and lockfile
  updates, not by hand-copying files into tool homes.
- APM target writes for Codex, Claude Code, opencode, or future harnesses need
  explicit approval gates.
- Tool homes such as `~/.codex`, `~/.claude`, and `~/.config/opencode` remain
  local state except for APM-managed target output.
- The active `apm` command should resolve through the Homebrew formula declared
  in the Brewfile. The old manual `/usr/local` APM install was removed on
  2026-07-07 and should not be reintroduced.
- The downside is relying on APM's target behavior and lockfile semantics.
  Doctor must therefore verify both package evidence and deployed baseline
  output.
