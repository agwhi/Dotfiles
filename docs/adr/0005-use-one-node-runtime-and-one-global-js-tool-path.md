# Use One Node Runtime and One Global JS Tool Path

Status: accepted.
Date: 2026-06-30.
Amended: 2026-07-07. Reconstructed decision history and ADR quality structure.
Refined by: ADR-0007.
Related: ADR-0001, docs/plans/js-toolchain-stabilization-plan.md,
system/packages/Brewfile, system/packages/pnpm-global.txt,
scripts/js_toolchain.sh.

## Context

This ADR preserves the policy decision that the JavaScript toolchain needs one
runtime owner and one global package path. It was created before ADR-0007
selected `fnm` as the concrete owner.

The audit found JavaScript drift across `fnm`, Homebrew `node`, Homebrew
`pnpm`, Corepack visibility, npm globals, pnpm globals, Codex runtime
candidates, and stale Homebrew-prefix global package leftovers. Tools such as
`aws-cdk`, `cdk`, `cdk-dia`, markdownlint, opencode, and Pi made the drift
visible because commands could resolve differently depending on shell context.

The durable policy is broader than any one tool: do not let Node, npm, pnpm,
Corepack, and JavaScript globals have multiple equal owners.

## Decision Drivers

- Project and AI-agent commands need deterministic `node`, `npm`, `npx`, and
  `pnpm` behavior.
- Global JavaScript tools should be declared in a manifest and installed
  through one trusted path.
- Homebrew upgrades should not silently change the active Node major version.
- npm globals should not become an untracked second package manifest.
- Codex/runtime-provided binaries must be treated as execution context, not
  laptop source-of-truth state.

## Considered Options

- One runtime owner plus one package-manager path: selected because it gives
  doctor and bootstrap a clear policy boundary.
- Keep Homebrew `node` plus Homebrew `pnpm` as the simple global path: rejected
  because Homebrew then owns active Node upgrades and project-local Node policy
  becomes weaker.
- Allow npm and pnpm globals side by side: rejected because it makes command
  provenance and cleanup ambiguous.
- Let each AI surface bring its own JavaScript tooling: rejected because app
  runtime context is not a reproducible laptop toolchain.
- Choose the concrete owner in this ADR: deferred to ADR-0007 so the first ADR
  could record the policy before the `fnm` versus `mise` decision was settled.

## Decision

The Development Ecosystem must have one canonical Node runtime owner and one
canonical global JavaScript tool path.

npm globals are prohibited except as temporary migration exceptions or
runtime-owned packages that ship with the selected Node installation. Global
JavaScript tools should be declared through the Orchestrator Repo and installed
through the chosen package-manager path.

ADR-0007 refines this policy by selecting Homebrew-installed `fnm` as the Node
runtime owner and Corepack/pnpm from the selected `fnm` default Node as the
trusted global path.

## Consequences

Existing drift such as npm-global `aws-cdk`, Homebrew `node` competing with
`fnm`, mixed `cdk`/`cdk-dia` resolution, stale Homebrew-prefix Node globals,
and undeclared pnpm packages must be cleaned up behind Reset Approval Gates.

Doctor should distinguish the selected JavaScript owner from Codex runtime
context. Recipes and agent prompts should use `scripts/js_toolchain.sh` or an
explicit selected-runtime command instead of trusting whichever JavaScript
binary appears first in the current process.

The trade-off is less convenience for one-off global installs. New global
JavaScript tools need a manifest change or an explicit temporary-exception
record.
