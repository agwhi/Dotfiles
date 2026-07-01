# Package Manifests

This directory declares installable software for the Development Ecosystem.
Keep manifests declarative and one-purpose; bootstrap and doctor logic should
consume these files rather than embedding desired package lists.

## JavaScript Toolchain

`system/packages/Brewfile` declares Homebrew as the installer for `fnm` only.
Per ADR-0007, `fnm` owns the Node runtime, and Corepack/pnpm should be reached
through the selected `fnm` default Node path. Global JavaScript tools belong in
`system/packages/pnpm-global.txt` and are installed by `just install-node-tools`.

Homebrew `node` and Homebrew `pnpm` are not steady-state owners. If they are
present locally, treat them as approval-gated cleanup candidates until shell
parity and global tool paths are verified.

## .NET Toolchain

Per ADR-0006, Homebrew declares `mise` as the strategic .NET SDK manager.
`system/mise/config.toml` declares .NET 10 as the default SDK line and .NET 8
as the compatibility line, and `scripts/setup_symlinks.sh` links it to
`~/.config/mise/config.toml`.

Bootstrap order is Homebrew installs `mise`, `install-dotnet-sdks` installs the
declared SDK lines through `scripts/dotnet_sdk_install.sh`, and then
`install-dotnet-tools` installs global tools through
`scripts/dotnet_toolchain.sh`. The SDK installer is explicitly mutating when
run, requires the repo-managed `system/mise/config.toml`, and does not fall
back to Microsoft pkg .NET or Homebrew `dotnet@8`.

The SDK install recipe should run only as a later approved migration step.
Existing Microsoft pkg .NET and Homebrew `dotnet@8` remain managed exceptions
until the `mise` SDK root, editor discovery, workloads, and global tools are
verified.

## Manual And Approval-Gated State

Use `system/packages/manual-apps.md` for manual tools, managed exceptions,
intentional exclusions, and removal candidates that need a Reset Approval Gate.
This keeps installed local state visible without turning cleanup into an
implicit install or uninstall instruction.

## Read-only Doctor

Run `just doctor` from the repo root to audit installed tools against these
manifests without changing the machine. The doctor reports drift and install
provenance only; it does not install, uninstall, migrate, back up, start
services, or rewrite files.

Use `just doctor --json` when another agent or script needs structured output.
