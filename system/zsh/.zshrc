# Repo-managed interactive zsh setup.

[[ -o interactive ]] || return 0

setopt interactive_comments

# Re-assert the shared PATH contract for interactive shells.
if [[ -r "$HOME/.dotfiles/system/shell/path.sh" ]]; then
    . "$HOME/.dotfiles/system/shell/path.sh"
fi

_dotfiles_zsh_has_tty=0
if [[ -t 0 && -t 1 ]]; then
    _dotfiles_zsh_has_tty=1
    autoload -Uz compinit
    compinit -D
fi

if command -v fnm >/dev/null 2>&1; then
    eval "$(fnm env --shell zsh --use-on-cd)"
fi
# fnm env prepends its session dir; keep mise shims ahead of it.
if command -v dotfiles_path_prepend >/dev/null 2>&1; then
    dotfiles_path_prepend "$DOTFILES_MISE_SHIMS_DIR"
fi

if command -v direnv >/dev/null 2>&1; then
    eval "$(direnv hook zsh)"
fi

export CARAPACE_BRIDGES="${CARAPACE_BRIDGES:-zsh,fish,bash,inshellisense}"
if (( _dotfiles_zsh_has_tty )) && command -v carapace >/dev/null 2>&1; then
    source <(carapace _carapace zsh)
fi

if (( _dotfiles_zsh_has_tty )) && command -v fzf >/dev/null 2>&1 && [[ -o zle ]]; then
    source <(fzf --zsh)
fi

alias vim='nvim'
alias lambda-test='dotnet-lambda-test-tool-8.0'
alias fnm-install='fnm install'
alias fnm-use='fnm use'

alias dotfile='just --global-justfile'
alias gjust='just --global-justfile'
alias quality='just --global-justfile quality-check'
alias security='just --global-justfile security-scan'
alias glint='just --global-justfile lint'
alias gformat='just --global-justfile format'
alias gdocs='just --global-justfile docs-lint'
alias gfix='just --global-justfile fix-formatting'
alias gupgrade='just --global-justfile upgrade'
alias gnode='just --global-justfile setup-node'
alias gdotnet='just --global-justfile setup-dotnet'
alias gaws='just --global-justfile setup-aws'
alias gbiome='just --global-justfile init-biome'
alias ghelp='just --global-justfile help'

alias secure-on='just --global-justfile secure-mode-on'
alias secure-off='just --global-justfile secure-mode-off'
alias dns-start='just --global-justfile dns-secure-start'
alias dns-stop='just --global-justfile dns-secure-stop'
alias vpn-on='just --global-justfile vpn-secure-on'
alias vpn-off='just --global-justfile vpn-secure-off'
alias dns-test='just --global-justfile dns-leak-test'
alias lulu-backup='just --global-justfile lulu-backup'
alias lulu-restore='just --global-justfile lulu-restore'
alias lulu-list='just --global-justfile lulu-list'

if command -v zoxide >/dev/null 2>&1; then
    eval "$(zoxide init zsh)"
fi

if (( _dotfiles_zsh_has_tty )) && [[ ${TERM:-} != dumb ]] && command -v starship >/dev/null 2>&1; then
    eval "$(starship init zsh)"
fi

unset _dotfiles_zsh_has_tty
