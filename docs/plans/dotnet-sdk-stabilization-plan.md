# .NET SDK Stabilization Plan

Date: 2026-07-01.

This plan is non-mutating. It does not install, uninstall, relink, unlink,
upgrade, repair, or remove any .NET SDK, runtime, workload, global tool, or
Homebrew formula. It records the canonical source decision and the approval
gates needed before any cleanup.

## Decision

Use `mise` as the strategic `.NET` SDK owner for the Development Ecosystem.
Homebrew should install `mise`; `mise` should install and select `.NET` SDKs.
This is not a general runtime-consolidation decision. The ecosystem should pick
the best-fit tool for each runtime; ADR-0007 keeps `fnm` as the Node owner.

Target SDK set:

- .NET 10 as the default SDK line for new work.
- .NET 8 as a temporary compatibility SDK line for projects that have not yet
  migrated.

Confidence: medium-high. This is more change than keeping the current Microsoft
pkg install, but it matches the desired future: a repo-managed runtime owner
that can expose .NET 10 by default, keep .NET 8 side-by-side, and later remove
the compatibility SDK when projects migrate.

The current Microsoft pkg install and Homebrew `dotnet@8` formula remain
Managed Exceptions and approval-gated cleanup candidates. They must not be
removed until the `mise` SDK root, shell activation, editor discovery, workloads,
global tools, and project-level SDK selection are verified.

## Evidence

Local command evidence collected on 2026-07-01:

- `which -a dotnet` in the zsh/Codex context returns only
  `/usr/local/share/dotnet/dotnet`.
- Active Microsoft pkg SDK: `8.0.412` at `/usr/local/share/dotnet/sdk`.
- Active Microsoft pkg runtimes: `Microsoft.AspNetCore.App 8.0.18` and
  `Microsoft.NETCore.App 8.0.18`.
- Active Microsoft pkg workloads: none.
- Microsoft pkg receipts include
  `com.microsoft.dotnet.dev.8.0.412.component.osx.arm64` and runtime receipts
  under `usr/local/share/dotnet`.
- Homebrew `dotnet@8` is installed on request and declared in
  `system/packages/Brewfile`.
- Homebrew `dotnet@8` version: `8.0.128`.
- Direct Homebrew `dotnet@8` SDK: `8.0.128` at
  `/opt/homebrew/Cellar/dotnet@8/8.0.128/libexec/sdk`.
- Direct Homebrew `dotnet@8` runtimes: `Microsoft.AspNetCore.App 8.0.28` and
  `Microsoft.NETCore.App 8.0.28`.
- Direct Homebrew `dotnet@8` workload list reports `aspire 8.2.2/8.0.100`
  from user-local workload manifests under
  `/Users/alex/.dotnet/sdk-manifests/8.0.100`.
- Homebrew formula metadata reports `dotnet` as `10.0.301`, alias
  `dotnet@10`, but it is not installed.
- Homebrew cask metadata reports `dotnet-sdk` as `10.0.301` and
  `dotnet-sdk@8` as `8.0.422`, but neither cask is installed.
- Homebrew formula metadata reports `mise` as available but not installed.
- `system/packages/Brewfile` now declares `mise` as the strategic .NET SDK
  owner and keeps Homebrew `dotnet@8` as a managed migration exception.
- Repo-managed `mise` policy now lives at `system/mise/config.toml`, is linked
  to `~/.config/mise/config.toml` by `scripts/setup_symlinks.sh`, and declares
  .NET 10 plus .NET 8 without declaring Node.
- `scripts/dotnet_toolchain.sh` is the canonical wrapper for .NET commands; it
  requires `mise` and does not silently fall back to Homebrew `dotnet@8`.
- `scripts/dotnet_sdk_install.sh` is the explicit mutating SDK installer that
  should run only after Homebrew has installed `mise`; it uses
  `system/mise/config.toml` via `MISE_GLOBAL_CONFIG_FILE`.
- `scripts/dotnet_snapshot.sh` is the read-only pre-migration snapshot command.
  It writes local reports to `reports/dotnet-migration-snapshot-<timestamp>.md`.
- `dotnet-snapshot` recipes exist in both `justfile` and
  `system/global-justfile`, and `install-dotnet-sdks` depends on the snapshot
  recipe before running the mutating SDK installer.
