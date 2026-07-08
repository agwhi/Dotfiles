# Command Reference

All task automation runs through `just`. Repo-local recipes live in
[`justfile`](../../justfile); system-wide recipes live in
[`system/global-justfile`](../../system/global-justfile) (symlinked to
`~/.justfile`) and are reachable from any directory via the `dotfile` alias
or the shorthand aliases below.

## Repo-local commands (run inside the dotfiles repo)

```bash
just bootstrap                  # Complete laptop setup (alias: just install)
just doctor                     # Read-only Development Ecosystem audit (alias: just audit)
just brew                       # Install Homebrew packages from the Brewfile
just install-personal-brew      # Install gitignored personal packages, if present
just install-vscode-extensions  # Install VS Code extensions (aliases: vscode, editor)
just setup-node                 # Install Node.js LTS plus global tools
just setup-dotnet               # Install mise-managed .NET SDKs and global tools
just setup-aws-cli              # Configure AWS CLI with SSO
just backup                     # Back up current system config to the repo
just link                       # Create symlinks only (alias: link-only)
just backup-and-link            # Back up, then create symlinks
just edit                       # Open the dotfiles folder in VS Code
just repo-lint                  # Lint repo code with Biome
just readme-lint                # Lint README.md
just quality-check              # Delegates to the global quality-check
just security-scan              # Delegates to the global security-scan
just upgrade                    # Delegates to the global upgrade (topgrade)
```

## Global commands (any directory)

Invoke as `dotfile <recipe>` or with the aliases defined in
[`system/zsh/.zshrc`](../../system/zsh/.zshrc):

```bash
# Quality and security
quality        # dotfile quality-check: secret scans + format checks
security       # dotfile security-scan: secret scans only
glint          # dotfile lint: Biome lint (if biome.json exists)
gformat        # dotfile format: Biome format
gdocs          # dotfile docs-lint: markdownlint
gfix           # dotfile fix-formatting

# Environment setup
gnode          # dotfile setup-node
gdotnet        # dotfile setup-dotnet
gaws           # dotfile setup-aws
gupgrade       # dotfile upgrade (topgrade)
gbiome         # dotfile init-biome
ghelp          # dotfile help

# Network security (see docs/how-to/secure-public-networks.md)
secure-on      # DNS encryption + VPN
secure-off     # Disable both
dns-start      # DNS encryption only
dns-stop
vpn-on         # VPN only
vpn-off
dns-test       # Open a DNS leak test
lulu-backup    # Back up LuLu firewall rules
lulu-restore
lulu-list
```

`just --list` (repo) and `ghelp` (global) always show the live recipe list;
prefer them over this page if the two ever disagree.
