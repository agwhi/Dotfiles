# Repo-managed zsh environment.
# Keep this file safe for every zsh invocation, including non-interactive scripts.

export EDITOR="${EDITOR:-nvim}"
export VISUAL="${VISUAL:-nvim}"

# PATH and toolchain env come from the single shared contract.
if [[ -r "$HOME/.dotfiles/system/shell/path.sh" ]]; then
    . "$HOME/.dotfiles/system/shell/path.sh"
fi
