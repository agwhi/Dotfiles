# Homebrew Provenance Stabilization Plan

Date: 2026-07-01.

This original pass was non-mutating. It recorded live Homebrew state against
the repo source of truth without installing, uninstalling, upgrading, linking,
unlinking, cleaning up, or changing taps. A later 2026-07-07 reconciliation
pass applied the approved Homebrew work described below.

## Evidence

Read-only commands used:

- `just doctor --json`
- `brew list --formula --full-name`
- `brew list --cask`
- `brew leaves`
- `brew deps --installed`
- `brew bundle check --file=system/packages/Brewfile`
- `brew bundle check --verbose --file=system/packages/Brewfile`
- `brew bundle list --all --file=system/packages/Brewfile`
- `brew info --json=v2` for undeclared formula and cask candidates

`just doctor --json` reported that all previously declared Homebrew formulae
and casks were installed. `brew bundle check --verbose` still reported bundle
drift because `visual-studio-code`, `carapace`, and `awscli` can be updated,
and because the VS Code extension `github.copilot` is declared but absent.
Those are update or extension-install concerns, not Homebrew provenance removal
approval.

## Decisions

Homebrew remains the canonical macOS package manifest. Installed
development-related Homebrew leaves and casks with no stronger owner were added
to `system/packages/Brewfile`.

`mise` was added as desired Homebrew state because ADR-0006 selects it as the
strategic .NET SDK owner. The current Microsoft pkg .NET install and Homebrew
`dotnet@8` stay as managed exceptions until the `mise` migration is explicitly
approved and verified.

Homebrew `node` and `pnpm` were not added. ADR-0007 selects `fnm` as the Node,
Corepack, and pnpm owner. The installed Homebrew formulae are duplicate owners
and approval-gated removal candidates.

Docker/Colima was promoted to the Brewfile as the container development
baseline. The intended model is Colima as the runtime and Homebrew `docker` as
the CLI. Docker Desktop is not part of the baseline.

AI-related Homebrew packages were represented only at the install-surface
level. Deeper AI CLI, asset, cache, and config classification remains reserved
for the AI Tool Surface task.

## Canonical Homebrew Additions

Formulae added as canonical Homebrew-managed development tools:

- `ast-grep`
- `colima`
- `composer`
- `docker`
- `docker-buildx`
- `docker-compose`
- `ffmpeg`
- `graphviz`
- `mise`
- `mysql-client`
- `ollama`
- `poppler`
- `semgrep`
- `universal-ctags`
- `uv`

Casks added as canonical Homebrew-managed applications or support tools:

- `caffeine`
- `chatgpt-atlas`
- `codex`
- `leapp`
- `maccy`
- `postman`
- `rider`
- `session-manager-plugin`

## Managed Exceptions And Approval Gates

Do not remove or migrate these without explicit approval:

- Homebrew `node`, because it duplicates the ADR-0007 `fnm` Node owner.
- Homebrew `pnpm`, because it duplicates the ADR-0007 Corepack/pnpm owner.
- Homebrew `dotnet@8`, because it is a declared .NET migration exception.
- Microsoft pkg .NET under `/usr/local/share/dotnet`, because it is the active
  SDK source in the current zsh/Codex context.
- Homebrew `unbound`, because it has resolver-service behavior and DNS
  ownership has not been verified.
- Manual/local AI and editor shims recorded in
  `system/packages/manual-apps.md`.

## 2026-07-07 Reconciliation

`brew bundle install --file=system/packages/Brewfile` updated declared
formulae and casks. The pass found two source-of-truth corrections:

- `docker-completion` conflicted with the `docker` formula. The `docker`
  formula already ships bash, zsh, fish, and PowerShell completions, so the
  separate completion formula was removed from the Brewfile and uninstalled.
- `github.copilot-chat` is now built into VS Code on this laptop. Installing
  the marketplace extension attempted to downgrade the built-in version, so it
  was removed from the Brewfile and `system/packages/vscode-extensions.txt`.
- `github.copilot` also resolves as app-managed VS Code content under
  `/Applications/Visual Studio Code.app/Contents/Resources/app/extensions/copilot`;
  the marketplace install path still tried to install the built-in chat
  dependency, so it was removed from the explicit extension manifests too.

Docker/Colima target state after reconciliation:

- Keep `colima` as the container runtime manager.
- Keep `docker` as the CLI used to talk to Colima.
- Keep `docker-buildx` and `docker-compose` as declared CLI plugins/tools.
- Do not install Docker Desktop unless a future workflow specifically needs
  Docker Desktop features.

Remaining Homebrew/manual app decisions:

- `nordvpn` remains declared but needs an interactive upgrade because its
  helper uninstall path requires `sudo`.
- `whatsapp` remains an installed, intentionally excluded cask managed through
  the gitignored local `system/packages/personal.Brewfile`.
- Initial manual GUI apps outside the Brewfile were recorded in
  `system/packages/manual-apps.md`: Dia, Firefox, Wispr Flow, Falcon, and the
  Claude Code URL handler.

On the follow-up pass, Firefox and Wispr Flow were promoted to the Brewfile,
and Dia was removed as unwanted local state. Falcon remains explicitly outside
repo ownership.

## Intentional Exclusion

`whatsapp` is installed as a Homebrew cask, but it is personal messaging state
outside this Development Ecosystem baseline. It was documented as intentionally
excluded instead of being promoted to the Brewfile.

## Follow-Up Checks

- Re-run `just doctor --json` after the Brewfile changes and confirm
  Homebrew present-undeclared drift is limited to duplicate or approval-gated
  state.
- In a separate install/repair task, decide whether to link Homebrew `docker`
  or remove the unlinked formula behind approval.
- Decide whether Homebrew `unbound` belongs to the network-security baseline or
  should be removed behind approval.
- Implement ADR-0006's `mise` .NET migration in a separate approved task.
- Remove Homebrew `node` and `pnpm` only after ADR-0007 shell parity and pnpm
  global paths are verified.
- Keep AI CLI and asset decisions in the AI Tool Surface task.
