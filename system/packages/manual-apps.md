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

- `node` (Homebrew formula): duplicate Node runtime owner. ADR-0007 selects
  `fnm`; remove Homebrew `node` only after proving no formula, shell, editor,
  or project workflow still depends on it.
- `pnpm` (Homebrew formula): duplicate package-manager owner. ADR-0007 keeps
  Corepack/pnpm under the selected `fnm` default Node; remove the Homebrew
  formula only after shell parity and global tool paths are verified.
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
- `/usr/local/bin/apm`: manual/pkg CLI resolving to `/usr/local/lib/apm/apm`.
  ADR-0008 selects APM as the AI Asset Manager, and
  `system/packages/Brewfile` now declares the official Homebrew tap formula
  `microsoft/apm/apm` as the intended installer. Keep this manual binary as a
  managed exception and cleanup candidate until a later task installs/verifies
  the Homebrew formula and confirms PATH precedence. Do not self-update,
  reinstall, prune, or remove it without approval.
- `/usr/local/bin/cursor`: app-provided CLI shim for the Homebrew-managed
  Cursor cask. Keep as local app state unless a later editor policy migrates
  it.
- `~/.local/bin/claude`: manual-local AI CLI resolving to
  `~/.local/share/claude/versions/2.1.198`. Keep as a managed exception until
  a later task declares the Claude Code CLI install path. Older local versions
  `2.1.187`, `2.1.196`, and `2.1.197` are approval-gated cleanup candidates.
- Codex app runtime helper commands such as `codex-execve-wrapper` and
  `codex_chronicle`: app-runtime-context, not package-manager drift.
- `~/.local/share/fnm/aliases/default/bin/opencode`: npm-global
  `opencode-ai` binary observed under the `fnm` default Node path. Current
  observed version is `1.17.13`. Keep as a legacy managed exception until the
  AI Tool Surface policy decides whether opencode is project-local, managed,
  or removed.
- `~/Library/pnpm/pi`: pnpm-global Pi command from
  `@mariozechner/pi-coding-agent`. Not part of the Global AI Baseline. Migrate
  to APM or remove only behind approval.

## AI Approval-Gated Cleanup

- `~/.codex/skills/grill-with-docs`: target Baseline AI Asset. Do not replace
  or remove until APM can reproduce the intended baseline.
- `~/.codex/skills/using-superpowers`: approval-gated-removal. ADR-0003 keeps
  it out of the Global AI Baseline; remove only in a later cleanup task with a
  Rebuild Snapshot.
- Claude cached superpowers plugin versions under `~/.claude/plugins/cache`:
  approval-gated-removal after APM reproduces the selected baseline.
- npm global `opencode-ai`: approval-gated-removal or migration candidate after
  opencode policy is decided.
- pnpm global `@mariozechner/pi-coding-agent`: approval-gated-removal or
  project-local migration candidate after Pi policy is decided.

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
