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

## Approval-Gated Homebrew State

- `dotnet@8` (Homebrew formula): declared managed exception and
  approval-gated cleanup candidate. ADR-0006 selects `mise` as the strategic
  .NET SDK owner, and the `mise` SDK root now exposes the declared .NET 10 and
  .NET 8 SDK lines. Keep this formula installed until a separate cleanup task
  confirms no project, editor, workload, recipe, or shell path still depends on
  `/opt/homebrew/opt/dotnet@8`.
- `unbound` (Homebrew formula/service): installed leaf with network-service
  behavior and no current Brewfile declaration. Keep approval-gated until DNS
  ownership between macOS, `dnscrypt-proxy`, and any local resolver workflow is
  verified.
- `docker` link state: the Homebrew formula is declared as part of the
  container baseline, but its keg is currently unlinked and `docker` is not on
  PATH. Link or repair it only in a later approved install/repair task.

## Manual Or Local Tool State

- `/usr/local/share/dotnet/dotnet`: Microsoft pkg .NET SDK source still
  present after the `mise` migration. It is no longer the canonical source when
  PATH resolves through `/Users/alex/.local/share/mise/shims/dotnet`; keep it
  as an approval-gated cleanup candidate until a separate task confirms no
  project, editor, workload, or Lambda workflow depends on the pkg root.
- `/usr/local/bin/apm`: legacy manual/pkg duplicate resolving to
  `/usr/local/lib/apm/apm`. ADR-0008 selects APM as the AI Asset Manager, and
  the active `apm` command now resolves through `/opt/homebrew/bin/apm` from
  the declared Homebrew formula `microsoft/apm/apm`. Keep the old root-owned
  manual binary as an approval-gated removal candidate. A 2026-07-05
  non-interactive cleanup attempt confirmed Homebrew PATH precedence but could
  not remove the duplicate because `sudo` requires a password. Do not
  self-update, reinstall, prune, or remove it without an interactive approval
  path.
- `/usr/local/bin/cursor`: app-provided CLI shim for the Homebrew-managed
  Cursor cask. Keep as local app state unless a later editor policy migrates
  it.
- Codex app runtime helper commands such as `codex-execve-wrapper` and
  `codex_chronicle`: app-runtime-context, not package-manager drift.

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
- npm global `opencode-ai`: removed after migrating opencode CLI ownership to
  the upstream Homebrew tap `anomalyco/tap/opencode` on 2026-07-07. The IVCE
  AI Gateway / Bedrock config and opencode APM skills were verified unchanged
  by hash during the migration.
- Pi global packages: the deprecated `@mariozechner/pi-coding-agent` package
  and npm-installed Pi helper packages were removed on 2026-07-05, then Pi was
  restored through the canonical pnpm global manifest using the maintained
  `@earendil-works/pi-coding-agent` package and declared Pi extension packages.
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
  state, but not part of the Development Ecosystem baseline in this pass.
