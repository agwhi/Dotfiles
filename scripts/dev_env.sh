#!/bin/sh
# Run a command with the repo's non-interactive development PATH contract.

set -eu

if [ "$#" -eq 0 ]; then
    echo "usage: dev_env.sh <command> [args...]" >&2
    exit 64
fi

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
        MISE_DATA_DIR="$HOME/.local/share/mise"
        ;;
    "~")
        MISE_DATA_DIR="$HOME"
        ;;
    "~/"*)
        MISE_DATA_DIR="$HOME/${MISE_DATA_DIR#\~/}"
        ;;
esac
MISE_SHIMS_DIR="$MISE_DATA_DIR/shims"

case "${MISE_DOTNET_ROOT:-}" in
    "")
        MISE_DOTNET_ROOT="$MISE_DATA_DIR/dotnet-root"
        ;;
    "~")
        MISE_DOTNET_ROOT="$HOME"
        ;;
    "~/"*)
        MISE_DOTNET_ROOT="$HOME/${MISE_DOTNET_ROOT#\~/}"
        ;;
esac
if [ -d "$MISE_DOTNET_ROOT" ]; then
    export DOTNET_ROOT="$MISE_DOTNET_ROOT"
fi

path_prepend() {
    entry="$1"
    [ -n "$entry" ] || return 0
    [ -d "$entry" ] || return 0

    new_path="$entry"
    old_ifs="$IFS"
    IFS=:
    for current in $PATH; do
        [ -n "$current" ] || continue
        case "$current" in
            "~")
                normalized="$HOME"
                ;;
            "~/"*)
                normalized="$HOME/${current#\~/}"
                ;;
            *)
                normalized="$current"
                ;;
        esac
        if [ "$current" = "$entry" ] || [ "$normalized" = "$entry" ]; then
            continue
        fi
        new_path="$new_path:$current"
    done
    IFS="$old_ifs"
    PATH="$new_path"
}

path_prepend "/usr/local/bin"
path_prepend "/opt/homebrew/sbin"
path_prepend "/opt/homebrew/bin"
path_prepend "$HOME/.dotnet/tools"
path_prepend "$PNPM_HOME"
path_prepend "$HOME/.local/bin"
path_prepend "$HOME/.local/share/fnm/aliases/default/bin"
path_prepend "$MISE_SHIMS_DIR"
export PATH

exec "$@"
