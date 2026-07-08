# .NET SDK Stabilization Plan

Date: 2026-07-01. Updated: 2026-07-07.
Status: completed. Historical record; current state comes from `just doctor`
and the package manifests.

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

`mise` is now active for the shell/Codex path and lists both target SDK lines.
Homebrew `dotnet@8` and the Microsoft pkg SDK source root under
`/usr/local/share/dotnet` were removed on 2026-07-07. Stale Microsoft pkg
receipts may still be visible through `pkgutil`, but no legacy SDK source path
is present and doctor reports the SDK source as canonical.

## Evidence

Local command evidence collected on 2026-07-01:

- Before migration, `which -a dotnet` in the zsh/Codex context returned only
  `/usr/local/share/dotnet/dotnet`.
- Before migration, the active Microsoft pkg SDK was `8.0.412` at
  `/usr/local/share/dotnet/sdk`.
- Before migration, active Microsoft pkg runtimes were
  `Microsoft.AspNetCore.App 8.0.18` and `Microsoft.NETCore.App 8.0.18`.
- Before migration, active Microsoft pkg workloads were none.
- Microsoft pkg receipts include
  `com.microsoft.dotnet.dev.8.0.412.component.osx.arm64` and runtime receipts
  under `usr/local/share/dotnet`.
- Homebrew `dotnet@8` was previously installed on request and declared in
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
- Homebrew formula metadata reported `mise` as available before the migration,
  and `brew list --versions mise` now reports `mise 2026.6.14`.
- `system/packages/Brewfile` now declares `mise` as the strategic .NET SDK
  owner and no longer declares Homebrew `dotnet@8`.
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
- Local command evidence collected on 2026-07-02 shows `dotnet` resolving
  through `/Users/alex/.local/share/mise/shims/dotnet`, followed by the old
  Microsoft pkg path and Homebrew `dotnet@8` path.
- `dotnet --list-sdks` now reports `8.0.422` and `10.0.301` from
  `/Users/alex/.local/share/mise/dotnet-root/sdk`.
- `system/packages/dotnet-tools.txt` declares only `Amazon.Lambda.Tools` and
  `Amazon.Lambda.TestTool-8.0`; both declared tools are installed as
  `amazon.lambda.tools 7.0.0` and `amazon.lambda.testtool-8.0 0.18.0`.
- The previously installed undeclared global tools `amazon.lambda.testtool`,
  `csharpier`, `deadcsharp`, and `dotnet-ef` were removed on 2026-07-05.
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
| `mise` .NET | Strategic .NET owner that installs .NET 10 and .NET 8 side-by-side under a shared `DOTNET_ROOT` and supports project-level runtime selection. | Requires shell activation, doctor policy, editor-terminal parity, and migration from current SDK sources. | Selected as the .NET strategic replacement. |
| Microsoft pkg shared root | Native .NET side-by-side behavior and compatible with .NET 10 plus .NET 8 overlap through pkg/cask installs. | Manual/pkg state is outside the Brewfile, cleanup is receipt/root-owned, and project-level runtime ownership would remain less explicit than `mise`. | Rejected as canonical; the active SDK source has moved to `mise`. |
| Homebrew casks `dotnet-sdk` plus `dotnet-sdk@8` | Repo-installable wrapper around Microsoft's pkg layout and supports .NET 10 plus .NET 8 overlap. | Still lands in `/usr/local/share/dotnet`, not a runtime-manager root; Homebrew cask upgrade/removal behavior needs careful gates. | Use only as fallback if `mise` is rejected during implementation. |
| Homebrew formula `dotnet` plus `dotnet@8` | Formula `dotnet` provides .NET 10 and `dotnet@8` was available during evaluation. | Versioned formulae live in separate Homebrew roots, making side-by-side SDK discovery and `DOTNET_ROOT` policy less clean. | Reject as the canonical owner. |
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

The Microsoft pkg SDK source root and Homebrew `dotnet@8` have both been
removed because the core `mise` checks now pass:

- `dotnet` resolves through the `mise` shim in the current shell/Codex context.
- .NET 10 is available as the default SDK line.
- .NET 8 is available for compatibility projects.
- Declared global tools are installed and visible.

Further cleanup confidence still needs project/editor-specific confirmation
where relevant:

- .NET 8 projects build/test without relying on legacy SDK paths.
- Workloads such as Aspire remain visible where needed.
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
.NET root exists. In the current zsh/Codex context, plain `dotnet` resolves to
`/Users/alex/.local/share/mise/shims/dotnet`, and the `mise` root exposes SDKs
`8.0.422` and `10.0.301`.

Just recipes:
Current recipes route .NET global tool installs through
`scripts/dotnet_toolchain.sh`, which runs under the ADR-0006 `mise` context.
The migration order has completed for the repo-managed SDK and declared tool
baseline: snapshot reports were written locally, Homebrew installed `mise`,
symlink setup linked the repo-managed `system/mise/config.toml`,
`install-dotnet-sdks` installed the declared SDK lines through `mise`, and
`setup-dotnet` installed approved global tools through that SDK context. Future
SDK repair or reinstall work should still use
`scripts/dotnet_sdk_install.sh --dry-run` before running the mutating install.
Compatibility projects should pin their SDK instead of relying on a global
shell default.

