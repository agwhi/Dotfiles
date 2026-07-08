#!/bin/sh
# Run JavaScript tools through the ADR-0007 trusted fnm default Node path.

set -eu

if ! command -v fnm >/dev/null 2>&1; then
    echo "fnm not found on PATH; install it with Homebrew before running JS tools." >&2
    exit 127
fi

DOTFILES_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)"
. "$DOTFILES_DIR/system/shell/path.sh"

exec fnm exec --using default "$@"
