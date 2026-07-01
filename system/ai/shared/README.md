# Shared AI Assets

Shared AI Assets are authored once and adapted for multiple AI Tool Surfaces
when formats differ.

APM is the selected installer and adapter path for shared assets. This directory
should document source packages, target mappings, and sensitive-safe templates,
not hold copied tool-specific cache state.

## Global Baseline

The only target Baseline AI Asset is:

- `grill-with-docs`

The following are intentionally not baseline assets:

- `using-superpowers`
- Pi assets
- opencode assets
- Claude plugin cache contents
- Codex runtime or system skills
- broad language/framework skills
- project-specific prompts, rules, agents, and templates

## Promotion Rule

Keep an asset project-local unless it has repeated cross-project value. When an
asset is promoted, declare its source through APM and map each target surface
explicitly.

## Source Versus Adapter

The source asset is the canonical package or repository. Codex, Claude Code,
opencode, Pi, or other tool-specific files are adapters. Adapters may be
generated output, but they are not the source of truth.

## Sensitive State

Never store tokens, histories, logs, local databases, trusted-project lists,
provider account files, or tool cache trees here. If a tool needs local
credentials, keep them local and document only the redacted shape required for
setup.
