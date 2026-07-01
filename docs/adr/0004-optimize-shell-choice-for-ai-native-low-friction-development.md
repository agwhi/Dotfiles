# Optimize Shell Choice For AI-Native Low-Friction Development

Status: accepted for zsh-primary trial.

The shell strategy is now a zsh-primary trial. Repo-managed editor terminals
should launch zsh for Alex's daily interactive development while Nushell remains
installed, declared, symlinked, and available as an optional structured-data
shell.

This is not a Nushell removal decision. Nushell config stays repo-managed under
`system/nushell/`, the Homebrew manifest keeps `nushell`, and no login shell is
changed with `chsh`. Any future Nu removal or cleanup requires explicit approval
after the zsh trial proves parity.

## Considered Options

- zsh as Primary Shell with Nushell retained optionally
- Nushell as Primary Shell with zsh/POSIX as Automation Shell
- both shells supported through generated shared environment configuration
- Nushell retained only as an optional structured-data tool after a later
  cleanup approval

## Decision

Use zsh as the primary interactive/editor shell for the trial because it reduces
friction for AI agents, vendor docs, bootstrap commands, `just` recipes, and
POSIX-compatible examples. Keep Nushell available for structured-data workflows
and as a rollback target.

Automation should continue to use POSIX-compatible command text and explicit
tool wrappers. Interactive aliases can exist in zsh for daily convenience, but
scripts, recipes, setup docs, and AI-generated instructions should not depend on
those aliases.

## Evidence

`docs/plans/shell-parity-and-strategy-plan.md` recorded that repo-managed editor
terminals previously launched Nu while Codex and `just` usually ran from
zsh/current-process contexts. That split created avoidable friction around
command syntax, `PNPM_HOME`, `.dotnet/tools`, `fnm`, Corepack, and AI CLI
visibility.

The zsh-primary trial ports the useful Nu startup behavior into repo-managed
zsh files:

- Homebrew login PATH setup
- expanded `PNPM_HOME`
- `fnm` activation with `--use-on-cd`
- Starship, zoxide, direnv, carapace, and fzf
- `.dotnet/tools` plus the temporary Homebrew `dotnet@8` path
- existing daily aliases for interactive use

## Consequences

VS Code, Cursor, and Ghostty launch zsh by default for the trial. Nu remains a
selectable editor terminal profile and its language/editor settings remain in
place.

Doctor shell parity checks remain read-only by default. Login/startup probes are
still opt-in because they execute user startup files and can run hooks. Doctor
may statically inspect repo-managed zsh files so the trial state is observable
without first mutating home startup files.

Rollback is intentionally small: restore the editor terminal defaults to Nu and
either rerun the symlink flow with previous zsh backups or remove the zsh home
symlinks after restoring the backed-up files. No Nushell install or config state
needs to be recreated because it is retained throughout the trial.
