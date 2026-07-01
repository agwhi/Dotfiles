#!/bin/sh
# MUTATING: install ADR-0006 .NET SDK lines through the repo-managed mise config.

set -eu

DOTFILES_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)"
MISE_CONFIG_FILE="$DOTFILES_DIR/system/mise/config.toml"

if [ ! -f "$MISE_CONFIG_FILE" ]; then
    echo "mise config not found at $MISE_CONFIG_FILE; restore system/mise/config.toml before installing .NET SDKs." >&2
    exit 78
fi

MISE_BIN="${MISE_BIN:-}"
if [ -n "$MISE_BIN" ]; then
    if [ -x "$MISE_BIN" ]; then
        :
    elif command -v "$MISE_BIN" >/dev/null 2>&1; then
        MISE_BIN="$(command -v "$MISE_BIN")"
    else
        echo "MISE_BIN is set to '$MISE_BIN', but that executable was not found." >&2
        exit 127
    fi
fi

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
    echo "mise not found on PATH; install the declared Homebrew mise formula before running this SDK installer." >&2
    exit 127
fi

DOTNET_VERSIONS="$(
    awk '
        /^[[:space:]]*dotnet[[:space:]]*=/ {
            line = $0
            sub(/[[:space:]]*#.*/, "", line)
            sub(/^[^=]*=/, "", line)
            gsub(/[\[\]",]/, " ", line)
            for (i = 1; i <= NF; i++) print $i
        }
    ' "$MISE_CONFIG_FILE"
)"

if [ -z "$DOTNET_VERSIONS" ]; then
    echo "no dotnet SDK lines are declared in $MISE_CONFIG_FILE." >&2
    exit 78
fi

set --
for version in $DOTNET_VERSIONS; do
    case "$version" in
        *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._+-]*)
            echo "unsupported dotnet version token '$version' in $MISE_CONFIG_FILE." >&2
            exit 65
            ;;
    esac
    set -- "$@" "dotnet@$version"
done

export MISE_GLOBAL_CONFIG_FILE="$MISE_CONFIG_FILE"
export DOTNET_CLI_TELEMETRY_OPTOUT="${DOTNET_CLI_TELEMETRY_OPTOUT:-1}"
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE="${DOTNET_SKIP_FIRST_TIME_EXPERIENCE:-1}"
export DOTNET_NOLOGO="${DOTNET_NOLOGO:-1}"

echo "MUTATING: installing ADR-0006 .NET SDK lines through mise: $*" >&2
echo "Using MISE_GLOBAL_CONFIG_FILE=$MISE_GLOBAL_CONFIG_FILE" >&2
echo "No Homebrew dotnet or Microsoft pkg .NET fallback will be used." >&2

exec "$MISE_BIN" install "$@"
