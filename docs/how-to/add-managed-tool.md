# Add Or Classify A Managed Tool

Use this guide when adding a tool to the Development Ecosystem or deciding how
an already-installed tool should be represented.

Start by asking whether the tool belongs in the global development baseline. If
it is only personal, project-specific, credential-bound, generated, or temporary,
do not add it to the baseline manifests.

## Choose The Ownership Path

| Tool kind | Source of truth | Notes |
| --- | --- | --- |
| macOS CLI formula | `system/packages/Brewfile` | Use Homebrew when it owns install and upgrades. |
| macOS GUI app or cask | `system/packages/Brewfile` | Baseline development apps only. |
| Personal app | `system/packages/personal.Brewfile` | Gitignored local manifest. |
| Global JavaScript tool | `system/packages/pnpm-global.txt` | Use `fnm` plus Corepack/pnpm. |
| Node runtime | ADR-governed | ADR-0007 selects `fnm`; do not add Homebrew `node`. |
| .NET SDK | `system/mise/config.toml` | ADR-0006 selects `mise`. |
| .NET global tool | `system/packages/dotnet-tools.txt` | Use `scripts/dotnet_toolchain.sh`. |
| VS Code extension | `system/packages/vscode-extensions.txt` | Keep editor manifests explicit. |
| Shared AI Asset | `system/ai/apm/apm.yml` | Requires APM policy and target-write gates. |
| AI Tool Surface binary | `Brewfile` or manifest | APM owns assets, not AI binaries. |
| Manual or exceptional tool | `system/packages/manual-apps.md` | Include reason and gate. |

If the tool changes a durable ownership boundary, write or update an ADR before
changing manifests.

## Add A Homebrew Tool

1. Confirm it belongs in the Development Ecosystem baseline.
2. Add the formula, cask, tap, or VS Code entry to
   `system/packages/Brewfile`.
3. Keep comments short and focused on why the tool exists.
4. Run:

```sh
brew bundle check --file=system/packages/Brewfile --verbose
just doctor
```

Run `brew bundle --file=system/packages/Brewfile` only when you intend to
install or update local packages.

## Add A Global JavaScript Tool

1. Confirm the tool should be globally available across projects.
2. Add the package name to `system/packages/pnpm-global.txt`.
3. Use the canonical wrapper when installing or checking it:

```sh
just install-node-tools
./scripts/js_toolchain.sh pnpm list -g --depth 0
just doctor
```

Do not use npm globals for steady-state tooling. ADR-0007 makes `fnm` plus
Corepack/pnpm the JS toolchain owner.

## Add A .NET Tool

1. Confirm the tool should be global rather than project-local.
2. Add the package ID to `system/packages/dotnet-tools.txt`.
3. Install through the `mise`-managed .NET wrapper:

```sh
just install-dotnet-tools
./scripts/dotnet_toolchain.sh dotnet tool list --global
just doctor
```

Do not bypass `scripts/dotnet_toolchain.sh`; it prevents accidental fallback to
Microsoft pkg .NET or removed Homebrew SDK paths.

## Add Or Classify An AI Asset

Use `system/ai/README.md` first. The current model distinguishes:

- AI Tool Surface binaries such as Codex, Claude Code, opencode, and Pi;
- Shared AI Assets managed by APM;
- Sensitive Local State under tool-specific config and cache roots.

Shared assets should enter through `system/ai/apm/apm.yml` and
`system/ai/apm/apm.lock.yaml`. Do not hand-copy prompt or skill output into
tool-specific config trees unless an approved target-write gate says to do so.

## Document A Managed Exception

Use `system/packages/manual-apps.md` when a tool is intentional but cannot be
fully represented by a normal manifest, or when cleanup must be delayed.

Record:

- current local path or package source;
- why it is not normal baseline state;
- whether it is a Managed Exception, personal state, or cleanup candidate;
- the approval gate required before mutating or removing it;
- exact date for time-sensitive observations.

## Validate The Change

For a docs or manifest-only change:

```sh
just doctor
git diff --check
```

For markdown changes:

```sh
./scripts/js_toolchain.sh markdownlint path/to/file.md
```

For shell or script changes, also run the relevant syntax checks named in the
nearby plan or README before relying on the change.
