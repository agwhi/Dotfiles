# config.nu
#
# Installed by:
# version = "0.105.1"
#
# This file is used to override default Nushell settings, define
# (or import) custom commands, or run any other startup tasks.
# See https://www.nushell.sh/book/configuration.html
#
# This file is loaded after env.nu and before login.nu
#
# You can open this file in your default editor using:
# config nu
#
# See `help config nu` for more options
#
# You can remove these comments if you want or leave
# them for future reference.

$env.config.buffer_editor = "nvim"
$env.config.show_banner = false
use std/util "path add"

# Add homebrew
path add "~/.local/bin"
path add "/usr/local/bin"
path add "/opt/homebrew/bin"

# Add starship prompt
mkdir ($nu.data-dir | path join "vendor/autoload")
starship init nu | save -f ($nu.data-dir | path join "vendor/autoload/starship.nu")

# FNM setup
if not (which fnm | is-empty) {
    ^fnm env --json | from json | load-env

    $env.PATH = $env.PATH | prepend ($env.FNM_MULTISHELL_PATH | path join (if $nu.os-info.name == 'windows' {''} else {'bin'}))
    $env.config.hooks.env_change.PWD = (
        $env.config.hooks.env_change.PWD? | append {
            condition: {|| ['.nvmrc' '.node-version', 'package.json'] | any {|el| $el | path exists}}
            code: {|| ^fnm use --install-if-missing}
        }
    )
}

# Add zoxide (cd alternative)
source ~/.zoxide.nu

# Dotnet (brew version)
path add "/opt/homebrew/opt/dotnet@8/bin"
path add $"($env.HOME)/.dotnet/tools"

# Aliases
alias vim = nvim
alias lambda-test = dotnet-lambda-test-tool-8.0
alias fnm-install = fnm install
alias fnm-use = fnm use

# Global justfile aliases
alias dotfile = just --global-justfile
alias gjust = just --global-justfile
alias quality = just --global-justfile quality-check
alias security = just --global-justfile security-scan
alias glint = just --global-justfile lint
alias gformat = just --global-justfile format
alias gdocs = just --global-justfile docs-lint
alias gfix = just --global-justfile fix-formatting
alias gupgrade = just --global-justfile upgrade
alias gnode = just --global-justfile setup-node
alias gdotnet = just --global-justfile setup-dotnet
alias gaws = just --global-justfile setup-aws
alias gbiome = just --global-justfile init-biome
alias ghelp = just --global-justfile help

# Network security aliases
alias secure-on = just --global-justfile secure-mode-on
alias secure-off = just --global-justfile secure-mode-off
alias dns-start = just --global-justfile dns-secure-start
alias dns-stop = just --global-justfile dns-secure-stop
alias vpn-on = just --global-justfile vpn-secure-on
alias vpn-off = just --global-justfile vpn-secure-off
alias dns-test = just --global-justfile dns-leak-test
alias lulu-backup = just --global-justfile lulu-backup
alias lulu-restore = just --global-justfile lulu-restore
alias lulu-list = just --global-justfile lulu-list

# https://carapace-sh.github.io/carapace-bin/setup.html#nushell
source ~/.cache/carapace/init.nu

# Setup direnv for nushell (official nushell approach)
$env.config.hooks.pre_prompt = (
    $env.config.hooks.pre_prompt? | append { ||
        if (which /opt/homebrew/bin/direnv | is-empty) {
            return
        }

        do { /opt/homebrew/bin/direnv export json } | from json | default {} | load-env
        if 'ENV_CONVERSIONS' in $env and 'PATH' in $env.ENV_CONVERSIONS {
            $env.PATH = do $env.ENV_CONVERSIONS.PATH.from_string $env.PATH
        }
    }
)
