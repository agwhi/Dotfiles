# Use fnm As The Node Runtime And JS Toolchain Owner

ADR-0005 says the Development Ecosystem should have one Node runtime owner and
one global JavaScript tool path; this ADR selects `fnm` as that owner for the
stabilization phase. Homebrew remains the Canonical Installer for `fnm`, but
Homebrew `node`, Homebrew `pnpm`, and Homebrew `corepack` are not steady-state
owners. Corepack should come from the selected `fnm` default Node while that
default is a Node version that still distributes Corepack.

This decision remains in force even if `mise` is selected for another runtime
such as `.NET`. The ecosystem prefers the best-fit tool for each runtime over
consolidating everything under one generic runtime manager.

## Considered Options

- Keep `fnm`: selected because it is already declared, installed, configured in
  zsh, and modeled by doctor as the trusted JS scope.
- Replace `fnm` with `mise`: rejected because `fnm` is the better specialized
  Tool Fit for Node in this ecosystem. `mise` may own another runtime without
  becoming the Node owner.
- Use Homebrew `node`: rejected because it gives up project-local Node runtime
  ownership and lets Homebrew upgrades drive the active Node major version.
- Use another specialized Node manager: rejected because no local evidence
  shows a stronger fit than the already-installed `fnm`.

## Consequences

Homebrew `node`, Homebrew `pnpm`, npm globals, and duplicate JS globals become
approval-gated cleanup candidates rather than normal toolchain owners. Doctor
should keep treating Codex/runtime `pnpm` as context only, and future JS recipes
should use `fnm exec --using default` until shell parity is enforced.

If the `fnm` default Node moves to Node 25 or newer, Corepack must be
re-evaluated before the default changes because Corepack is not distributed
with Node 25+.
