# Zsh Primary Trial Plan

Date: 2026-07-01.

This plan implements a reversible zsh-primary trial. It adds repo-managed zsh
startup files, points editor terminals at zsh, and keeps Nushell installed and
repo-managed until Alex explicitly approves any cleanup.

## Trial Scope

- zsh becomes the default integrated terminal shell for VS Code, Cursor, and
  Ghostty.
- Nushell remains available through the Nu editor profile, Homebrew, and
  `system/nushell/config.nu` plus `system/nushell/env.nu`.
- Existing Nu language/editor settings remain unchanged.
- No login shell is changed with `chsh`.
- No Nushell files, packages, symlinks, or install state are removed.

## Feature Mapping

<!-- markdownlint-disable MD013 -->

| Nu feature | zsh equivalent | Status | Notes |
| --- | --- | --- | --- |
| `$env.config.buffer_editor = "nvim"` | `EDITOR=nvim` and `VISUAL=nvim` in `system/zsh/.zshenv` | Recreated | Safe for non-interactive zsh probes. |
| `show_banner = false` | None | Not needed | zsh has no comparable startup banner in this setup. |
| Homebrew paths | `brew shellenv` in `system/zsh/.zprofile`, plus Homebrew bin/sbin PATH guards | Recreated | Login-safe and keeps fzf/completion out of `.zprofile`. |
| `PNPM_HOME` | `PNPM_HOME="$HOME/Library/pnpm"` in `system/zsh/.zshenv` | Improved | Removes the literal `~/Library/pnpm` value from zsh startup. |
| Starship | `eval "$(starship init zsh)"` in interactive `.zshrc` | Recreated | Only runs when `starship` is installed. |
| `fnm` | `eval "$(fnm env --shell zsh --use-on-cd)"` in interactive `.zshrc` | Recreated | Keeps project version switching in interactive zsh. |
| zoxide | `eval "$(zoxide init zsh)"` in interactive `.zshrc` | Recreated | Loaded late, matching the intended interactive behavior. |
| `.dotnet/tools` | `$HOME/.dotnet/tools` PATH prepend in `.zshenv` and `.zshrc` | Improved | Uses an expanded path so global tools resolve in zsh. |
| temporary `dotnet@8` path | `/opt/homebrew/opt/dotnet@8/bin` PATH prepend | Recreated | Temporary until the separate `mise` .NET migration is approved and implemented. |
| Carapace | `CARAPACE_BRIDGES` and `source <(carapace _carapace zsh)` | Recreated | Interactive only. |
| direnv | `eval "$(direnv hook zsh)"` | Recreated | Interactive only. |
| fzf | `source <(fzf --zsh)` guarded by interactive zle availability | Improved | Avoids the previous non-interactive zle warnings. |
| Nu aliases | zsh aliases in interactive `.zshrc` | Improved | Daily convenience only; both shells use `just --global-justfile` so recipes run from the caller's project directory. |

<!-- markdownlint-enable MD013 -->

## Nu-Only Non-Goals

- Do not port Nushell structured pipelines, table rendering, or typed data
  exploration into zsh. Nu remains the better optional shell for those jobs.
- Do not make automation depend on zsh aliases or interactive shell startup.
- Do not migrate .NET to `mise` in this trial.
- Do not remove Homebrew `node`, Homebrew `pnpm`, Microsoft package .NET,
  Homebrew `dotnet@8`, Pi, opencode, Claude, Codex, APM, or AI asset state.

## Rollback

1. Change `terminal.integrated.defaultProfile.osx` in
   `system/vscode/settings.jsonc` and `system/cursor/settings.jsonc` back to
   `nu`.
2. Change `system/ghostty/config` back to `command = /opt/homebrew/bin/nu`.
3. If zsh home symlinks were applied, restore `~/.zshenv`, `~/.zprofile`, and
   `~/.zshrc` from the latest `backups/<timestamp>/` entry, or rerun the
   symlink flow after reverting the repo zsh files.
4. Restart editor terminals.

Nushell does not need reinstalling during rollback because its package and
repo-managed config are retained.

## Acceptance Criteria

- Nushell remains installed, declared, and symlinked.
- zsh config is repo-managed under `system/zsh/` and symlink-ready.
- `setup_symlinks.sh` creates a stable `~/.dotfiles` shortcut when the repo is
  cloned elsewhere, because global just recipes use that path.
- Nu and zsh global just aliases preserve the caller's current project
  directory.
- zsh non-interactive startup does not emit fzf or zle warnings from the
  repo-managed files.
- VS Code, Cursor, and Ghostty default to zsh for the trial.
- Current Nu features have zsh equivalents or explicit non-goals.
- Doctor can observe the zsh trial state without mutating startup files by
  default.
- Rollback to Nu editor terminals is documented and limited to editor defaults
  plus optional zsh symlink restoration.

## Validation Plan

<!-- markdownlint-disable MD013 -->

- `git diff --check`
- `bash -n scripts/setup_symlinks.sh scripts/js_toolchain.sh`
- `zsh -n system/zsh/.zshenv system/zsh/.zprofile system/zsh/.zshrc`
- `/bin/zsh -fc 'source system/zsh/.zshenv 2>/dev/null || true; print -r -- ok'`
- `/bin/zsh -lic 'echo ok'`
- `just --list`
- `~/.dotfiles/scripts/js_toolchain.sh markdownlint --version`
- `just doctor --json | python3 -m json.tool >/dev/null`
- `DOTFILES_DOCTOR_ALLOW_STARTUP_PROBES=1 just doctor --json | python3 -m json.tool >/dev/null`
- `nu --no-config-file --commands 'nu-check system/nushell/env.nu; nu-check system/nushell/config.nu; print ok'`
- `./scripts/js_toolchain.sh markdownlint docs/plans/zsh-primary-trial-plan.md docs/adr/0004-optimize-shell-choice-for-ai-native-low-friction-development.md`
- `ripsecrets --strict-ignore .`
- `gitleaks detect --source . --no-git --redact --no-banner`

<!-- markdownlint-enable MD013 -->

## Open Followups

- Decide after the trial whether zsh should remain primary.
- If zsh stays primary, update Cursor rules and README shell language that still
  describe Nu as the default shell.
- Design the shared shell-neutral environment source instead of hand-maintained
  Nu and zsh fragments.
- Run live command checks inside VS Code and Cursor terminals after restarting
  those apps.
