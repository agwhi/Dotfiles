# Repo-managed interactive zsh setup.

[[ -o interactive ]] || return 0

setopt interactive_comments

_dotfiles_zsh_path_prepend() {
    local entry="$1"
    local current
    local -a new_path

    [[ -n "$entry" ]] || return 0

    new_path=("$entry")
    for current in "${path[@]}"; do
        local normalized_current="${current/#\~/$HOME}"
        [[ -n "$current" && "$current" != "$entry" && "$normalized_current" != "$entry" ]] || continue
        new_path+=("$current")
    done

    path=("${new_path[@]}")
    export PATH
}

_dotfiles_zsh_path_prepend "/usr/local/bin"
_dotfiles_zsh_path_prepend "/opt/homebrew/sbin"
_dotfiles_zsh_path_prepend "/opt/homebrew/bin"
_dotfiles_zsh_path_prepend "/opt/homebrew/opt/dotnet@8/bin"
_dotfiles_zsh_path_prepend "$HOME/.dotnet/tools"
_dotfiles_zsh_path_prepend "$PNPM_HOME"
_dotfiles_zsh_path_prepend "$HOME/.local/bin"

_dotfiles_zsh_has_tty=0
if [[ -t 0 && -t 1 ]]; then
    _dotfiles_zsh_has_tty=1
    autoload -Uz compinit
    compinit -D
fi

if command -v fnm >/dev/null 2>&1; then
    eval "$(fnm env --shell zsh --use-on-cd)"
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
unfunction _dotfiles_zsh_path_prepend
