# AI Tooling

This directory documents the managed AI Tool Surface model for the Development
Ecosystem. It owns sensitive-safe declarations, templates, generated adapters,
and validation rules. It does not own auth files, histories, local databases,
cache trees, trusted-project state, or vendor runtime state.

## Target Model

APM is the selected AI Asset Manager. The Orchestrator Repo owns APM's
manifest and lockfile, exposes them to `~/.apm` with symlinks, and lets APM
install, audit, and materialize AI Assets for the AI Tool Surfaces that consume
them after sources are declared and target writes are approved.

Homebrew remains the installer for AI app surfaces declared in
`system/packages/Brewfile`, including Codex, ChatGPT, ChatGPT Atlas, and
Ollama. APM manages reusable AI Assets, not every AI binary on the laptop.

The Global AI Baseline is intentionally small:

- `grill-with-docs`

The current APM lockfile pins the public `grill-with-docs` package plus its
public `grilling` and `domain-modeling` dependency skills. Live deployment is
still blocked until a later gate approves target writes and reviews the
generated split-skill layout.

Do not include `using-superpowers`, Pi, opencode, broad language/framework
skills, or project-specific prompts in the global baseline unless a later ADR
promotes them.

## Global Versus Project-Local Assets

Global AI Assets must be useful across projects and reproducible from this
repo. Project-specific prompts, agents, rules, workflows, and tool preferences
belong in the project repos that need them.

Custom AI Assets are normal AI Package Sources. They may come from a Companion
Repo, Git source, local bundle, marketplace, or public package, but they should
flow through the same APM declaration and lock process as third-party assets.

## Shared Asset Strategy

Author each Shared AI Asset once. Let APM generate, install, or link the
tool-specific adapter for Codex, Claude Code, opencode, Pi, or future AI Tool
Surfaces after target writes are approved.

Do not copy the same prompt or skill manually across tool-specific config trees
or keep a repo-owned Codex skill tree as the primary model. If a tool requires
a different format, the adapter is generated output or an explicit
target-specific wrapper, not the source of truth.

## What This Repo Owns

- AI Asset Manager policy and APM project files under `system/ai/apm/`.
- Codex-safe managed configuration and adapters under `system/ai/codex/`.
- Claude-safe managed configuration and adapters under `system/ai/claude/`.
- opencode-safe managed configuration and adapters under `system/ai/opencode/`.
- Shared AI Asset declarations and source mapping under `system/ai/shared/`.
- Manual, local, and approval-gated AI classifications in
  `system/packages/manual-apps.md`.

## What Stays Local

Never commit raw contents from:

- `~/.codex`
- `~/.claude`
- `~/.local/share/claude`
- `~/.local/share/opencode`
- `~/.config/opencode`
- `~/Library/pnpm` AI package state
- app runtime helpers and temporary command wrappers

Extract only redacted, sensitive-safe templates or generated adapters when a
future task explicitly needs them.
