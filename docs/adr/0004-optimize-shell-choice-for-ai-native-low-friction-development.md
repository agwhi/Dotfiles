# Optimize Shell Choice For AI-Native Low-Friction Development

Status: accepted.

The shell strategy is zsh-primary. Repo-managed editor terminals launch zsh for
Alex's daily interactive development, and Nushell is removed from the managed
development ecosystem.

No login shell is changed with `chsh`. The repo owns zsh startup files, editor
terminal defaults, and POSIX-compatible automation. Nu may be reintroduced only
through a new ADR that proves a strong Tool Fit.

## Considered Options

- zsh as Primary Shell
- Nushell as Primary Shell with zsh/POSIX as Automation Shell
- both shells supported through generated shared environment configuration
- Nushell retained only as an optional structured-data tool

## Decision

Use zsh as the primary interactive/editor shell because it reduces friction for
AI agents, vendor docs, bootstrap commands, `just` recipes, and
POSIX-compatible examples. Do not keep Nushell as a first-class shell or
rollback target.

Automation should continue to use POSIX-compatible command text and explicit
tool wrappers. Interactive aliases can exist in zsh for daily convenience, but
scripts, recipes, setup docs, and AI-generated instructions should not depend on
those aliases.

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
- `.dotnet/tools` plus the temporary Homebrew `dotnet@8` path
- existing daily aliases for interactive use

## Consequences

VS Code, Cursor, and Ghostty launch zsh by default. Nu editor profiles,
language-specific settings, package declarations, symlink targets, and
repo-managed config files are removed.

Doctor shell parity checks remain read-only by default. Login/startup probes are
still opt-in because they execute user startup files and can run hooks. Doctor
may statically inspect repo-managed zsh files so the shell state is observable
without first mutating home startup files.

Rollback requires a deliberate reinstall and a new source-of-truth update. Do
not restore Nu casually through local-only config.
