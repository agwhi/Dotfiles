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

case "${MISE_DATA_DIR:-}" in
    "")
        _dotfiles_mise_data_dir="$HOME/.local/share/mise"
        ;;
    "~")
        _dotfiles_mise_data_dir="$HOME"
        ;;
    "~/"*)
        _dotfiles_mise_data_dir="$HOME/${MISE_DATA_DIR#\~/}"
        ;;
    *)
        _dotfiles_mise_data_dir="$MISE_DATA_DIR"
        ;;
esac
_dotfiles_mise_shims_dir="$_dotfiles_mise_data_dir/shims"

case "${MISE_DOTNET_ROOT:-}" in
    "")
        _dotfiles_mise_dotnet_root="$_dotfiles_mise_data_dir/dotnet-root"
        ;;
    "~")
        _dotfiles_mise_dotnet_root="$HOME"
        ;;
    "~/"*)
        _dotfiles_mise_dotnet_root="$HOME/${MISE_DOTNET_ROOT#\~/}"
        ;;
    *)
        _dotfiles_mise_dotnet_root="$MISE_DOTNET_ROOT"
        ;;
esac
if [[ -d "$_dotfiles_mise_dotnet_root" ]]; then
    export DOTNET_ROOT="$_dotfiles_mise_dotnet_root"
fi

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

_dotfiles_zsh_path_prepend "$HOME/.dotnet/tools"
_dotfiles_zsh_path_prepend "$PNPM_HOME"
_dotfiles_zsh_path_prepend "$HOME/.local/bin"
_dotfiles_zsh_path_prepend "$HOME/.local/share/fnm/aliases/default/bin"
_dotfiles_zsh_path_prepend "/opt/homebrew/opt/dotnet@8/bin"
_dotfiles_zsh_path_prepend "$_dotfiles_mise_shims_dir"

unset _dotfiles_mise_data_dir _dotfiles_mise_shims_dir _dotfiles_mise_dotnet_root
unfunction _dotfiles_zsh_path_prepend
