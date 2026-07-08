#!/bin/sh
# Read-only .NET migration snapshot for ADR-0006 readiness.

set -eu

DOTFILES_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)"
REPORTS_DIR="${DOTNET_SNAPSHOT_REPORTS_DIR:-$DOTFILES_DIR/reports}"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
REPORT="$REPORTS_DIR/dotnet-migration-snapshot-$TIMESTAMP.md"

umask 077
mkdir -p "$REPORTS_DIR"

is_sensitive_value() {
    value="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
    case "$value" in
        *token* | *secret* | *password* | *passwd* | *credential* | *api_key* | *apikey* | *access_key* | *authorization* | *bearer* | *private_key*)
            return 0
            ;;
    esac
    return 1
}

redact_value() {
    if is_sensitive_value "$1"; then
        printf '[REDACTED]'
    else
        printf '%s' "$1"
    fi
}

append_section() {
    {
        printf '\n## %s\n\n' "$1"
    } >> "$REPORT"
}

capture_cmd() {
    title="$1"
    shift

    append_section "$title"
    {
        printf '```text\n'
        printf '$'
        for arg in "$@"; do
            printf ' %s' "$arg"
        done
        printf '\n'
    } >> "$REPORT"

    set +e
    "$@" >> "$REPORT" 2>&1
    status=$?
    set -e

    {
        printf '\n[exit %s]\n' "$status"
        printf '```\n'
    } >> "$REPORT"
}

capture_shell() {
    title="$1"
    command_text="$2"

    append_section "$title"
    {
        printf '```text\n'
        printf '$ %s\n' "$command_text"
    } >> "$REPORT"

    set +e
    sh -c "$command_text" >> "$REPORT" 2>&1
    status=$?
    set -e

    {
        printf '\n[exit %s]\n' "$status"
        printf '```\n'
    } >> "$REPORT"
}

append_environment_snapshot() {
    append_section "Environment"

    {
        printf '```text\n'
        if [ "${DOTNET_ROOT+x}" = x ]; then
            printf 'DOTNET_ROOT=%s\n' "$(redact_value "$DOTNET_ROOT")"
        else
            printf 'DOTNET_ROOT=<unset>\n'
        fi
        printf '\nPATH entries containing dotnet or mise:\n'
    } >> "$REPORT"

    path_entries="$(
        printf '%s' "${PATH:-}" | awk '
            BEGIN { RS = ":" }
            {
                lowered = tolower($0)
                if (lowered ~ /(dotnet|mise)/) {
                    print $0
                }
            }
        '
    )"

    if [ -n "$path_entries" ]; then
        printf '%s\n' "$path_entries" | while IFS= read -r entry; do
            printf -- '- %s\n' "$(redact_value "$entry")" >> "$REPORT"
        done
    else
        printf -- '- <none>\n' >> "$REPORT"
    fi

    printf '```\n' >> "$REPORT"
}

append_pkgutil_snapshot() {
    append_section "pkgutil .NET Receipts"

    if ! command -v pkgutil >/dev/null 2>&1; then
        printf '```text\npkgutil not available\n```\n' >> "$REPORT"
        return
    fi

    receipts="$(
        pkgutil --pkgs 2>/dev/null | awk '
            {
                lowered = tolower($0)
                if (lowered ~ /(dotnet|netcore|aspnetcore)/) {
                    print $0
                }
            }
        '
    )"

    {
        printf '```text\n'
        if [ -z "$receipts" ]; then
            printf 'No dotnet/netcore/aspnetcore receipts found.\n'
        else
            printf '%s\n' "$receipts"
            printf '\n'
            printf '%s\n' "$receipts" | while IFS= read -r receipt; do
                [ -n "$receipt" ] || continue
                printf -- '--- %s ---\n' "$receipt"
                pkgutil --pkg-info "$receipt" 2>&1
                printf '\n'
            done
        fi
        printf '```\n'
    } >> "$REPORT"
}

append_homebrew_snapshot() {
    append_section "Homebrew .NET And mise Formula State"

    if ! command -v brew >/dev/null 2>&1; then
        printf '```text\nbrew not available\n```\n' >> "$REPORT"
        return
    fi

    {
        printf '```text\n'
        printf 'HOMEBREW_NO_AUTO_UPDATE=1\n'
        for formula in dotnet dotnet@8 mise; do
            printf -- '--- %s ---\n' "$formula"
            if HOMEBREW_NO_AUTO_UPDATE=1 brew list --versions "$formula" 2>/dev/null; then
                :
            else
                printf 'not installed\n'
            fi
            if prefix="$(HOMEBREW_NO_AUTO_UPDATE=1 brew --prefix "$formula" 2>/dev/null)"; then
                printf 'prefix: %s\n' "$prefix"
            fi
            printf '\n'
        done
        printf '```\n'
    } >> "$REPORT"
}

append_presence_snapshot() {
    append_section "Managed Path Presence"

    {
        printf '```text\n'
        for path in "$HOME/.dotnet/tools" "$HOME/.config/mise/config.toml" "$HOME/.local/share/mise"; do
            if [ -e "$path" ] || [ -L "$path" ]; then
                printf '%s: present\n' "$path"
                ls -ld "$path" 2>&1
                if [ -L "$path" ]; then
                    target="$(readlink "$path" 2>/dev/null || true)"
                    printf 'symlink target: %s\n' "$(redact_value "$target")"
                fi
            else
                printf '%s: absent\n' "$path"
            fi
            printf '\n'
        done
        printf '```\n'
    } >> "$REPORT"
}

export DOTNET_CLI_TELEMETRY_OPTOUT="${DOTNET_CLI_TELEMETRY_OPTOUT:-1}"
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE="${DOTNET_SKIP_FIRST_TIME_EXPERIENCE:-1}"
export DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE="${DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE:-1}"
export DOTNET_NOLOGO="${DOTNET_NOLOGO:-1}"

{
    printf '# .NET Migration Snapshot\n\n'
    printf -- '- Created: `%s`\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
    printf -- '- Host: `%s`\n' "$(hostname 2>/dev/null || printf 'unknown')"
    printf -- '- Repo: `%s`\n' "$DOTFILES_DIR"
    printf -- '- Policy: local-only report under ignored `reports/`; do not commit snapshot artifacts.\n'
    printf -- '- Secret handling: full environment is not captured; selected values are redacted when they look sensitive.\n'
} > "$REPORT"

capture_cmd "date" date
capture_shell "command -v dotnet" "command -v dotnet"
capture_cmd "which -a dotnet" which -a dotnet
capture_cmd "dotnet --info" dotnet --info
capture_cmd "dotnet --list-sdks" dotnet --list-sdks
capture_cmd "dotnet --list-runtimes" dotnet --list-runtimes
capture_cmd "dotnet workload list" dotnet workload list
capture_cmd "dotnet tool list --global" dotnet tool list --global
append_environment_snapshot
append_pkgutil_snapshot
append_homebrew_snapshot
append_presence_snapshot

printf 'Snapshot written to %s\n' "$REPORT"