- No `.csproj`, `.fsproj`, `.vbproj`, `.sln`, `global.json`, `.props`, or
  `.targets` files exist in this repo.
- Installed global tools are user-local packages:
  `amazon.lambda.testtool`, `amazon.lambda.testtool-8.0`, `csharpier`,
  `deadcsharp`, and `dotnet-ef`.
- `system/packages/dotnet-tools.txt` declares only `Amazon.Lambda.Tools` and
  `Amazon.Lambda.TestTool-8.0`; `Amazon.Lambda.Tools` is currently absent.
- Global tool shims exist in `/Users/alex/.dotnet/tools`, and the shell/dev
  environment contract now uses the expanded path rather than a literal tilde.

External source context:

- Microsoft's lifecycle policy lists .NET 10 as LTS through 2028-11-14 and
  .NET 8 as supported through 2026-11-10:
  <https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core>
- Microsoft's macOS install docs describe the SDK as including both the
  standard .NET Runtime and ASP.NET Core Runtime:
  <https://learn.microsoft.com/en-us/dotnet/core/install/macos>
- Microsoft's .NET global tools docs state that global tool binaries default
  to `$HOME/.dotnet/tools` on Linux/macOS and are user-specific:
  <https://learn.microsoft.com/en-us/dotnet/core/tools/global-tools>
- `mise` .NET docs describe installing SDKs through Microsoft's install script
  under a shared `DOTNET_ROOT`, with side-by-side SDK visibility:
  <https://mise.jdx.dev/lang/dotnet.html>
- `mise` .NET docs also describe a `dotnet:ToolName` backend for .NET global
  tools, so global tool installation policy must be decided separately from SDK
  ownership:
  <https://mise.jdx.dev/lang/dotnet.html>
- Homebrew formula metadata reports `mise` as a polyglot runtime manager:
  <https://formulae.brew.sh/formula/mise>

## Decision Matrix

<!-- markdownlint-disable MD013 -->

| Option | Strengths | Weaknesses | Verdict |
| --- | --- | --- | --- |
| `mise` .NET | Strategic .NET owner that can install .NET 10 and .NET 8 side-by-side under a shared `DOTNET_ROOT` and supports project-level runtime selection. | Not installed yet, requires shell activation, doctor policy, editor-terminal parity, and migration from current SDK sources. | Select as the .NET strategic replacement. |
| Microsoft pkg shared root | Native .NET side-by-side behavior, currently active, and compatible with .NET 10 plus .NET 8 overlap through pkg/cask installs. | Manual/pkg state is already outside the Brewfile, cleanup is receipt/root-owned, and project-level runtime ownership would remain less explicit than `mise`. | Keep as migration source and fallback until `mise` is proven. |
| Homebrew casks `dotnet-sdk` plus `dotnet-sdk@8` | Repo-installable wrapper around Microsoft's pkg layout and supports .NET 10 plus .NET 8 overlap. | Still lands in `/usr/local/share/dotnet`, not a runtime-manager root; Homebrew cask upgrade/removal behavior needs careful gates. | Use only as fallback if `mise` is rejected during implementation. |
| Homebrew formula `dotnet` plus `dotnet@8` | Formula `dotnet` provides .NET 10 and `dotnet@8` is already installed. | Versioned formulae live in separate Homebrew roots, making side-by-side SDK discovery and `DOTNET_ROOT` policy less clean. | Reject as the canonical owner. |
| `asdf` .NET plugin | Can manage .NET through a runtime-manager ecosystem. | Plugin-based, shell-specific `DOTNET_ROOT` setup, and weaker local Tool Fit than `mise`. | Reject unless a future ADR standardizes on `asdf`. |

<!-- markdownlint-enable MD013 -->

## Compatibility Conclusion

`mise` is the best target for the revised requirement: move to .NET 10 while
keeping .NET 8 projects working during migration.

The reason is not that the current Microsoft pkg install is broken. It is
because the ecosystem wants a strategic .NET owner. `mise` gives the repo a
clear .NET runtime-manager boundary:

- Homebrew installs `mise`.
- `mise` installs .NET SDK lines.
- `system/mise/config.toml` selects the global default once linked to
  `~/.config/mise/config.toml`.
- Project-local config or `global.json` can pin .NET 8 where needed.
- Doctor can verify that active `dotnet`, `DOTNET_ROOT`, SDK list, runtime
  list, and workloads come from the selected owner.

