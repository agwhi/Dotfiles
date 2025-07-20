# 💻 Dotfiles Setup – macOS Dev Environment (M4 Pro)

A carefully curated developer setup for Node.js (via pnpm), .NET 8 (C#), TypeScript (CDK + Serverless), and React/Next.js on macOS, designed to maximise dev experience and developer security with a fast, consistent toolchain.

---

## 🎯 Philosophy

- **Global-first**: Everything here is set up globally (not repo-specific)
- **Speed & Clarity**: We favour tools that reduce friction and are fast to use
- **Terminal native**: Most tools are CLI or TUI based, Rust-preferred if options exist
- **Single source of truth**: All config is tracked, versioned, and symlinked
- **Secure by default**: DevSecOps from day one

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
just link-dotfiles
```

### Git Configuration

Symlink `.gitconfig` globally and separate sensitive config:

```bash
cp git/.gitconfig.local.example ~/.gitconfig.local
just link-dotfiles
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

**Backup non-symlinked files:**

```bash
just backup
```

Updates `Brewfile` and `vscode/extensions.txt` (symlinked files are already tracked).

---

## 🧱 Structure

```
dotfiles/
├── .config/
│   ├── starship.toml
│   ├── carapace/
│   │   └── carapace.yaml
│   ├── zoxide/
│   │   └── config.toml
│   └── nvim/
│       └── init.lua
├── .cursor/
│   └── rules/
├── aws/
│   └── config
├── ghostty/
│   └── config
├── git/
│   ├── gitconfig
│   ├── .gitconfig.local.example
│   └── gitignore_global
├── nushell/
│   ├── config.nu
│   └── env.nu
├── vscode/
│   ├── settings.json
│   └── extensions.txt
├── .fzf.zsh
├── Brewfile
├── justfile
├── backup.sh
└── README.md
```

---

## 🤖 AI Usage & Cursor Rules

This repository uses [Cursor](https://cursor.com) with custom `.cursor/rules` to ensure consistency and alignment with our philosophy.

### Rule Enforcement Areas

| Area                   | Based on Section      |
| ---------------------- | --------------------- |
| Shell & Terminal Tools | 🖥 Terminal + Shell    |
| Editor & Dev Tooling   | ✨ Editor / IDE       |
| Runtime Tooling        | 📦 Package Managers   |
| Cloud & CDK Tools      | 🌐 AWS / Cloud Dev    |
| Security & Linting     | 🔒 DevSecOps          |
| Dotfile Management     | 🔧 Setup & Management |

### Contributor Guidelines

1. Check if tools/settings are already listed in the README
2. Update relevant sections when adding new tools
3. Use Cursor rules as a consistency checklist

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
