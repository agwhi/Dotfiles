# Use fnm As The Node Runtime And JS Toolchain Owner

Status: accepted.
Date: 2026-07-01.
Amended: 2026-07-07. Reconstructed decision history and ADR quality structure.
Refines: ADR-0005.
Related: ADR-0001, ADR-0005,
docs/plans/js-toolchain-stabilization-plan.md, system/packages/Brewfile,
system/packages/pnpm-global.txt, scripts/js_toolchain.sh.

## Context

ADR-0005 established the policy that the Development Ecosystem should have one
Node runtime owner and one global JavaScript tool path. This ADR records the
concrete owner decision: keep `fnm`.

The JavaScript stabilization plan records the local evidence. `fnm` is declared
in the Brewfile, installed through Homebrew, configured by repo-managed zsh
startup, and modeled by doctor as the trusted JavaScript scope. The selected
default Node exposes `node`, `npm`, `npx`, `pnpm`, and Corepack through the
`fnm` path.

`mise` was considered seriously because it is now the .NET SDK owner, but this
repo prefers specialized best-fit tools over generic consolidation when the
specialized tool is already working.

## Decision Drivers

- Preserve the existing specialized Node manager when it already satisfies the
  policy from ADR-0005.
- Keep Homebrew as the installer for `fnm`, not as the owner of active Node.
- Keep Corepack and pnpm tied to the selected `fnm` default Node while that
  Node version distributes Corepack.
- Give AI agents an explicit command path that avoids Codex/runtime pnpm
  ambiguity.
- Avoid replacing working Node infrastructure only to consolidate with `mise`.

## Considered Options

- Keep `fnm`: selected because it is already declared, installed, configured,
  and trusted by doctor.
- Replace `fnm` with `mise`: rejected because `fnm` is the better specialized
  Tool Fit for Node here. `mise` can own .NET without becoming the Node owner.
- Use Homebrew `node`: rejected because it lets Homebrew upgrades drive the
  active Node major version and weakens project-local runtime switching.
- Introduce another Node manager such as `volta`, `nvm`, or `nodenv`: rejected
  because no local evidence showed a stronger fit than `fnm`.

## Decision

Use Homebrew-installed `fnm` as the Node runtime and JavaScript toolchain owner.

Homebrew `node`, Homebrew `pnpm`, and Homebrew `corepack` are not steady-state
owners. Corepack should come from the selected `fnm` default Node while that
Node version distributes Corepack. Global JavaScript tools belong in
`system/packages/pnpm-global.txt` and should be installed through the trusted
`fnm`/pnpm path.

Repo recipes and agent workflows should prefer `scripts/js_toolchain.sh` or an
explicit `fnm exec --using default ...` command when JavaScript toolchain
provenance matters.

## Consequences

- Duplicate Homebrew Node/pnpm packages and npm globals are approval-gated
  cleanup candidates, not alternative owners.
- Codex/runtime-provided JavaScript binaries may appear in execution contexts
  but must not be treated as laptop source-of-truth state.
- The upside is low migration cost and a deterministic specialized Node path.
- The downside is keeping more than one runtime manager in the ecosystem:
  `fnm` for Node and `mise` for .NET.
- If the `fnm` default Node moves to Node 25 or newer, Corepack must be
  re-evaluated before the default changes because Corepack distribution changes
  at that boundary.
