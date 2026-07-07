# Shared AI Assets

Shared AI Assets are authored once and adapted for multiple AI Tool Surfaces
when formats differ.

APM is the selected package discovery, lock, audit, and materialization path
for shared assets. This directory should document source packages, target
mappings, and sensitive-safe templates, not hold copied tool-specific cache
state.

## Global Baseline

The only target Baseline AI Asset is:

- `grill-with-docs`

Current source status: `system/ai/apm/apm.yml` and `apm.lock.yaml` pin the
public `grill-with-docs` wrapper plus the public dependency skills it invokes:

- `mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1`
- `mattpocock/skills/skills/productivity/grilling#v1.0.1`
- `mattpocock/skills/skills/engineering/domain-modeling#v1.0.1`

Scratch validation on 2026-07-03 showed that `grilling` lives under
`skills/productivity/grilling`, not `skills/engineering/grilling`. The frozen
scratch install generated `grill-with-docs`, `grilling`, and
`domain-modeling`, and it did not generate `using-superpowers`.

Live Codex, Claude Code, and opencode deployments have materialized the split
baseline. opencode receives the shared skills under
`~/.config/opencode/skills`.

The following are intentionally not baseline assets:

- `using-superpowers`
- Pi-specific assets, unless a future APM Pi target policy promotes them
- Claude plugin cache contents
- Codex runtime or system skills
- broad language/framework skills
- project-specific prompts, rules, agents, and templates

## Promotion Rule

Keep an asset project-local unless it has repeated cross-project value. When an
asset is promoted, declare its package source through APM and map each target
surface explicitly.

The Orchestrator Repo exposes APM's project files through `~/.apm` symlinks;
APM should own generated modules and target output after target writes are
approved.

## Source Versus Adapter

The source asset is the canonical package or repository consumed by APM. Codex,
Claude Code, opencode, future Pi adapters, or other tool-specific files are
adapters. Generated adapters are not source of truth.

Skills, commands, agents, MCP definitions, and similar shared AI assets should
be declared as APM package dependencies before they are deployed to any tool.

## Sensitive State

Never store tokens, histories, logs, local databases, trusted-project lists,
provider account files, or tool cache trees here. If a tool needs local
credentials, keep them local and document only the redacted shape required for
setup.
