# 💻 Dotfiles Setup – macOS Dev Environment

A carefully curated developer setup for Node.js (via pnpm), .NET 8 (C#),
TypeScript (CDK + Serverless), and React/Next.js on macOS, designed to
maximise dev experience and developer security with a fast, consistent
toolchain.

This repository manages your macOS development environment through dotfiles,
providing a unified setup for all your development tools and configurations.

---

## 🎯 Philosophy

This dotfiles repository follows a carefully considered philosophy for
building a productive, secure, and maintainable development environment:

### **Global-first Approach**

Everything here is set up globally (not repo-specific) to provide a
consistent experience across all projects. This includes:

- **Editor configurations** that work everywhere
- **Global tools** that are always available
- **Shell environment** that's consistent across terminals
- **Security tools** that protect all your work

### **Speed & Clarity**

We favor tools that reduce friction and are fast to use:

- **Rust-based tools** (fd, bat, ripgrep, topgrade) for performance
- **Just task runner** for simple, fast automation
- **Nushell** for structured data and better scripting
- **Minimal prompts** (Starship) that don't slow down your workflow

### **Terminal Native**

Most tools are CLI or TUI based, with Rust-preferred when options exist:

- **CLI-first** approach for automation and scripting
- **TUI tools** for interactive tasks (fzf, fd)
- **Rust ecosystem** for performance-critical tools
- **Cross-platform** compatibility where possible

### **Single Source of Truth**

All config is tracked, versioned, and symlinked:

- **Version controlled** configurations
- **Symlinked** from dotfiles to system locations
- **Backup system** for existing configurations
- **Idempotent** setup scripts

### **Secure by Default**

DevSecOps from day one with built-in security:

- **Secret scanning** (ripsecrets, gitleaks) for all commits
- **Environment management** (direnv) for secure config
- **Global gitignore** for sensitive files
- **Security tools** integrated into daily workflow

---

## 🚀 Quick Start

### Prerequisites

- macOS (tested on macOS 14+)
- Git installed
- Administrator access (for Homebrew installation)

### 1. Clone and Install Prerequisites

```bash
# Clone this repository
git clone <your-repo-url> ~/.dotfiles
cd ~/.dotfiles

# Install Homebrew, just, and other requirements
./install.sh
```

### 2. Set Up Your Environment

```bash
# Complete laptop bootstrap: install packages and create symlinks
just bootstrap
```

This comprehensive setup will:

- Install all Homebrew packages from `Brewfile`
- Install VS Code extensions
- Install Node.js LTS and global tools (Biome, AWS CDK)
- Install .NET 8 and Lambda tools
- Configure security tools and direnv
- Back up existing config files to `backups/`
- Create symlinks from dotfiles to system locations

### 3. Verify Installation

```bash
# Check that everything is working
just quality-check
just security-scan
```

### 4. Essential Commands

```bash
just bootstrap              # Complete laptop setup (alias: just install)
just brew                  # Install all Homebrew packages from Brewfile
just backup                # Back up current system config to repo
just edit                  # Open dotfiles folder in Cursor editor
just upgrade               # Update all packages and tools
just vscode                # Install VS Code extensions (alias: just editor)
just link-only             # Create symlinks only
just --list                # Show all available commands
```

### 5. Next Steps

After bootstrap, you can:

- **Configure AWS CLI**: `just setup-aws-cli`
- **Set up Git config**: Copy `git/gitconfig.local.example` to
  `~/.gitconfig.local`
- **Restart your terminal** to load all shell changes
- **Customize your setup**: Edit configuration files in the dotfiles
  directory

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

**Cursor Configuration:**

- `system/cursor/settings.jsonc` - Enforces 4-space indentation, LF line
  endings, and format-on-save
- `system/cursor/keybindings.jsonc` - Consistent keyboard shortcuts
- `system/cursor/extensions.json` - Recommended extensions including Biome
  formatter
- `.cursor/rules/` - AI context rules for development consistency

### 🚀 Productivity & Launchers

| Tool      | Description                                |
| --------- | ------------------------------------------ |
| [Raycast] | Spotlight replacement w/ dev tools support |

### 🌐 AWS / Cloud Dev

| Tool                        | Description                    |
| --------------------------- | ------------------------------ |
| [awscli]                    | AWS CLI                        |
| [aws-sso-util]              | AWS SSO configuration helper   |
| [cdk]                       | AWS CDK (TypeScript)           |
| [cdk-dia]                   | CDK diagram generator          |
| [Amazon.Lambda.Tools]       | .NET Lambda deployment tools   |
| [Amazon.Lambda.TestTool]    | .NET Lambda local testing      |

### 🔒 DevSecOps

| Tool                   | Description                               |
| ---------------------- | ----------------------------------------- |
| [ripsecrets]           | Fast secret scanner for commits           |
| [gitleaks]             | Deep secret scanning with rulesets        |
| [direnv]               | Auto loads `.envrc` files per directory   |
| [dotenv-linter]        | Lint `.env` files globally                |
| [editorconfig-checker] | Ensures consistent editor settings        |

### 🎨 Code Quality & Formatting

| Tool                   | Description                               |
| ---------------------- | ----------------------------------------- |
| [@biomejs/biome]       | Global code formatter and linter          |
| [.editorconfig]        | Editor configuration for consistent formatting |
| [VS Code/Cursor]       | Configured with 4-space indentation and format-on-save |

**Formatting Standards:**

- **4-space indentation** (never tabs)
- **LF line endings** (Unix-style)
- **No trailing whitespace**
- **Final newline** at end of files
- **Biome** as default formatter for supported file types

**Using Biome in Projects:**

```bash
# Install global Node.js tools (includes Biome)
just install-node-tools

# In your project directory
biome init                    # Create biome.json configuration
biome check .                 # Check formatting and linting
biome format .                # Format all files
biome lint .                  # Lint all files
```

**Editor Integration:**

- VS Code and Cursor are configured to use Biome as the default formatter
- Format-on-save is enabled for automatic formatting
- Biome respects the 4-space indentation standard

---

## 🔧 Setup & Management

### Symlink Setup

All configs are symlinked into correct system paths to maintain this repo
as the single source of truth:

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
just setup-node            # Install Node.js LTS and global tools (Biome, CDK)
just setup-dotnet          # Install .NET 8 Lambda tools
just setup-aws             # Configure AWS CLI (CDK tools installed via Node.js)
just setup-security        # Install and configure security tools
just install-node-tools    # Install global Node.js tools from pnpm-global.txt
just security-scan         # Run secret scanning and security checks
just quality-check         # Run code quality and formatting checks
```

**Backup non-symlinked files:**

```bash
just backup
```

Updates `Brewfile` and `vscode/extensions.txt` (symlinked files are already
tracked).

### AWS Development Setup

**Configure AWS CLI with SSO:**

```bash
just setup-aws
```

This will:

- Install AWS CLI and aws-sso-util via Homebrew
- Configure AWS CLI with SSO authentication
- Back up AWS configuration files

**Note:** AWS CDK tools (aws-cdk, cdk-dia) are installed via Node.js setup
(`just setup-node`)

**Manual AWS CLI configuration:**

```bash
aws configure sso
```

Follow the prompts to set up your AWS SSO profile. The configuration will
be backed up automatically.

### Security & DevSecOps Setup

**Install and configure security tools:**

```bash
just setup-security
```

This will:

- Install ripsecrets, gitleaks, direnv, dotenv-linter, and
  editorconfig-checker
- Configure direnv for nushell environment management
- Back up security tool versions

**Run security scans:**

```bash
just security-scan
```

This runs:

- `ripsecrets` - Fast secret scanning for commits
- `gitleaks` - Deep secret scanning with rulesets

**Run quality checks:**

```bash
just quality-check
```

This runs:

- Secret scanning (ripsecrets + gitleaks)
- EditorConfig validation
- Environment file linting

---

## 🛡️ DevSecOps & Security

Security checks are run manually using:

```bash
just quality-check
just security-scan
```

If you want to automate secret scanning, you can add a pre-commit hook like
this:

```bash
#!/bin/sh
just quality-check || exit 1
```

Copy this to `.git/hooks/pre-commit` to enforce checks before every commit
(optional).

---

## 🧱 Structure

This repository is organized to provide a clear separation of concerns and
maintainable configuration management:

### **Core Configuration Files**

```text
dotfiles/
├── system/                  # System-wide configuration files
│   ├── cursor/             # Global Cursor configuration
│   │   ├── settings.jsonc  # Cursor settings (4-space indentation, formatting)
│   │   ├── keybindings.jsonc # Cursor keyboard shortcuts
│   │   ├── argv.jsonc      # Cursor command line arguments
│   │   └── extensions.json # Cursor recommended extensions
│   ├── vscode/             # Global VS Code configuration
│   │   ├── settings.jsonc  # VS Code settings (formatting, extensions)
│   │   └── extensions.txt  # VS Code extensions list
│   ├── nushell/            # Global shell configuration
│   │   ├── config.nu       # Main shell config (aliases, functions)
│   │   └── env.nu          # Environment variables and PATH setup
│   ├── git/                # Global Git configuration
│   │   ├── gitconfig       # Global git config (safe to commit)
│   │   ├── gitconfig.local.example # Template for local git config (credentials)
│   │   └── gitignore_global # Global gitignore for OS files
│   ├── aws/                # Global AWS configuration
│   │   └── config          # AWS CLI profiles and settings
│   ├── ghostty/            # Global terminal configuration
│   │   └── config          # Terminal appearance and behavior
│   ├── starship/           # Global shell prompt configuration
│   │   └── starship.toml   # Starship prompt configuration (themes, modules)
│   ├── neovim/             # Global Neovim configuration
│   │   └── init.lua        # Neovim initialization script (minimal setup)
│   ├── Brewfile            # Homebrew packages and apps
│   ├── pnpm-global.txt     # Global Node.js tools list
│   └── .editorconfig       # Global editor configuration
├── .cursor/                 # Repository-specific Cursor rules
│   └── rules/              # AI context rules for development consistency
├── scripts/                 # Setup and management scripts
│   ├── setup_symlinks.sh   # Symlink creation script
│   ├── backup.sh           # System backup script
│   └── install.sh          # Prerequisites installer
```

### **Management and Automation**

```text
├── .gitignore              # Repository-specific ignore rules
├── LICENSE                 # MIT License
├── justfile                # Task automation (all setup commands)
├── README.md               # This documentation
├── biome.json              # Biome linting and formatting configuration
├── backup-log.txt          # Backup operation logs
└── symlink-backups.txt     # Symlink operation logs
```

### **How the Symlink System Works**

The dotfiles repository uses a sophisticated symlink system to maintain a
single source of truth:

1. **Source of Truth**: All configurations live in this repository
2. **Symlink Creation**: `setup_symlinks.sh` creates symbolic links from
   dotfiles to system locations
3. **Backup Protection**: Existing configs are backed up before symlinking
4. **Idempotent**: Running setup multiple times is safe

**Example Symlinks:**

- `system/vscode/settings.jsonc` → `~/Library/Application Support/Code/User/settings.json`
- `system/cursor/settings.jsonc` → `~/.cursor/settings.json`
- `system/git/gitconfig` → `~/.gitconfig`
- `system/nushell/config.nu` → `~/Library/Application Support/nushell/config.nu`

### **Git Ignore Strategy**

This repository uses a two-tier gitignore approach:

- **`.gitignore`** - Repository-specific files only (backup logs, local config)
- **`git/gitignore_global`** - Global gitignore for OS files (`.DS_Store`,
  `Thumbs.db`, etc.)

The global gitignore is symlinked to `~/.gitignore_global` during setup,
providing system-wide OS file filtering while keeping repository concerns
separate.

---

## 🔄 Development Workflow

### **Daily Development**

This dotfiles setup provides a streamlined development workflow:

#### **Starting a New Project**

```bash
# Create a new project directory
mkdir my-project && cd my-project

# Initialize Biome for consistent formatting
biome init

# Start coding with consistent formatting
# VS Code/Cursor will automatically format on save
```

#### **Quality Assurance**

```bash
# Run quality checks on your project
just quality-check

# Run security scans
just security-scan

# Format code with Biome
biome format .
```

#### **Environment Management**

```bash
# Use direnv for project-specific environment variables
echo 'export API_KEY="your-key"' > .envrc
direnv allow

# Environment variables are automatically loaded/unloaded
```

### **Maintaining Your Dotfiles**

#### **Adding New Tools**

1. **Homebrew packages**: Add to `Brewfile`
2. **Node.js tools**: Add to `pnpm-global.txt`
3. **VS Code extensions**: Add to `vscode/extensions.txt`
4. **Configuration files**: Add to `setup_symlinks.sh`
5. **Run bootstrap**: `just bootstrap` to install and configure everything

#### **Updating Configurations**

```bash
# Edit configuration files in the dotfiles directory
just edit

# Changes are immediately reflected via symlinks
# No need to restart applications in most cases
```

#### **Backup and Sync**

```bash
# Backup current system state
just backup

# Upgrade all tools
just upgrade

# Commit and push changes
git add .
git commit -m "Update dotfiles configuration"
git push
```

### **Best Practices**

#### **Configuration Management**

- **Edit in dotfiles**: Always edit files in the dotfiles directory, not the
  symlinked locations
- **Test changes**: Use `just quality-check` after making changes
- **Backup first**: Run `just backup` before major changes
- **Version control**: Commit changes regularly

#### **Tool Integration**

- **Use just commands**: Prefer `just` commands over manual installation
- **Consistent formatting**: Let Biome handle code formatting
- **Security first**: Run security scans regularly
- **Environment isolation**: Use direnv for project-specific configs

#### **Troubleshooting**

- **Symlink issues**: Run `just link` to recreate symlinks
- **Tool conflicts**: Check for conflicting global installations
- **Permission issues**: Ensure proper file permissions
- **Backup recovery**: Check `backups/` directory for previous configurations

---

## 🍴 Forking This Repository

This is my personal dotfiles setup, tailored to my specific development
workflow and preferences. Rather than contributing directly to this
repository, I encourage you to:

### **Fork and Customize**

1. **Fork this repository** to your own GitHub account
2. **Customize it** for your specific needs and preferences
3. **Make it your own** by adapting tools, configurations, and workflows
4. **Share improvements** by creating your own public dotfiles repository

### **Why Fork Instead of Contribute?**

- **Personal preferences**: Dotfiles are highly personal and subjective
- **Different workflows**: Your development workflow may differ significantly
- **Tool choices**: You might prefer different tools or versions
- **Learning experience**: Building your own setup teaches valuable skills

### **Getting Started with Your Fork**

1. Fork this repository
2. Update the README to reflect your setup
3. Modify configurations to match your preferences
4. Add or remove tools based on your needs
5. Test thoroughly on your system

### **Sharing Your Setup**

If you create an interesting dotfiles setup based on this one, feel free to:

- Link back to this repository as inspiration
- Share your repository with the community
- Write about your customizations and improvements

This approach ensures that everyone can have a dotfiles setup that's
perfectly tailored to their needs while still benefiting from shared ideas
and approaches.

---

## 🤖 AI Usage & Cursor Rules

This repository uses [Cursor](https://cursor.com) with custom `.cursor/rules`
to ensure consistency and alignment with our philosophy. These rules are
automatically applied when working in this repository and provide AI context
for development decisions.

### Rule Categories

The `.cursor/rules/` directory contains specialized rules for different
areas:

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

These rules are automatically loaded by Cursor when you open this repository
and provide context for:

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
[ripsecrets]: https://github.com/snickdx/ripsecrets
[gitleaks]: https://github.com/gitleaks/gitleaks
[direnv]: https://direnv.net
[dotenv-linter]: https://dotenv-linter.github.io
[editorconfig-checker]: https://editorconfig-checker.github.io
[topgrade]: https://github.com/r-darwish/topgrade
