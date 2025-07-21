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
            code: {|| ^fnm use}
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

# Global justfile aliases
alias dotfile = just $'--justfile=($env.HOME)/.justfile'
alias gjust = just $'--justfile=($env.HOME)/.justfile'
alias quality = just $'--justfile=($env.HOME)/.justfile' quality-check
alias security = just $'--justfile=($env.HOME)/.justfile' security-scan
alias glint = just $'--justfile=($env.HOME)/.justfile' lint
alias gformat = just $'--justfile=($env.HOME)/.justfile' format
alias gdocs = just $'--justfile=($env.HOME)/.justfile' docs-lint
alias gfix = just $'--justfile=($env.HOME)/.justfile' fix-formatting
alias gupgrade = just $'--justfile=($env.HOME)/.justfile' upgrade
alias gnode = just $'--justfile=($env.HOME)/.justfile' setup-node
alias gdotnet = just $'--justfile=($env.HOME)/.justfile' setup-dotnet
alias gaws = just $'--justfile=($env.HOME)/.justfile' setup-aws
alias gbiome = just $'--justfile=($env.HOME)/.justfile' init-biome
alias ghelp = just $'--justfile=($env.HOME)/.justfile' help

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
