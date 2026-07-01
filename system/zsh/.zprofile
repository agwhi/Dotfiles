# Repo-managed zsh login setup.
# Keep this file safe for non-interactive login probes.

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

if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

_dotfiles_zsh_path_prepend "/usr/local/bin"
_dotfiles_zsh_path_prepend "/opt/homebrew/sbin"
_dotfiles_zsh_path_prepend "/opt/homebrew/bin"

unfunction _dotfiles_zsh_path_prepend