This does not change the Node decision. `fnm` remains the best-fit specialized
Node owner unless a later Node-specific decision proves otherwise.

The current Microsoft pkg install should stay in place until `mise` proves:

- .NET 10 is available as the default SDK.
- .NET 8 is available for compatibility projects.
- .NET 8 projects can build/test without relying on `/usr/local/share/dotnet`.
- Workloads such as Aspire remain visible where needed.
- Global tools are invokable from every supported shell.
- Editors discover the intended SDK root.

## Shell And Path Policy

Target `dotnet` path:

```text
/Users/alex/.local/share/mise/shims/dotnet
```

Target `DOTNET_ROOT`:

```text
/Users/alex/.local/share/mise/dotnet-root
```

Target global tool path:

```text
/Users/alex/.dotnet/tools
```

zsh/Codex:
Repo-managed zsh startup and `scripts/dev_env.sh` now prepend the `mise` shims
directory when it exists and set `DOTNET_ROOT` only when the expected `mise`
.NET root exists. This is safe before `mise` is installed, but once the shims
exist they should win over Homebrew `dotnet@8`. Plain `dotnet` still remains
migration-pending until the SDKs are installed through `mise`.

Just recipes:
Current recipes route .NET global tool installs through
`scripts/dotnet_toolchain.sh`, which runs under the ADR-0006 `mise` context.
Migration order is explicit: `dotnet-snapshot` captures the current local
state, Homebrew installs `mise`, symlink setup links the repo-managed
`system/mise/config.toml`, `install-dotnet-sdks` installs the declared SDK
lines through `mise`, `setup-dotnet` installs approved global tools through
that SDK context, and then doctor plus editor-terminal checks verify parity.
Compatibility projects should pin their SDK instead of relying on a global
shell default.

Snapshot artifacts:
`just dotnet-snapshot` writes
`reports/dotnet-migration-snapshot-<timestamp>.md`. The `reports/` directory is
gitignored because snapshots contain local machine state and should stay
local-only unless Alex deliberately chooses to publish a sanitized excerpt.

Editor terminals:
VS Code, Cursor, and other editor terminals should resolve the same `mise`
`dotnet` and `DOTNET_ROOT` as the shell. Do not remove existing SDK sources
until C# extension discovery, SDK listing, and terminal `dotnet --info` match
the target owner.

Automation:
Automation must not assume interactive shell startup has run. Use
`scripts/dotnet_toolchain.sh` or explicit `mise exec` commands for .NET
automation.

## Global Tool Policy

`.NET` global tools are user-local development state installed under
`/Users/alex/.dotnet/tools`. They should not be treated as installed under the
selected SDK source. The selected SDK owner is the installer/runner used to
manage them.

There is still an implementation choice to make: keep the current
`system/packages/dotnet-tools.txt` manifest as input to
`dotnet tool install --global` through the `mise`-managed SDK, or migrate global
tool declarations to `mise`'s `dotnet:ToolName` backend. Do not migrate or
remove existing global tools until that choice is explicit.

Keep `system/packages/dotnet-tools.txt` as the Package Manifest for approved
global tools. Future installs or updates should run through the canonical
`mise`-managed .NET SDK after shell parity is fixed.

`setup-dotnet` depends on `install-dotnet-sdks` before `install-dotnet-tools`.
That makes the bootstrap path clear, but validation of this readiness work must
use `just --dry-run` only unless the mutation is explicitly approved.

Current decisions:

- Keep `Amazon.Lambda.TestTool-8.0` declared while .NET 8 projects remain.
- Keep `Amazon.Lambda.Tools` declared, but install it only after SDK ownership
  is stable.
- Treat `dotnet-ef` as approval-gated for removal unless Alex confirms EF Core
  tooling is part of the baseline.
- Treat `amazon.lambda.testtool`, `csharpier`, and `deadcsharp` the same way:
  declare them if they are intentional baseline tools, otherwise remove them
  only after explicit approval.
- Fix global tool command visibility before using tool presence as proof that a
  workflow is healthy.

## Cleanup Gates

Before installing or activating `mise` for `.NET`:

- Run `just dotnet-snapshot` to capture a Rebuild Snapshot of current
  `dotnet --info`, `--list-sdks`, `--list-runtimes`, `workload list`,
  `tool list --global`, relevant PATH entries, `DOTNET_ROOT`, pkg receipts,
  Homebrew formula state, and managed path presence.
