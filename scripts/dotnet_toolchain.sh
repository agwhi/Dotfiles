#!/bin/sh
# Run .NET commands through the ADR-0006 mise-managed SDK context.

set -eu

if [ "$#" -eq 0 ]; then
    echo "usage: dotnet_toolchain.sh <command> [args...]" >&2
    exit 64
fi

DOTFILES_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)"
MISE_CONFIG_FILE="${MISE_GLOBAL_CONFIG_FILE:-$DOTFILES_DIR/system/mise/config.toml}"

MISE_BIN="${MISE_BIN:-}"
if [ -z "$MISE_BIN" ]; then
    for candidate in "$HOME/.local/bin/mise" /opt/homebrew/bin/mise /usr/local/bin/mise; do
        if [ -x "$candidate" ]; then
            MISE_BIN="$candidate"
            break
        fi
    done
fi
if [ -z "$MISE_BIN" ] && command -v mise >/dev/null 2>&1; then
    MISE_BIN="$(command -v mise)"
fi
if [ -z "$MISE_BIN" ]; then
    echo "mise not found on PATH; install the declared Homebrew mise formula before running .NET tools." >&2
    exit 127
fi
if [ ! -f "$MISE_CONFIG_FILE" ]; then
    echo "mise config not found at $MISE_CONFIG_FILE; run just link-only or restore system/mise/config.toml." >&2
    exit 78
fi

export MISE_GLOBAL_CONFIG_FILE="$MISE_CONFIG_FILE"
export MISE_AUTO_INSTALL="${MISE_AUTO_INSTALL:-0}"
export MISE_PREFER_OFFLINE="${MISE_PREFER_OFFLINE:-1}"
export DOTNET_CLI_TELEMETRY_OPTOUT="${DOTNET_CLI_TELEMETRY_OPTOUT:-1}"
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE="${DOTNET_SKIP_FIRST_TIME_EXPERIENCE:-1}"
export DOTNET_NOLOGO="${DOTNET_NOLOGO:-1}"

# DOTNET_ROOT (and the rest of the toolchain env) comes from the shared contract.
. "$DOTFILES_DIR/system/shell/path.sh"

if ! "$MISE_BIN" which dotnet >/dev/null 2>&1; then
    echo "mise is available, but ADR-0006 .NET SDKs are not installed or active yet." >&2
    echo "Run an approved SDK installation step for dotnet@10 and dotnet@8 before using this wrapper." >&2
    exit 69
fi

exec "$MISE_BIN" exec -- "$@"
