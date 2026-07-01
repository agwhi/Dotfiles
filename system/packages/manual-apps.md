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
- `intentionally-excluded`: observed local state that is outside the
  Development Ecosystem baseline for now.

## Approval-Gated Homebrew State

- `node` (Homebrew formula): duplicate Node runtime owner. ADR-0007 selects
  `fnm`; remove Homebrew `node` only after proving no formula, shell, editor,
  or project workflow still depends on it.
- `pnpm` (Homebrew formula): duplicate package-manager owner. ADR-0007 keeps
  Corepack/pnpm under the selected `fnm` default Node; remove the Homebrew
  formula only after shell parity and global tool paths are verified.
- `dotnet@8` (Homebrew formula): declared managed exception. ADR-0006 selects
  `mise` as the strategic .NET SDK owner, but this formula remains installed
  until the `mise` SDK root, editor discovery, workloads, and global tools are
  proven.
- `unbound` (Homebrew formula/service): installed leaf with network-service
  behavior and no current Brewfile declaration. Keep approval-gated until DNS
  ownership between macOS, `dnscrypt-proxy`, and any local resolver workflow is
  verified.
- `docker` link state: the Homebrew formula is declared as part of the
  container baseline, but its keg is currently unlinked and `docker` is not on
  PATH. Link or repair it only in a later approved install/repair task.

## Manual Or Local Tool State

- `/usr/local/share/dotnet/dotnet`: active Microsoft pkg .NET SDK source.
  Managed exception until ADR-0006's `mise` migration is implemented and
  verified.
- `/usr/local/bin/apm`: manual/pkg CLI. Identify whether this is the intended
  AI Asset Manager or unrelated legacy state before declaring or removing it.
- `/usr/local/bin/cursor`: app-provided CLI shim for the Homebrew-managed
  Cursor cask. Keep as local app state unless a later editor policy migrates
  it.
- `~/.local/bin/claude`: manual-local AI CLI. Defer declaration, migration, or
  removal to the AI Tool Surface task.
- Codex app runtime helper commands such as `codex-execve-wrapper` and
  `codex_chronicle`: app/runtime context, not package-manager drift.

## Intentional Exclusions

- `whatsapp` (Homebrew cask): personal messaging app observed in Homebrew
  state, but not part of the Development Ecosystem baseline in this pass.