- Keep `system/packages/Brewfile` and `system/mise/config.toml` as the
  repo-managed declarations.
- Keep `dotnet = ["10", "8"]` as the SDK selector policy unless a later ADR
  changes the default or compatibility line.
- Decide how `global.json` should be handled in compatibility projects.

Before making `mise` active in shells:

- Prove `mise` installs and lists the target .NET 10 and .NET 8 SDKs.
- Prove `DOTNET_ROOT` points to the `mise` .NET root.
- Prove `dotnet --list-sdks` sees both SDK lines from the `mise` root.
- Prove zsh login, zsh non-login, Codex, VS Code terminal, Cursor terminal, and
  AI command surfaces resolve the `mise` `dotnet`.
- Prove editor C# tooling discovers the `mise` SDK root.
- Prove global tool commands are invokable from supported shells.

Before removing the Microsoft pkg install:

- Prove no active project, editor, or Lambda workflow depends on
  `/usr/local/share/dotnet`.
- Prove .NET 8 compatibility projects build/test through `mise`.
- Confirm that removing `/usr/local/share/dotnet` and Microsoft pkg receipts is
  acceptable, then perform the removal only with explicit approval.

Before removing Homebrew `dotnet@8`:

- Prove no shell, editor, recipe, workload, or project uses
  `/opt/homebrew/opt/dotnet@8`.
- Update the Brewfile and doctor policy to stop expecting Homebrew `dotnet@8`.
- Perform `brew uninstall dotnet@8` only with explicit approval.

Before removing or changing global tools:

- Decide whether each installed undeclared tool is baseline, Managed Exception,
  migrated project-local tooling, or cleanup.
- Add intentional tools to `system/packages/dotnet-tools.txt` before using
  doctor to enforce them.
- Remove tools only after explicit approval because tool removal changes
  user-local development state.

## Implementation Plan

1. Record the `mise` strategic replacement decision in ADR-0006. Done.
2. Keep the doctor read-only and make `.NET` source, candidate paths, SDKs,
   runtimes, workloads, global tool packages, and global tool command path
   visibility observable. Done for the first readiness slice.
3. Add Homebrew `mise` to the package manifest and add a repo-managed `mise`
   SDK version policy. Done.
4. Add a `.NET` wrapper and recipes that use the `mise` context without
   mutating the laptop during validation. Done.
5. Add an explicit `install-dotnet-sdks` recipe that installs the ADR-0006 SDK
   lines through `mise` only when deliberately run. Done.
6. Add a read-only `dotnet-snapshot` recipe before the SDK install recipe and
   keep generated snapshot reports local-only. Done.
7. Next approved order: run `dotnet-snapshot`, install and link `mise`, install
   SDKs, run `setup-dotnet`, then verify doctor plus editor terminals.
8. Install .NET 10 and .NET 8 through `mise` in a later approved mutation step
   by running `install-dotnet-sdks` after Homebrew installs `mise`.
9. Activate `mise` in zsh/Codex and editor terminals after install.
10. Re-run doctor and shell checks from zsh, Codex, VS Code, Cursor, and AI
   command surfaces.
11. Decide whether .NET global tools stay as `dotnet tool --global` installs or
   move to `mise` `dotnet:ToolName` declarations.
12. Decide global tool manifest changes for `dotnet-ef`, `csharpier`,
   `deadcsharp`, and the legacy Lambda test tool package.
13. Only after all gates pass, ask for explicit approval to remove Microsoft pkg
   .NET and Homebrew `dotnet@8`.
14. Remove .NET 8 from `mise` only after all compatibility projects have
   migrated and a separate approval gate passes.

## What Not To Do

- Do not install `mise` during this readiness pass.
- Do not install, uninstall, relink, unlink, repair, or upgrade any .NET
  SDK/runtime during this readiness pass; `install-dotnet-sdks` is repo wiring
  and must be validated with dry-runs only until an approved mutation step.
- Do not remove Microsoft pkg files or Homebrew `dotnet@8`.
- Do not install or uninstall global tools until SDK ownership and PATH parity
  are stable; recipes may declare the intended install command, but validation
  must use dry-runs only.
- Keep `/Users/alex/.dotnet/tools` as an expanded path in shell and dev
  environment contracts.
- Do not assume non-login or AI command contexts use the same PATH as an
  interactive zsh login shell.