Snapshot artifacts:
`just dotnet-snapshot` writes
`reports/dotnet-migration-snapshot-<timestamp>.md`. The `reports/` directory is
gitignored because snapshots contain local machine state and should stay
local-only unless Alex deliberately chooses to publish a sanitized excerpt.

Editor terminals:
VS Code and other managed editor terminals should resolve the same `mise`
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
That keeps future bootstrap and repair order clear. Any additional mutation to
SDKs or global tools still needs explicit approval.

Current decisions:

- Keep `Amazon.Lambda.TestTool-8.0` declared while .NET 8 projects remain.
- Keep `Amazon.Lambda.Tools` declared; it is now installed through the
  `mise`-managed SDK context.
- Keep `system/packages/dotnet-tools.txt` unchanged until repo evidence proves
  another tool belongs in the global baseline.
- Keep project-specific .NET tools out of the global baseline unless a later
  workflow proves they need to be globally installed.

Removed undeclared global tool classification:

<!-- markdownlint-disable MD013 -->

| Tool | Classification | Decision |
| --- | --- | --- |
| `amazon.lambda.testtool` | removed approval-gated cleanup | Legacy Lambda test tool variant duplicated the declared `Amazon.Lambda.TestTool-8.0` baseline. Do not reintroduce unless Alex confirms a workflow still needs the non-8.0 package. |
| `csharpier` | project-local | Formatter version should be pinned by consuming C# projects if needed. Do not declare globally from this repo without project evidence. |
| `deadcsharp` | removed approval-gated cleanup | Analysis tool had no baseline evidence in this repo. Do not reintroduce without explicit approval. |
| `dotnet-ef` | project-local | EF Core CLI version should track the consuming project's EF package line. Do not declare globally from this repo without project evidence. |

<!-- markdownlint-enable MD013 -->

## Cleanup Gates

Completed migration gates:

- `just dotnet-snapshot` wrote local reports under `reports/` before the SDK
  source migration.
- Keep `system/packages/Brewfile` and `system/mise/config.toml` as the
  repo-managed declarations.
- Keep `dotnet = ["10", "8"]` as the SDK selector policy unless a later ADR
  changes the default or compatibility line.
- Prove `dotnet` resolves through `/Users/alex/.local/share/mise/shims/dotnet`
  in the current zsh/Codex context. Done.
- Prove `dotnet --list-sdks` sees .NET 10 and .NET 8 from the `mise` root.
  Done.
- Prove declared global tools are installed. Done.

Remaining parity gates before SDK-source removal:

- Decide how `global.json` should be handled in compatibility projects.
- Prove VS Code terminal and AI command surfaces resolve the
  `mise` `dotnet` if they are in scope for the cleanup task.
- Prove editor C# tooling discovers the `mise` SDK root if editor cleanup
  confidence is required.
- Prove workloads remain visible where needed.

Microsoft pkg cleanup:

- `/usr/local/share/dotnet` was removed on 2026-07-07 after `mise` became the
  canonical SDK source.
- Stale Microsoft pkg receipts may remain visible through `pkgutil`; treat them
  as informational unless they create doctor-visible drift or installer
  conflicts.
- Prove .NET 8 compatibility projects build/test through `mise` before removing
  the .NET 8 SDK line from `system/mise/config.toml`.

Homebrew `dotnet@8` cleanup:

- Prove no shell, editor, recipe, workload, or project uses
  `/opt/homebrew/opt/dotnet@8`.
- Update the Brewfile and doctor policy to stop expecting Homebrew `dotnet@8`.
- Perform `brew uninstall dotnet@8` only with explicit approval. Done on
  2026-07-07.

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
7. Run `dotnet-snapshot`, install and link `mise`, install SDKs, run
   `setup-dotnet`, then verify doctor. Done for the current zsh/Codex context.
8. Install .NET 10 and .NET 8 through `mise` by running `install-dotnet-sdks`
   after Homebrew installs `mise`. Done.
9. Activate `mise` in zsh/Codex. Done.
10. Install declared global tools through the `mise`-managed SDK. Done.
11. Keep .NET global tools as `dotnet tool --global` installs for now; migrate
   to `mise` `dotnet:ToolName` declarations only if a later decision finds
   better reproducibility.
12. Classify and remove `dotnet-ef`, `csharpier`, `deadcsharp`, and the legacy
   Lambda test tool package. Done.
13. Re-run editor-terminal checks from VS Code before SDK-source cleanup if
   editor verification is in scope for the removal task.
14. Microsoft pkg .NET source cleanup and Homebrew `dotnet@8` removal are
   done.
15. Remove .NET 8 from `mise` only after all compatibility projects have
   migrated and a separate approval gate passes.

## What Not To Do

- Do not reinstall, uninstall, relink, unlink, repair, or upgrade any .NET
  SDK/runtime during this cleanup-planning pass.
- Do not remove stale Microsoft pkg receipts unless they create installer or
  doctor-visible drift.
- Do not install, update, or uninstall additional global tools during this
  cleanup-planning pass.
- Keep `/Users/alex/.dotnet/tools` as an expanded path in shell and dev
  environment contracts.
- Do not assume non-login or AI command contexts use the same PATH as an
  interactive zsh login shell.
