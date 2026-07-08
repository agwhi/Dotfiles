# Repo-managed zsh login setup.
# Keep this file safe for non-interactive login probes.

if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

# Re-assert the shared PATH contract: macOS /etc/zprofile (path_helper)
# reordered PATH after .zshenv ran.
if [[ -r "$HOME/.dotfiles/system/shell/path.sh" ]]; then
    . "$HOME/.dotfiles/system/shell/path.sh"
fi
