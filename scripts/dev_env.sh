#!/bin/sh
# Run a command with the repo's non-interactive development PATH contract.

set -eu

if [ "$#" -eq 0 ]; then
    echo "usage: dev_env.sh <command> [args...]" >&2
    exit 64
fi

DOTFILES_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)"
. "$DOTFILES_DIR/system/shell/path.sh"

exec "$@"
