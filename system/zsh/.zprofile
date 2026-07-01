# Repo-managed zsh login setup.
# Keep this file safe for non-interactive login probes.

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

if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

_dotfiles_zsh_path_prepend "/usr/local/bin"
_dotfiles_zsh_path_prepend "/opt/homebrew/sbin"
_dotfiles_zsh_path_prepend "/opt/homebrew/bin"
_dotfiles_zsh_path_prepend "$HOME/.local/share/fnm/aliases/default/bin"
_dotfiles_zsh_path_prepend "$_dotfiles_mise_shims_dir"

unset _dotfiles_mise_data_dir _dotfiles_mise_shims_dir
unfunction _dotfiles_zsh_path_prepend
