# Treat Custom AI Assets as Normal AI Package Sources

Status: accepted.
Date: 2026-06-30.
Amended: 2026-07-07. Reconstructed decision history and ADR quality structure.
Refined by: ADR-0008, ADR-0009.
Related: ADR-0001, ADR-0003, ADR-0008, ADR-0009,
system/ai/README.md, system/ai/apm/README.md,
system/ai/apm/apm.yml, system/ai/apm/apm.lock.yaml.

## Context

This ADR preserves the AI asset boundary established during the AI tooling
audit. Alex wants an AI-native development setup where Codex, Claude Code,
opencode, Pi, and future harnesses can reuse shared skills, commands, prompts,
and MCP-style configuration where possible.

At the same time, custom AI work should not be forced into dotfiles just
because this repo orchestrates the laptop. Custom skills, prompts, agents,
templates, and workflow artifacts may deserve their own versioning, release
history, and project ownership. Sensitive local AI state such as auth, histories,
sessions, trusted-project data, local databases, and provider configuration
must stay out of git.

The important policy is that custom and third-party AI assets are treated the
same way once selected: they must come through a declared AI asset flow, not
manual per-tool copies.

## Decision Drivers

- Shared AI assets should be reusable across harnesses instead of copied into
  each tool's home directory by hand.
- Custom AI assets may need a different repository lifecycle from dotfiles.
- Third-party and custom assets should have equivalent provenance, lock, and
  install behavior once accepted into the Global AI Baseline.
- Sensitive AI state must remain local or ignored, not committed to make a
  rebuild easier.
- Project-specific AI assets should live with the project that needs them.

## Considered Options

- Store all custom AI assets directly in dotfiles: rejected because it couples
  personal AI asset development to laptop setup and risks mixing reusable
  content with machine orchestration.
- Keep custom AI assets as unmanaged local installs: rejected because it makes
  rebuilds and cross-harness reuse non-reproducible.
- Copy assets separately into Codex, Claude, opencode, and Pi homes: rejected
  because it creates drift between harnesses.
- Treat custom repositories as normal AI package sources: selected because the
  orchestrator can declare the package source while the custom repo retains its
  own lifecycle.

## Decision

Custom AI assets may live outside this repo, including in Alex-owned companion
repositories, but they must be consumed through the same declared AI Asset
Manager flow as third-party assets when they become part of the laptop-wide
baseline.

The Orchestrator Repo declares only the Global AI Baseline and the install,
lock, symlink, or deployment mechanism. It does not need to own the source code
for every custom AI asset.

Sensitive local state stays out of git. If a sensitive template or local config
is needed later, it should be represented as a redacted template, ignored file,
or documented manual step rather than committed values.

## Consequences

- ADR-0008 can choose APM as the AI Asset Manager without requiring all custom
  assets to move into this repo.
- ADR-0009 can expose repo-owned APM project files to `~/.apm` while package
  content remains resolved through APM sources.
- Public skills, marketplace packages, Git refs, local bundles, and custom
  companion repos are all valid package source categories once declared.
- The Global AI Baseline remains intentionally small until an asset has repeated
  cross-project value and a reproducible package source.
- The downside is an extra layer of indirection: future agents must inspect the
  APM manifest and lockfile, not just tool home directories, to understand the
  baseline.
