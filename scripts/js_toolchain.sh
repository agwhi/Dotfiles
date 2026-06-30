#!/bin/sh
# Run JavaScript tools through the ADR-0007 trusted fnm default Node path.

set -eu

if ! command -v fnm >/dev/null 2>&1; then
    echo "fnm not found on PATH; install it with Homebrew before running JS tools." >&2
    exit 127
fi

: "${PNPM_HOME:=$HOME/Library/pnpm}"
case "$PNPM_HOME" in
    "~")
        PNPM_HOME=$HOME
        ;;
    "~/"*)
        PNPM_HOME=$HOME/${PNPM_HOME#\~/}
        ;;
esac
export PNPM_HOME
export PATH="$PNPM_HOME:$PATH"

exec fnm exec --using default "$@"
