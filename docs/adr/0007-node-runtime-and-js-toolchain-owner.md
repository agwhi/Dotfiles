# Use fnm As The Node Runtime And JS Toolchain Owner

ADR-0005 says the Development Ecosystem should have one Node runtime owner and
one global JavaScript tool path; this ADR selects `fnm` as that owner for the
stabilization phase. Homebrew remains the Canonical Installer for `fnm`, but
Homebrew `node`, Homebrew `pnpm`, and Homebrew `corepack` are not steady-state
owners. Corepack should come from the selected `fnm` default Node while that
default is a Node version that still distributes Corepack.

## Considered Options

- Keep `fnm`: selected because it is already declared, installed, configured in
  Nushell, and modeled by doctor as the trusted JS scope.
- Replace `fnm` with `mise`: rejected for now because `mise` is a credible
  Consolidating Tool but would be churn unless Alex chooses to consolidate
  multiple runtimes behind one manager.
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
