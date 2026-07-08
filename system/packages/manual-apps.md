# Manual Apps And Approval Gates

Use this manifest for apps and tools that require manual installation, account
setup, licensing, approval, or a Reset Approval Gate before automation.

## States

- `managed-exception`: intentionally present outside the future steady-state
  owner while migration is in progress.
- `approval-gated-removal`: do not remove without explicit approval and a
  rebuild snapshot when relevant.
- `manual-local`: installed or exposed outside a package manifest and not yet
  migrated to a canonical installer.
- `app-runtime-context`: command or helper exposed by an application runtime,
  not an independently managed package.
- `intentionally-excluded`: observed local state that is outside the
  Development Ecosystem baseline for now.

Entries under Completed Cleanup are history, not exemptions: doctor ignores
that section, so leftovers of a removed tool are reported again.

## Approval-Gated Homebrew State

No current approval-gated Homebrew state is recorded here.

## Manual Or Local Tool State

- Codex app runtime helper commands such as `codex-execve-wrapper` and
  `codex_chronicle`: app-runtime-context, not package-manager drift.
- `/Users/alex/Applications/Claude Code URL Handler.app`: Claude Code app
  runtime helper. Keep as app-runtime-context, not an independent package.

## Manual GUI Apps Observed

- `/Applications/Falcon.app` (`com.crowdstrike.falcon.App`, version `7.38`):
  external security/MDM-managed software. Keep it out of this repo's package
  manifests and do not remove or migrate it without explicit confirmation.
- Bundled Apple apps such as Safari, GarageBand, iMovie, Keynote, Numbers, and
  Pages are treated as OS/app-suite state, not development baseline drift.

## AI Approval-Gated Cleanup

- `~/.codex/skills/grill-with-docs`, `~/.codex/skills/grilling`, and
  `~/.codex/skills/domain-modeling`: APM-managed Codex baseline. Mutate only
  through approved APM target-write gates.
- `~/.config/opencode/skills/grill-with-docs`,
  `~/.config/opencode/skills/grilling`, and
  `~/.config/opencode/skills/domain-modeling`: APM-managed opencode baseline.
  Mutate only through approved APM target-write gates.
- `~/.codex/skills/using-superpowers`: intentionally excluded and currently
  absent from the live baseline. Reinstall only if a later ADR changes the
  Global AI Baseline.
- Claude cached superpowers plugin versions under `~/.claude/plugins/cache`:
  approval-gated-removal if Claude later receives an approved APM-managed
  baseline.

## Completed Cleanup

- Homebrew `node` and Homebrew `pnpm`: removed on 2026-07-05 after ADR-0007
  made `fnm` plus Corepack/pnpm the canonical JavaScript toolchain owner.
- Homebrew `docker-completion`: removed from the baseline on 2026-07-07 because
  the `docker` formula ships bash, zsh, fish, and PowerShell completions itself
  and the separate formula blocked `docker` from linking.
- Homebrew `docker`: linked successfully on 2026-07-07 after
  `docker-completion` was removed. Keep `docker` as the CLI for the Colima
  runtime; Docker Desktop was not installed and is not part of the baseline.
- Homebrew `dotnet@8`: removed from the Brewfile and uninstalled on
  2026-07-07 after `mise` became the canonical .NET SDK owner and exposed the
  required .NET 10 and .NET 8 SDK lines.
- Microsoft pkg .NET SDK source files under `/usr/local/share/dotnet`: removed
  on 2026-07-07 after the `mise` SDK source was verified. Stale pkg receipts
  may still be listed by `pkgutil`, but no legacy SDK source path is present
  and doctor reports `.NET` source state as canonical.
- Legacy manual APM duplicate under `/usr/local/bin/apm` and
  `/usr/local/lib/apm`: removed on 2026-07-07. The active `apm` command now
  resolves only through the declared Homebrew formula `microsoft/apm/apm`.
- Homebrew `nordvpn`: upgraded to cask version `10.5.1` on 2026-07-07 after
  the earlier non-interactive helper cleanup blocker was resolved.
- Homebrew `unbound`: no installed Homebrew formula or service was detected on
  2026-07-07, so the stale approval-gated cleanup note was removed.
- Homebrew `cursor`: removed from the Brewfile and uninstalled on 2026-07-07
  after ADR-0011 selected VS Code plus dedicated AI agents instead of Cursor as
  a managed GUI editor surface.
- `/Applications/Dia.app`: removed on 2026-07-07 after Alex confirmed it was
  not needed.
- `/Applications/Firefox.app`: migrated to Homebrew cask `firefox` on
  2026-07-07.
- `/Applications/Wispr Flow.app`: migrated to Homebrew cask `wispr-flow` on
  2026-07-07.
- npm global `opencode-ai`: removed after migrating opencode CLI ownership to
  the upstream Homebrew tap `anomalyco/tap/opencode` on 2026-07-07. The IVCE
  AI Gateway / Bedrock config and opencode APM skills were verified unchanged
  by hash during the migration.
- npm global `context-mode`: removed on 2026-07-07 after no current Codex,
  Claude, opencode, or Pi config referenced it and Alex did not recognize it.
- Stale Homebrew-prefix Node globals: `/opt/homebrew/bin/cdk`,
  `/opt/homebrew/lib/node_modules/aws-cdk`, and
  `/opt/homebrew/lib/node_modules/npm` were removed on 2026-07-07. `cdk` now
  resolves through the declared pnpm global `aws-cdk`.
- Declared pnpm globals: `@biomejs/biome`, `aws-cdk`, `cdk-dia`, and
  `markdownlint-cli` were refreshed through the canonical fnm/pnpm path on
  2026-07-07.
- Pi global packages: the deprecated `@mariozechner/pi-coding-agent` package
  and npm-installed Pi helper packages were removed on 2026-07-05, then Pi was
  restored through the canonical pnpm global manifest using the maintained
  `@earendil-works/pi-coding-agent` package and declared Pi extension packages.
  Declared Pi packages were refreshed through pnpm on 2026-07-07. Keep `~/.pi`
  as sensitive local state.
- Undeclared `.NET` global tools: `amazon.lambda.testtool`, `csharpier`,
  `deadcsharp`, and `dotnet-ef` were removed on 2026-07-05. Project-specific
  .NET tooling should be pinned in consuming projects instead of reintroduced
  as global baseline state.

## Sensitive AI Local State

Do not commit, delete, rewrite, or move these without explicit approval and a
Rebuild Snapshot:

- `~/.codex` auth, history, logs, local databases, trusted-project state,
  plugin caches, runtime caches, attachments, shell snapshots, and temporary
  wrappers.
- `~/.claude`, `~/.claude.json`, and `~/.local/share/claude` permissions,
  settings, plugin caches, histories, backups, debug files, and installed
  versions.
- `~/.local/share/opencode` account/auth files, databases, logs, snapshots,
  storage, and MCP auth state.
- `~/.config/opencode` provider configuration, local wrappers, package state,
  and generated dependencies.

## Intentional Exclusions

- `whatsapp` (Homebrew cask): personal messaging app observed in Homebrew
  state, but not part of the Development Ecosystem baseline. Keep it in the
  gitignored local `system/packages/personal.Brewfile`.
