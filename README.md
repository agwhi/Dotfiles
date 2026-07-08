# 💻 Dotfiles Setup – macOS Dev Environment

A carefully curated developer setup for Node.js (via fnm-managed Node and
Corepack/pnpm), .NET via mise, TypeScript (CDK + Serverless), and React/Next.js
on macOS, designed to maximise dev experience and developer security with a
fast, consistent toolchain.

This repository manages the macOS development environment through dotfiles:
package manifests declare what is installed, symlinks apply configuration, and
a read-only doctor reports drift.

---

## 📚 Documentation Map

- [`docs/README.md`](docs/README.md) explains the documentation model and where
  to put tutorials, how-tos, reference, explanation, ADRs, plans, and audits.
- [`docs/architecture.md`](docs/architecture.md) explains the current
  Orchestrator Repo architecture.
- [`CONTEXT.md`](CONTEXT.md) defines the Development Ecosystem language used by
  docs, ADRs, plans, scripts, and agents.
- [`docs/reference/tools.md`](docs/reference/tools.md) lists the managed tools
  by category.
- [`docs/reference/commands.md`](docs/reference/commands.md) is the full
  command and alias reference.
- [`system/packages/README.md`](system/packages/README.md) documents package
  ownership, manifests, and doctor usage.
- [`system/ai/README.md`](system/ai/README.md) documents AI Tool Surface and AI
  Asset ownership.

---

## 🎯 Philosophy

- **Global-first**: everything is set up globally (editors, tools, shell,
  security) for a consistent experience across all projects.
- **Speed & clarity**: fast Rust-based tools (fd, bat, ripgrep, topgrade), a
  minimal Starship prompt, and `just` for simple automation.
- **Terminal native**: CLI/TUI-first, Rust-preferred when options exist.
- **Single source of truth**: all config is tracked, versioned, and symlinked;
  setup scripts are idempotent and back up what they replace.
- **Secure by default**: secret scanning (ripsecrets, gitleaks), direnv for
  environment isolation, and network privacy tooling built in.

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

# Install Homebrew and just
./scripts/install.sh
```

### 2. Set Up Your Environment

```bash
# Complete laptop bootstrap: install packages and create symlinks
just bootstrap
```

This comprehensive setup will:

- Install all Homebrew packages from `system/packages/Brewfile`
  (including the security and network tools)
- Install VS Code extensions
- Install Node.js LTS and global tools (Biome, AWS CDK)
- Install .NET SDKs through mise and install Lambda tools
- Back up existing config files to `backups/`
- Create symlinks from dotfiles to system locations (shell, git, editor,
  direnv, dnscrypt-proxy, mise, and APM configs)

Note: VPN, LuLu firewall, and browser privacy settings still need one-time
manual configuration — see
[`docs/how-to/secure-public-networks.md`](docs/how-to/secure-public-networks.md).

### 3. Verify Installation

```bash
# Check that everything is working (read-only audit)
just doctor
```

### 4. Essential Commands

```bash
just bootstrap             # Complete laptop setup (alias: just install)
just doctor                # Read-only Development Ecosystem audit
just brew                  # Install all Homebrew packages
just backup                # Back up current system config to repo
just link                  # Create symlinks only
just upgrade               # Update all packages and tools
just edit                  # Open dotfiles folder in VS Code
just --list                # Show all available commands
```

The full command and alias reference (including the global `dotfile` commands
available in any directory) lives in
[`docs/reference/commands.md`](docs/reference/commands.md).

### 5. Next Steps

After bootstrap:

- **Restart your terminal** to load all shell changes.
- **Configure AWS CLI**: `just setup-aws-cli`.
- **Set up Git config**: copy `system/git/gitconfig.local.example` to
  `~/.gitconfig.local` and edit; it holds credentials and stays out of git.
- **Configure network security**: follow
  [`docs/how-to/secure-public-networks.md`](docs/how-to/secure-public-networks.md),
  then use `secure-on` on untrusted Wi-Fi.

---

## 🧱 Structure

```text
dotfiles/
├── README.md               # This bootstrap guide
├── CONTEXT.md              # Domain language glossary
├── AGENTS.md               # Repo-wide agent guidance
├── justfile                # Repo task automation
├── docs/                   # Architecture, ADRs, plans, how-tos, reference
├── scripts/                # install, symlinks, backup, doctor, wrappers
└── system/                 # Managed desired state
    ├── packages/           # Brewfile and package manifests
    ├── shell/path.sh       # Single source of truth for PATH
    ├── zsh/                # Shell startup files
    ├── git/ vscode/ ...    # Per-tool configuration (symlinked)
    ├── ai/                 # APM project and AI surface policy
    └── global-justfile     # System-wide commands (~/.justfile)
```

How it works: configuration lives in this repo and is symlinked into place by
`scripts/setup_symlinks.sh` (existing files are backed up first, re-runs are
idempotent). Packages install from the manifests in `system/packages/`.
`just doctor` audits the live machine against those manifests without changing
anything. See [`docs/architecture.md`](docs/architecture.md) for the full
picture.

---

## 🛡️ Security

```bash
just security-scan   # ripsecrets + gitleaks secret scanning
just quality-check   # security scans + formatting checks
```

Optional pre-commit hook (`.git/hooks/pre-commit`):

```bash
#!/bin/sh
just quality-check || exit 1
```

For public Wi-Fi protection (DNS encryption, VPN, firewall), see
[`docs/how-to/secure-public-networks.md`](docs/how-to/secure-public-networks.md).

---

## 🍴 Forking This Repository

This is a personal setup, tailored to one workflow. Fork it rather than
contributing directly: adapt the manifests, configs, and tool choices to your
needs, and link back if it inspired yours. Dotfiles are personal — building
your own teaches more than adopting someone else's.

---

## 🤖 AI Usage & Agent Guidance

This repository uses dedicated AI agent surfaces (Codex, Claude Code, opencode,
Pi) with APM as the shared AI Asset Manager. Agents should follow
[`AGENTS.md`](AGENTS.md) for safe commands and validation, and
[`docs/adr/AGENTS.md`](docs/adr/AGENTS.md) when touching decision records.
Durable tool choices belong in ADRs; manifests and ADRs are the source of
truth, not this README.
