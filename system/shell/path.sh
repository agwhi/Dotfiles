# shellcheck shell=sh
# shellcheck disable=SC2088  # literal-tilde case patterns are intentional
# Canonical development PATH and toolchain-env contract.
# Single source of truth, sourced by:
#   - system/zsh/.zshenv, .zprofile, .zshrc
#   - scripts/dev_env.sh, js_toolchain.sh, dotnet_toolchain.sh
# POSIX sh only — no bash/zsh-isms. Safe to source repeatedly: prepends
# deduplicate and re-assert the same precedence, which matters on macOS where
# /etc/zprofile (path_helper) reorders PATH between .zshenv and .zprofile.

# Normalize literal-tilde values that external tools sometimes persist.
case "${PNPM_HOME:-}" in
    "")
        PNPM_HOME="$HOME/Library/pnpm"
        ;;
    "~")
        PNPM_HOME="$HOME"
        ;;
    "~/"*)
        PNPM_HOME="$HOME/${PNPM_HOME#\~/}"
        ;;
esac
export PNPM_HOME

case "${MISE_DATA_DIR:-}" in
    "")
        DOTFILES_MISE_DATA_DIR="$HOME/.local/share/mise"
        ;;
    "~")
        DOTFILES_MISE_DATA_DIR="$HOME"
        ;;
    "~/"*)
        DOTFILES_MISE_DATA_DIR="$HOME/${MISE_DATA_DIR#\~/}"
        ;;
    *)
        DOTFILES_MISE_DATA_DIR="$MISE_DATA_DIR"
        ;;
esac
DOTFILES_MISE_SHIMS_DIR="$DOTFILES_MISE_DATA_DIR/shims"

case "${MISE_DOTNET_ROOT:-}" in
    "")
        DOTFILES_MISE_DOTNET_ROOT="$DOTFILES_MISE_DATA_DIR/dotnet-root"
        ;;
    "~")
        DOTFILES_MISE_DOTNET_ROOT="$HOME"
        ;;
    "~/"*)
        DOTFILES_MISE_DOTNET_ROOT="$HOME/${MISE_DOTNET_ROOT#\~/}"
        ;;
    *)
        DOTFILES_MISE_DOTNET_ROOT="$MISE_DOTNET_ROOT"
        ;;
esac
if [ -d "$DOTFILES_MISE_DOTNET_ROOT" ]; then
    export DOTNET_ROOT="$DOTFILES_MISE_DOTNET_ROOT"
fi

# Prepend a directory to PATH, moving it to the front if already present.
# String-based so it behaves identically in zsh and POSIX sh (zsh does not
# word-split unquoted expansions, so looping over $PATH would not port).
dotfiles_path_prepend() {
    [ -n "$1" ] || return 0
    _dpp_rest="$PATH:"
    _dpp_result=""
    while [ -n "$_dpp_rest" ]; do
        _dpp_seg="${_dpp_rest%%:*}"
        _dpp_rest="${_dpp_rest#*:}"
        if [ -n "$_dpp_seg" ] && [ "$_dpp_seg" != "$1" ]; then
            _dpp_result="$_dpp_result:$_dpp_seg"
        fi
    done
    PATH="$1$_dpp_result"
    unset _dpp_rest _dpp_result _dpp_seg
}

# Canonical precedence — later prepends outrank earlier ones.
dotfiles_path_prepend "/usr/local/bin"
dotfiles_path_prepend "/opt/homebrew/sbin"
dotfiles_path_prepend "/opt/homebrew/bin"
dotfiles_path_prepend "$HOME/.dotnet/tools"
dotfiles_path_prepend "$PNPM_HOME"
dotfiles_path_prepend "$HOME/.local/bin"
dotfiles_path_prepend "$HOME/.local/share/fnm/aliases/default/bin"
dotfiles_path_prepend "$DOTFILES_MISE_SHIMS_DIR"
export PATH
