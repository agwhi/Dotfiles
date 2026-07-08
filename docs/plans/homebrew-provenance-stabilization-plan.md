# Homebrew Provenance Stabilization Plan

Date: 2026-07-01.
Status: completed. Historical record; current state comes from `just doctor`
and the package manifests.

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
strategic .NET SDK owner. Homebrew `dotnet@8` and the Microsoft pkg SDK source
root were removed after the `mise` migration was verified.

Homebrew `node` and `pnpm` were not added. ADR-0007 selects `fnm` as the Node,
Corepack, and pnpm owner. The duplicate Homebrew formulae were removed during
cleanup, and `node` and `pnpm` now resolve through the `fnm` default Node.

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
- `httpie`
- `mise`
- `mysql-client`
- `ollama`
- `poppler`
- `semgrep`
- `universal-ctags`
- `uv`

Casks added as canonical Homebrew-managed applications or support tools:

- `bruno`
- `caffeine`
- `chatgpt-atlas`
- `codex`
- `leapp`
- `maccy`
- `rider`
- `session-manager-plugin`

## Managed Exceptions And Approval Gates

No active Homebrew duplicate-owner exceptions remain from this pass.

Future manual/local exceptions should be recorded in
`system/packages/manual-apps.md` before cleanup. Stale package receipts are
informational unless they create doctor-visible drift or installer conflicts.

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

- `whatsapp` remains an installed, intentionally excluded cask managed through
  the gitignored local `system/packages/personal.Brewfile`.
- Initial manual GUI apps outside the Brewfile were recorded in
  `system/packages/manual-apps.md`: Dia, Firefox, Wispr Flow, Falcon, and the
  Claude Code URL handler.

On the follow-up pass, Firefox and Wispr Flow were promoted to the Brewfile,
and Dia was removed as unwanted local state. Falcon remains explicitly outside
repo ownership.

The final cleanup pass removed Homebrew `dotnet@8` and confirmed no Homebrew
`unbound` formula or service was installed. Postman was replaced by Bruno for
GUI API development and HTTPie for command-line API requests.

The later interactive cleanup pass removed the remaining root-owned manual
state for Microsoft pkg .NET under `/usr/local/share/dotnet` and legacy manual
APM under `/usr/local/bin/apm` and `/usr/local/lib/apm`. NordVPN is now
upgraded to cask version `10.5.1`. Stale Microsoft pkg receipts may still be
visible through `pkgutil`, but no legacy SDK source path remains.

## Intentional Exclusion

`whatsapp` is installed as a Homebrew cask, but it is personal messaging state
outside this Development Ecosystem baseline. It was documented as intentionally
excluded instead of being promoted to the Brewfile.

## Follow-Up Checks

- Re-run `just doctor --json` after the Brewfile changes and confirm
  Homebrew present-undeclared drift is limited to duplicate or approval-gated
  state.
- Keep stale package receipts informational unless they create doctor-visible
  drift or installer conflicts.
- Keep AI CLI and asset decisions in the AI Tool Surface task.
