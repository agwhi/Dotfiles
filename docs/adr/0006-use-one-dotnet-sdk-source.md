# Use mise as the .NET SDK Source

The Development Ecosystem should expose one canonical `.NET` SDK source across
supported shells. The selected strategic source is `mise`.

Homebrew should install `mise`; `mise` should install and select `.NET` SDKs.
This decision applies to `.NET` only. It does not supersede ADR-0007's `fnm`
decision for Node because this ecosystem prefers the best-fit tool for each
runtime over a generic tool that does everything.

The target SDK policy is:

- .NET 10 as the default SDK line.
- .NET 8 as a temporary compatibility SDK line until remaining projects
  migrate.

The repo-managed global `mise` policy lives at:

```text
system/mise/config.toml
```

`scripts/setup_symlinks.sh` links that file to:

```text
/Users/alex/.config/mise/config.toml
```

Supported shells, editor terminals, and recipes should eventually resolve
`dotnet` through the `mise` shim:

```text
/Users/alex/.local/share/mise/shims/dotnet
```

Tools that need `DOTNET_ROOT` should use the `mise` .NET root:

```text
/Users/alex/.local/share/mise/dotnet-root
```

The Microsoft pkg install under `/usr/local/share/dotnet` remains a root-owned
Managed Exception and approval-gated cleanup candidate. Homebrew `dotnet@8`
was removed on 2026-07-07 after `mise` was verified as the active SDK owner.
The Microsoft pkg root must not be removed until an interactive sudo cleanup
session can verify and remove it from the laptop.

## Considered Options

- `mise`: selected for `.NET` because it can provide side-by-side .NET 10 and
  .NET 8 SDKs under a shared `DOTNET_ROOT` and supports project-level
  selection.
- Microsoft pkg: kept as a migration source and fallback because it is the
  current zsh/Codex active SDK, but rejected as canonical because it is not
  managed by the repo as a runtime owner.
- Homebrew casks `dotnet-sdk` and `dotnet-sdk@8`: viable fallback because they
  wrap Microsoft's pkg layout, but not selected because the desired long-term
  owner is a runtime manager rather than cask-managed pkg state.
- Homebrew formula `dotnet` plus `dotnet@8`: rejected because versioned
  formulae live in separate Homebrew roots, which is a weaker fit for .NET 10
  default plus .NET 8 compatibility.
- `asdf`: rejected because `.NET` support is plugin-based and requires more
  shell-specific environment handling than `mise` for this repo.

## Consequences

`.NET` global tools are user-local state under `/Users/alex/.dotnet/tools`, not
files installed under the SDK source. They should still be declared in a Package
Manifest and installed or updated through the canonical `mise`-managed
`dotnet`.

Repo automation should run .NET commands through:

```text
scripts/dotnet_toolchain.sh
```

That wrapper requires `mise` and the repo-managed config. It must fail clearly
when `mise` or the SDKs are absent instead of silently using Microsoft pkg .NET
or Homebrew `dotnet@8`.

Bootstrap has an explicit SDK step before global tool installation:

```text
Homebrew installs mise -> mise installs SDKs -> wrapper installs global tools
```

The SDK step is `install-dotnet-sdks`, which runs
`scripts/dotnet_sdk_install.sh`. That script is intentionally mutating when
executed: it locates `mise`, requires `system/mise/config.toml`, sets
`MISE_GLOBAL_CONFIG_FILE` to that repo-managed config, and installs only the
declared `dotnet` SDK lines through `mise`. It does not fall back to Microsoft
pkg .NET or Homebrew `dotnet@8`.

`setup-dotnet` must keep the order `install-dotnet-sdks` before
`install-dotnet-tools` so global tools are installed through the ADR-0006 SDK
source rather than a migration exception.

The installer surface for global tools is a separate implementation decision:
the repo may keep using `dotnet tool install --global` through the
`mise`-managed SDK, or it may use `mise`'s `dotnet:ToolName` backend where that
gives better reproducibility. Do not remove or migrate existing user-local
tools until that choice is documented.

`doctor` should report active `.NET` source, candidate paths, SDKs, runtimes,
workloads, global tool package drift, and global tool command visibility before
any SDK source is removed behind a Reset Approval Gate.

The selected source is a strategic replacement, so implementation is gated:
installing `mise`, installing .NET 10 and .NET 8 through `mise`, changing shell
activation, changing editor discovery, and removing existing SDK sources are
separate approved steps.

`mise` becoming the `.NET` owner is not evidence that Node should move away
from `fnm`. Node remains governed by ADR-0007 unless a later Node-specific ADR
finds that another specialized Node owner has better Tool Fit.
