# Use Dotfiles as the Development Ecosystem Orchestrator

Status: accepted.
Date: 2026-07-07.
Related: docs/adr/README.md, system/packages/Brewfile,
system/packages/README.md, scripts/setup_symlinks.sh, scripts/doctor.py.

## Context

This ADR preserves the foundational decision that already guided the audit and
cleanup work: `/Users/alex/Dev/dotfiles` is the living source of truth for the
laptop's Development Ecosystem.

The repo must support a new-laptop rebuild, ongoing drift detection, and
AI-agent collaboration. Before the audit, development state was split across
Homebrew, language package managers, manual application installs, shell startup
files, AI tool homes, editor state, and symlinks. That made it hard to know
whether an installed tool was intentional, legacy, duplicate, personal, or
missing from the repo.

The decision is not that every byte of development state belongs in this repo.
Some assets have their own lifecycle or sensitivity boundary. Examples include
custom AI assets that may belong in a companion repository, local auth and
history files, generated caches, project-local tooling, and personal apps
tracked through ignored local manifests. The repo still owns the policy,
bootstrap contract, symlink entry points, package manifests, and doctor checks
that make those boundaries explicit.

## Decision Drivers

- A new laptop should be rebuildable from repo-declared package manifests,
  symlink setup, and documented approval gates.
- Development tooling should have one visible source of truth, even when the
  installed files live under Homebrew, language package managers, or tool
  homes.
- AI agents need stable, low-context instructions for how to inspect, mutate,
  validate, and document the development ecosystem.
- Sensitive local state, generated caches, and personal non-development state
  must not be committed just because they are adjacent to development tools.
- Durable tool choices should be recorded as ADRs when they create a policy or
  cleanup boundary future agents must preserve.

## Considered Options

- Keep this as a traditional dotfiles repo only: rejected because symlinks
  alone do not explain package provenance, tool ownership, AI assets, runtime
  managers, or cleanup gates.
- Split every tool family into separate repos: rejected because it would make a
  new-laptop rebuild depend on too many independent sources of truth.
- Keep machine state local and document only what breaks: rejected because it
  preserves the drift problem and gives future agents no reliable baseline.
- Use this repo as the Orchestrator Repo: selected because it can declare,
  link, install, audit, and document the whole development ecosystem while
  still referencing companion sources where they make sense.

## Decision

Use this dotfiles repo as the Development Ecosystem Orchestrator.

The repo owns:

- package manifests and package-manager policy
- symlink setup for repo-managed configuration
- shell, editor, runtime, and AI tool surface policy
- read-only doctor checks and drift classification
- ADRs and plans for durable tool decisions and cleanup gates
- references to companion repos or local-only state where the repo should not
  own the content directly

The repo does not own:

- secrets, tokens, auth stores, histories, sessions, local databases, or caches
- generated tool output unless it is deliberately promoted to source
- project-specific dependencies that belong in project repos
- personal apps that are not part of the development ecosystem

## Consequences

- Package and tool changes should update the repo before, or at the same time
  as, changing the laptop.
- Tools installed outside the repo are drift until classified as canonical,
  personal, project-local, managed exceptions, or approval-gated cleanup
  candidates.
- Companion repos are allowed, but the orchestrator must still declare how
  they are fetched, linked, installed, audited, or intentionally excluded.
- ADRs are required for durable tool choices that establish a Canonical
  Installer, Managed Exception, Stabilizing Replacement, or source-of-truth
  boundary.
- The downside is process overhead: small local experiments should not become
  ADRs or manifests until they become part of the durable ecosystem.
- Future rebuild work should prefer improving manifests, wrappers, doctor, and
  docs over adding undocumented local setup steps.
