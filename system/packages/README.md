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

Current steady state is `dotnet` resolving through
`/Users/alex/.local/share/mise/shims/dotnet`, with SDKs `8.0.422` and
`10.0.301` visible from `/Users/alex/.local/share/mise/dotnet-root/sdk`.
Declared global tools from `system/packages/dotnet-tools.txt` are installed.

Bootstrap and rebuild order remains: Homebrew installs `mise`,
`install-dotnet-sdks` installs the declared SDK lines through
`scripts/dotnet_sdk_install.sh`, and then `install-dotnet-tools` installs
global tools through `scripts/dotnet_toolchain.sh`. The SDK installer is
explicitly mutating when run, requires the repo-managed
`system/mise/config.toml`, and does not fall back to Microsoft pkg .NET or
Homebrew `dotnet@8`.

Homebrew `dotnet@8` and the Microsoft pkg SDK source root under
`/usr/local/share/dotnet` were removed on 2026-07-07 after `mise` was verified
as canonical. Stale Microsoft pkg receipts may remain visible through
`pkgutil`, but no legacy SDK source path is present and doctor reports `.NET`
source state as canonical.

## Editor Extensions

`system/packages/vscode-extensions.txt` is the single owner for VS Code
extensions. They install via `just install-vscode-extensions` (part of
bootstrap), and doctor audits against the same file. Do not declare `vscode`
entries in the Brewfile: that would create a second owner and a double
install path through `brew bundle`.

## Manual And Approval-Gated State

Use `system/packages/manual-apps.md` for manual tools, managed exceptions,
intentional exclusions, and removal candidates that need a Reset Approval Gate.
This keeps installed local state visible without turning cleanup into an
implicit install or uninstall instruction.

## Personal Local Packages

Use `system/packages/personal.Brewfile` for non-development personal apps that
should remain installed on this laptop but should not become part of the
Development Ecosystem baseline. This file is gitignored. Example entries:

```ruby
cask "whatsapp"
```

Install or check it explicitly:

```sh
just install-personal-brew
just check-personal-brew
brew bundle --file=system/packages/personal.Brewfile
brew bundle check --file=system/packages/personal.Brewfile --verbose
```

Do not include MDM/security-managed software such as Falcon in this personal
manifest unless ownership is explicitly confirmed.

`brew bundle cleanup --file=system/packages/Brewfile` only knows about the
development baseline, so it may report personal casks from this ignored file as
cleanup candidates. Do not run that cleanup with `--force` unless personal
casks have been reviewed separately.

## Read-only Doctor

Run `just doctor` from the repo root to audit installed tools against these
manifests without changing the machine. The doctor reports drift and install
provenance only; it does not install, uninstall, migrate, back up, start
services, or rewrite files.

The default human output is concise: it says the ecosystem is ready when there
are no actionable findings, otherwise it prints only the actionable issues.
Use `just doctor --all` for the full read-only audit inventory.

Use `just doctor --json` when another agent or script needs structured output.
