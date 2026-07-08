# Managed Tools by Category

Reference for the tools this repo manages and why each is present. The exact
installable state lives in the package manifests under
[`system/packages/`](../../system/packages/); this page explains the lineup.

## Terminal + Shell

| Tool       | Description                               |
| ---------- | ----------------------------------------- |
| [Ghostty]  | Terminal emulator (fast, GPU-accelerated) |
| [zsh]      | Primary interactive and editor shell      |
| [Starship] | Minimal, fast prompt                      |
| [Carapace] | Completion engine for CLIs                |
| [Zoxide]   | Smarter `cd`                              |
| [fzf]      | Fuzzy finder                              |
| [fd]       | Better `find`                             |
| [bat]      | Syntax-highlighted `cat`                  |
| [topgrade] | One command to update everything          |

## Package Managers and Runtimes

| Tool       | Description                                            |
| ---------- | ------------------------------------------------------ |
| [Homebrew] | macOS-native package manager and fnm installer         |
| [fnm]      | Owner for the Node.js runtime and trusted JS commands  |
| [pnpm]     | Preferred Node.js package manager via fnm/Corepack     |
| [mise]     | Owner for .NET SDK selection (ADR-0006)                |
| [cargo]    | Rust package manager (used for many tools)             |

## Editor / IDE

| Tool      | Description          |
| --------- | -------------------- |
| [Neovim]  | For terminal editing |
| [VS Code] | Main GUI IDE         |

## Productivity & Launchers

| Tool      | Description                                |
| --------- | ------------------------------------------ |
| [Raycast] | Spotlight replacement w/ dev tools support |

## AWS / Cloud Dev

| Tool                     | Description                  |
| ------------------------ | ---------------------------- |
| [awscli]                 | AWS CLI                      |
| [aws-sso-util]           | AWS SSO configuration helper |
| [cdk]                    | AWS CDK (TypeScript)         |
| [cdk-dia]                | CDK diagram generator        |
| [Amazon.Lambda.Tools]    | .NET Lambda deployment tools |
| [Amazon.Lambda.TestTool] | .NET Lambda local testing    |

## DevSecOps

| Tool                   | Description                             |
| ---------------------- | --------------------------------------- |
| [ripsecrets]           | Fast secret scanner for commits         |
| [gitleaks]             | Deep secret scanning with rulesets      |
| [direnv]               | Auto loads `.envrc` files per directory |
| [dotenv-linter]        | Lint `.env` files globally              |
| [editorconfig-checker] | Ensures consistent editor settings      |

## Code Quality & Formatting

| Tool             | Description                                            |
| ---------------- | ------------------------------------------------------ |
| [@biomejs/biome] | Global code formatter and linter                       |
| `.editorconfig`  | Editor configuration for consistent formatting         |
| [VS Code]        | Configured with 4-space indentation and format-on-save |

Formatting standards: 4-space indentation, LF line endings, no trailing
whitespace, final newline, Biome as default formatter for supported types.

Using Biome in a project:

```bash
biome init      # Create biome.json configuration
biome check .   # Check formatting and linting
biome format .  # Format all files
```

## AI Agent Surfaces

Codex, Claude Code, opencode, and Pi are the AI agent surfaces; APM manages
shared AI Assets. See [`system/ai/README.md`](../../system/ai/README.md) for
ownership policy and [`AGENTS.md`](../../AGENTS.md) for agent guidance.

<!-- Reference link definitions -->

[Ghostty]: https://ghostty.app
[zsh]: https://www.zsh.org
[Starship]: https://starship.rs
[Carapace]: https://github.com/rsteube/carapace
[Zoxide]: https://github.com/ajeetdsouza/zoxide
[fzf]: https://github.com/junegunn/fzf
[fd]: https://github.com/sharkdp/fd
[bat]: https://github.com/sharkdp/bat
[Homebrew]: https://brew.sh
[pnpm]: https://pnpm.io
[fnm]: https://github.com/Schniz/fnm
[mise]: https://mise.jdx.dev
[cargo]: https://doc.rust-lang.org/cargo/
[Neovim]: https://neovim.io
[VS Code]: https://code.visualstudio.com
[Raycast]: https://www.raycast.com
[awscli]: https://aws.amazon.com/cli
[aws-sso-util]: https://github.com/benkehoe/aws-sso-util
[cdk]: https://docs.aws.amazon.com/cdk/
[cdk-dia]: https://github.com/pistazie/cdk-dia
[Amazon.Lambda.Tools]: https://github.com/aws/aws-extensions-for-dotnet-cli
[Amazon.Lambda.TestTool]: https://github.com/aws/aws-lambda-dotnet
[ripsecrets]: https://github.com/sirwart/ripsecrets
[gitleaks]: https://github.com/gitleaks/gitleaks
[direnv]: https://direnv.net
[dotenv-linter]: https://dotenv-linter.github.io
[editorconfig-checker]: https://editorconfig-checker.github.io
[topgrade]: https://github.com/topgrade-rs/topgrade
[@biomejs/biome]: https://biomejs.dev
