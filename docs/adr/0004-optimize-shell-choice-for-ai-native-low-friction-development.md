# Optimize Shell Choice For AI-Native Low-Friction Development

Status: accepted.
Date: 2026-07-01.
Amended: 2026-07-07. Reconstructed decision history and ADR quality structure.
Amended by: ADR-0011.
Related: ADR-0001, docs/plans/zsh-primary-adoption-plan.md,
scripts/dev_env.sh, scripts/js_toolchain.sh, system/packages/Brewfile.

## Context

This ADR preserves the shell decision reached after investigating Nushell,
zsh, AI agent ergonomics, and editor terminal behavior. Alex liked Nu for some
structured-data workflows, but the development ecosystem needed a lower-friction
default for vendor docs, AI-generated commands, bootstrap scripts, `just`
recipes, and POSIX-compatible examples.

The repo had previously needed reminders that Alex used Nushell, which consumed
context and created command-syntax mismatches for AI agents. The stabilization
goal was to reduce that friction while keeping explicit wrappers for commands
that should not depend on an interactive shell.

## Decision Drivers

- AI agents and vendor docs overwhelmingly assume POSIX-like shells.
- Bootstrap, install, and doctor commands should be easy to run from zsh,
  Codex, editor terminals, and non-login command contexts.
- Shell startup files should be repo-managed and inspectable.
- Runtime and package-manager paths should not depend on undocumented aliases.
- A second first-class shell doubles maintenance unless it delivers enough
  unique value.

## Considered Options

- zsh as Primary Shell: selected.
- Nushell as Primary Shell with zsh/POSIX as Automation Shell: rejected because
  it preserved the AI friction that prompted the investigation.
- both shells supported through generated shared environment configuration:
  rejected because it increased maintenance for unclear daily value.
- Nushell retained only as an optional structured-data tool: rejected for the
  managed baseline; it can be reconsidered later if a concrete workflow proves
  the Tool Fit.

## Decision

No login shell is changed with `chsh`. The repo owns zsh startup files, editor
terminal defaults, and POSIX-compatible automation. Nu may be reintroduced only
through a new ADR that proves a strong Tool Fit.

Use zsh as the primary interactive/editor shell because it reduces friction for
AI agents, vendor docs, bootstrap commands, `just` recipes, and
POSIX-compatible examples. Do not keep Nushell as a first-class shell or
rollback target.

Automation should continue to use POSIX-compatible command text and explicit
tool wrappers. Use `scripts/dev_env.sh` when an AI or non-login command needs
the repo's standard development PATH, and use `scripts/js_toolchain.sh` for
Node, npm, pnpm, Corepack, and JavaScript global tools. Interactive aliases can
exist in zsh for daily convenience, but scripts, recipes, setup docs, and
AI-generated instructions should not depend on those aliases.

## Evidence

Earlier shell parity work recorded that repo-managed editor terminals
previously launched Nu while Codex and `just` usually ran from
zsh/current-process contexts. That split created avoidable friction around
command syntax, `PNPM_HOME`, `.dotnet/tools`, `fnm`, Corepack, and AI CLI
visibility.

The zsh-primary adoption ports the useful former Nu startup behavior into
repo-managed zsh files:

- Homebrew login PATH setup
- expanded `PNPM_HOME`
- `fnm` activation with `--use-on-cd`
- Starship, zoxide, direnv, carapace, and fzf
- `.dotnet/tools` plus the `mise` .NET shim path
- a non-interactive development PATH wrapper for agent/tool command launches
- existing daily aliases for interactive use

## Consequences

VS Code and Ghostty launch zsh by default. Nu editor profiles,
language-specific settings, package declarations, symlink targets, and
repo-managed config files are removed. ADR-0011 later removed Cursor from the
managed editor surface entirely.

Doctor shell parity checks remain read-only by default. Login/startup probes are
still opt-in because they execute user startup files and can run hooks. Doctor
may statically inspect repo-managed zsh files so the shell state is observable
without first mutating home startup files.

Rollback requires a deliberate reinstall and a new source-of-truth update. Do
not restore Nu casually through local-only config.

The trade-off is losing Nu's structured pipeline ergonomics as a default daily
surface. If a future workflow justifies bringing Nu back, it must define how
zsh/POSIX automation, AI command generation, PATH policy, and shell parity stay
in sync.
