# Start with a Minimal Global AI Baseline

Status: accepted.
Date: 2026-06-30.
Amended: 2026-07-07. Reconstructed decision history and ADR quality structure.
Related: ADR-0001, ADR-0002, ADR-0008, ADR-0009,
system/ai/README.md, system/ai/apm/apm.yml,
system/ai/apm/apm.lock.yaml, docs/plans/ai-tooling-stabilization-plan.md.

## Context

This ADR preserves the baseline scope chosen during the AI tooling
stabilization work. The laptop has several AI harnesses and local AI state:
Codex, Claude Code, opencode, Pi, APM, plugin caches, generated skills, command
surfaces, histories, and project-specific configuration.

A broad global baseline would be easy to grow and hard to govern. Skills that
are useful in one project can become distracting or wrong in another. The
global baseline should therefore start with the one workflow Alex explicitly
uses across planning and architecture work: `grill-with-docs`.

APM later materialized that workflow as the public split-skill set
`grill-with-docs`, `grilling`, and `domain-modeling`, but the durable baseline
decision remains one workflow: `grill-with-docs`.

## Decision Drivers

- Global AI assets should be valuable across many repos, not just occasionally
  useful.
- Every global asset increases prompt surface area, maintenance, updates, and
  cross-harness drift risk.
- Project-specific skills should live in project repos or be selected per
  project.
- Sensitive local state and generated caches must not become baseline assets.
- The baseline should be small enough that doctor can verify it clearly.

## Considered Options

- Add every useful skill globally: rejected because it makes the global context
  noisy and moves project-local preferences into laptop policy.
- Include `using-superpowers`: rejected because Alex chose to rebuild the AI
  workflow from scratch and did not want that skill in the baseline.
- Include broad language, framework, or domain skills globally: rejected until
  repeated cross-project use proves they belong on every repo.
- Start with only `grill-with-docs`: selected because it supports planning,
  ADRs, and design review without assuming a project domain.

## Decision

The Global AI Baseline starts with only the `grill-with-docs` workflow.

The approved APM package source currently resolves that workflow through three
public skills:

- `grill-with-docs`
- `grilling`
- `domain-modeling`

Those support files are implementation detail of the selected public package
source. They do not open the door to broad global language, framework, or
project-specific skills.

## Consequences

- `using-superpowers` remains intentionally excluded unless a future ADR
  reverses this decision.
- Pi-specific assets, opencode-specific assets, Claude plugin caches, Codex
  runtime skills, and project-specific prompts are not part of the Global AI
  Baseline.
- Future global assets need a clear promotion test: repeated cross-project use,
  stable package source, no sensitive content, cross-harness value, and doctor
  observability.
- The downside is that new projects may need explicit local AI setup instead of
  inheriting many global helpers. That is intentional until the helpers prove
  they are baseline-worthy.
