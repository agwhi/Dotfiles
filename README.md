# 💻 Dotfiles Setup – macOS Dev Environment

A carefully curated developer setup for Node.js (via pnpm), .NET 8 (C#), TypeScript (CDK + Serverless), and React/Next.js on macOS, designed to maximise dev experience and developer security with a fast, consistent toolchain.

This repository manages your macOS development environment through dotfiles, providing a unified setup for all your development tools and configurations.

---

## 🎯 Philosophy

- **Global-first**: Everything here is set up globally (not repo-specific)
- **Speed & Clarity**: We favour tools that reduce friction and are fast to use
- **Terminal native**: Most tools are CLI or TUI based, Rust-preferred if options exist
- **Single source of truth**: All config is tracked, versioned, and symlinked
- **Secure by default**: DevSecOps from day one

---

## 🚀 Quick Start

### 1. Install Prerequisites

Run the install script to set up Homebrew, just, and other requirements:

```bash
./install.sh
```

### 2. Set Up Your Environment

Run the full setup to install all packages and create symlinks:

```bash
just setup
```

This will:
- Install all Homebrew packages from `Brewfile`
- Install VS Code extensions
- Back up existing config files
- Create symlinks to your dotfiles

### 3. Available Commands

```bash
just setup                  # Full setup: install packages and create symlinks
just brew                  # Install all Homebrew packages from Brewfile
just backup                # Back up current system config to repo
just edit                  # Open dotfiles folder in Cursor editor
just upgrade               # Update all packages and tools
just --list                # Show all available commands
```

---

## 🛠️ Tools by Category

### 🖥 Terminal + Shell

| Tool       | Description                               |
| ---------- | ----------------------------------------- |
| [Ghostty]  | Terminal emulator (fast, GPU-accelerated) |
| [Nushell]  | Smart shell with structured data support  |
| [Starship] | Minimal, fast prompt                      |
| [Carapace] | Completion engine for CLIs                |
| [Zoxide]   | Smarter `cd`                              |
| [fzf]      | Fuzzy finder                              |
| [fd]       | Better `find`                             |
| [bat]      | Syntax-highlighted `cat`                  |
| [topgrade] | One command to update everything          |

### 📦 Package Managers

| Tool       | Description                                      |
| ---------- | ------------------------------------------------ |
| [Homebrew] | macOS-native package manager                     |
| [pnpm]     | Preferred Node.js package manager (via Corepack) |
| [fnm]      | Fast Node.js version manager                     |
| [cargo]    | Rust package manager (used for many tools)       |

### ✨ Editor / IDE

| Tool      | Description                               |
| --------- | ----------------------------------------- |
| [Neovim]  | For terminal editing                      |
| [VS Code] | Main GUI IDE                              |
| [Cursor]  | AI-assisted development with custom rules |

### 🚀 Productivity & Launchers

| Tool      | Description                                |
| --------- | ------------------------------------------ |
| [Raycast] | Spotlight replacement w/ dev tools support |

### 🌐 AWS / Cloud Dev

| Tool                        | Description           |
| --------------------------- | --------------------- |
| [awscli]                    | AWS CLI               |
| [cdk]                       | AWS CDK (TypeScript)  |
| [cdk-dia]                   | CDK diagram generator |
| [aws-lambda-tools-defaults] | .NET Lambda tooling   |

### 🔒 DevSecOps

| Tool                   | Description                               |
| ---------------------- | ----------------------------------------- |
| [ripsecrets]           | Fast secret scanner for commits           |
| [gitleaks]             | Deep secret scanning with rulesets        |
| [direnv]               | Auto loads `.envrc` files per directory   |
| [dotenv-linter]        | Lint `.env` files globally                |
| [repolinter]           | Validates repo conventions (run manually) |
| [editorconfig-checker] | Ensures consistent editor settings        |
| [qlty]                 | Global quality checks across repos        |

---

## 🔧 Setup & Management

### Symlink Setup

All configs are symlinked into correct system paths to maintain this repo as the single source of truth:

```bash
just link
```

The setup script (`setup_symlinks.sh`) safely:
- Backs up existing config files to `.backup` versions
- Creates symlinks from dotfiles repo to system locations
- Logs all actions to `symlink-backups.txt`
- Handles idempotent re-runs safely
- Uses robust path resolution for symlink verification

### Backup System

**Backup current system state:**

```bash
just backup
```

This runs `backup.sh` which:
- Backs up non-symlinked files to the repo
- Updates `Brewfile` with current Homebrew packages
- Updates `vscode/extensions.txt` with current VS Code extensions
- Logs all actions to `backup-log.txt`

**Backup logs:**
- `symlink-backups.txt` - Log of symlink creation and backups
- `backup-log.txt` - Log of system state backups

### Git Configuration

Symlink `.gitconfig` globally and separate sensitive config:

```bash
cp git/.gitconfig.local.example ~/.gitconfig.local
just link
```

**Structure:**

- `git/gitconfig` → `~/.gitconfig` (safe to commit)
- `~/.gitconfig.local` (personal credentials, not committed)
- `git/.gitconfig.local.example` (template for new machines)

### Backup & Upgrade

**Upgrade everything:**

```bash
topgrade
```

**Available Commands:**

```bash
just setup                  # Full setup: install packages and create symlinks
just brew                  # Install all Homebrew packages from Brewfile
just backup                # Back up current system config to repo
just edit                  # Open dotfiles folder in Cursor editor
just upgrade               # Update all packages and tools
just link                  # Set up all dotfile symlinks only
just install-vscode-extensions # Install VS Code extensions only
```

**Backup non-symlinked files:**

```bash
just backup
```

Updates `Brewfile` and `vscode/extensions.txt` (symlinked files are already tracked).

---

## 🧱 Structure

```
dotfiles/
├── .config/                 # Global config directory
│   ├── starship.toml       # Starship prompt configuration
│   └── nvim/               # Neovim configuration
│       └── init.lua        # Neovim initialization script
├── .cursor/                 # Cursor editor configuration
│   └── rules/              # AI context rules for development
├── aws/                     # AWS CLI configuration
│   └── config
├── ghostty/                 # Ghostty terminal configuration
│   └── config
├── git/                     # Git configuration
│   ├── gitconfig           # Global git config
│   ├── gitconfig.local.example # Template for local git config
│   └── gitignore_global    # Global gitignore
├── nushell/                 # Nushell shell configuration
│   ├── config.nu           # Main shell config
│   └── env.nu              # Environment variables
├── vscode/                  # VS Code configuration
│   ├── settings.json       # VS Code settings
│   └── extensions.txt      # VS Code extensions list
├── .editorconfig           # Editor configuration for consistent formatting
├── .gitignore              # Git ignore rules
├── Brewfile                # Homebrew packages and apps
├── LICENSE                 # MIT License
├── backup.sh               # System backup script
├── backup-log.txt          # Backup operation logs
├── install.sh              # Prerequisites installer
├── justfile                # Task automation
├── README.md               # This documentation
├── setup_symlinks.sh       # Symlink creation script
└── symlink-backups.txt     # Symlink operation logs
```

---

## 🤖 AI Usage & Cursor Rules

This repository uses [Cursor](https://cursor.com) with custom `.cursor/rules` to ensure consistency and alignment with our philosophy. These rules are automatically applied when working in this repository and provide AI context for development decisions.

### Rule Categories

The `.cursor/rules/` directory contains specialized rules for different areas:

| Rule File | Purpose | Based on Section |
|-----------|---------|------------------|
| `global-meta.mdc` | Overall repository philosophy and structure | 🎯 Philosophy |
| `terminal-shell.mdc` | Shell and terminal tooling decisions | 🖥 Terminal + Shell |
| `editor-config.mdc` | Editor and IDE configuration | ✨ Editor / IDE |
| `backup-upgrade.mdc` | Backup and upgrade strategies | 🔧 Setup & Management |
| `dotfile-management.mdc` | Dotfile organization and symlinks | 🔧 Setup & Management |
| `devsecops-security.mdc` | Security and DevSecOps practices | 🔒 DevSecOps |
| `biome-linting.mdc` | Code formatting and linting | 🔒 DevSecOps |
| `language-dotnet.mdc` | .NET 8 and AWS Lambda development | 🌐 AWS / Cloud Dev |
| `justfile-bootstrap.mdc` | Task automation and justfile usage | 🔧 Setup & Management |
| `shell-env.mdc` | Shell environment configuration | 🖥 Terminal + Shell |
| `docs-lint.mdc` | Documentation standards | 📋 Documentation |

### How Rules Work

These rules are automatically loaded by Cursor when you open this repository and provide context for:
- Tool selection and configuration decisions
- Code style and formatting preferences
- Security and best practices
- Development workflow patterns

### Contributor Guidelines

1. Check if tools/settings are already listed in the README
2. Update relevant sections when adding new tools
3. Use Cursor rules as a consistency checklist
4. Rules are automatically enforced - follow the guidance they provide

---

<!-- Reference link definitions for table links -->

[Ghostty]: https://ghostty.app
[Nushell]: https://www.nushell.sh
[Starship]: https://starship.rs
[Carapace]: https://github.com/rsteube/carapace
[Zoxide]: https://github.com/ajeetdsouza/zoxide
[fzf]: https://github.com/junegunn/fzf
[fd]: https://github.com/sharkdp/fd
[bat]: https://github.com/sharkdp/bat
[Homebrew]: https://brew.sh
[pnpm]: https://pnpm.io
[fnm]: https://github.com/Schniz/fnm
[cargo]: https://doc.rust-lang.org/cargo/
[Neovim]: https://neovim.io
[VS Code]: https://code.visualstudio.com
[Cursor]: https://cursor.com
[Raycast]: https://www.raycast.com
[awscli]: https://aws.amazon.com/cli
[cdk]: https://docs.aws.amazon.com/cdk/
[cdk-dia]: https://github.com/pistazie/cdk-dia
[aws-lambda-tools-defaults]: https://github.com/aws/aws-extensions-for-dotnet-cli
[ripsecrets]: https://github.com/snickdx/ripsecrets
[gitleaks]: https://github.com/gitleaks/gitleaks
[direnv]: https://direnv.net
[dotenv-linter]: https://dotenv-linter.github.io
[repolinter]: https://github.com/todogroup/repolinter
[editorconfig-checker]: https://editorconfig-checker.github.io
[qlty]: https://github.com/yoheimuta/qlty
[topgrade]: https://github.com/r-darwish/topgrade
