# Use mise As The .NET SDK Source

Status: accepted.
Date: 2026-07-01.
Amended: 2026-07-07. Reconstructed decision history and ADR quality structure.
Related: ADR-0001, ADR-0007,
docs/plans/dotnet-sdk-stabilization-plan.md, system/mise/config.toml,
system/packages/Brewfile, system/packages/dotnet-tools.txt,
scripts/dotnet_snapshot.sh, scripts/dotnet_sdk_install.sh,
scripts/dotnet_toolchain.sh, scripts/setup_symlinks.sh.

## Context

The .NET audit found multiple SDK sources with different ownership models:
Microsoft pkg state under `/usr/local/share/dotnet`, Homebrew `dotnet@8`, and
the proposed `mise` runtime-manager path. The laptop needed .NET 10 for new
work while keeping .NET 8 available for compatibility projects.

This ADR records the .NET runtime-owner decision only. It does not standardize
all runtimes on `mise`; ADR-0007 keeps `fnm` as the specialized Node owner.
The repo's policy is best-fit runtime ownership, not generic consolidation.

As of 2026-07-07, `dotnet` resolves through the `mise` shim,
`dotnet --list-sdks` shows `8.0.422` and `10.0.301` from the `mise` .NET
root, Homebrew `dotnet@8` has been removed, and the Microsoft pkg SDK source
root under `/usr/local/share/dotnet` has been removed. Stale Microsoft pkg
receipts may still be visible through `pkgutil`, but they are not an active SDK
source.

## Decision Drivers

- .NET 10 should be the default SDK line for new work.
- .NET 8 should remain available until compatibility projects migrate.
- Shells, editor terminals, `just` recipes, and AI command contexts should see
  the same SDK source.
- Global .NET tools should be installed through the selected SDK context, not
  whichever `dotnet` happens to be first on PATH.
- The selected SDK source should be declared in this repo and verifiable by
  doctor without reading sensitive state.
- Existing root-owned SDK sources should be removed only behind explicit
  approval and snapshots.

## Considered Options

- `mise`: selected because it can install .NET 10 and .NET 8 side by side under
  a shared `DOTNET_ROOT`, supports project-level runtime selection, and gives
  this repo one runtime-manager boundary for .NET.
- Microsoft pkg shared root: rejected as canonical because it is manual/pkg
  state outside the repo package manifests and required receipt/root-owned
  cleanup during migration.
- Homebrew casks `dotnet-sdk` and `dotnet-sdk@8`: rejected as the primary
  owner because they wrap pkg-style state under `/usr/local/share/dotnet`
  rather than a repo-managed runtime-manager root.
- Homebrew formula `dotnet` plus `dotnet@8`: rejected because versioned
  formulae live in separate Homebrew roots, which makes side-by-side SDK and
  `DOTNET_ROOT` policy less clean.
- `asdf`: rejected because .NET support is plugin-based and has weaker local
  Tool Fit than `mise` for this repo.

## Decision

Homebrew installs `mise`; `mise` installs and selects .NET SDKs.

The repo-managed global `mise` policy lives at `system/mise/config.toml` and is
linked to `~/.config/mise/config.toml` by `scripts/setup_symlinks.sh`.

The target SDK policy is:

- .NET 10 as the default SDK line.
- .NET 8 as a temporary compatibility SDK line.

Automation must use `scripts/dotnet_toolchain.sh` or an explicit `mise`
context for .NET commands. SDK installation must go through
`scripts/dotnet_sdk_install.sh`, which reads the repo-managed `mise` config.
Pre-migration snapshots are written by `scripts/dotnet_snapshot.sh` to ignored
local reports.

.NET global tools are user-local state under `/Users/alex/.dotnet/tools`.
They are declared separately in `system/packages/dotnet-tools.txt` and should
be installed through the canonical `mise`-managed `dotnet`.

## Consequences

- Doctor can verify .NET source, SDK lines, global tools, and shell parity
  against one declared policy.
- Homebrew `dotnet@8`, Microsoft pkg .NET, and ad hoc global tools are not
  steady-state owners.
- Project compatibility should be expressed with project-local .NET config or
  `global.json`, not by relying on old global SDK roots.
- The downside is additional `mise` activation and shim behavior to maintain.
  Shell, editor, and AI command contexts must keep the `mise` shim path and
  `DOTNET_ROOT` aligned.
- Removing stale Microsoft pkg receipts remains out of scope unless they create
  installer or doctor-visible drift.
