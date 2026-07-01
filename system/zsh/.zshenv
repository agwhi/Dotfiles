# Repo-managed zsh environment.
# Keep this file safe for every zsh invocation, including non-interactive scripts.

export EDITOR="${EDITOR:-nvim}"
export VISUAL="${VISUAL:-nvim}"

case "${PNPM_HOME:-}" in
    "")
        export PNPM_HOME="$HOME/Library/pnpm"
        ;;
    "~")
        export PNPM_HOME="$HOME"
        ;;
    "~/"*)
        export PNPM_HOME="$HOME/${PNPM_HOME#\~/}"
        ;;
    *)
        export PNPM_HOME
        ;;
esac

_dotfiles_zsh_path_prepend() {
    local entry="$1"
    local current
    local -a new_path

    [[ -n "$entry" ]] || return 0

    new_path=("$entry")
    for current in "${path[@]}"; do
        [[ -n "$current" && "$current" != "$entry" ]] || continue
        new_path+=("$current")
    done

    path=("${new_path[@]}")
    export PATH
}

_dotfiles_zsh_path_prepend "$HOME/.dotnet/tools"
_dotfiles_zsh_path_prepend "$PNPM_HOME"
_dotfiles_zsh_path_prepend "/opt/homebrew/opt/dotnet@8/bin"

unfunction _dotfiles_zsh_path_prepend
