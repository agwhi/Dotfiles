# Optimize Shell Choice for AI-Native Low-Friction Development

The shell strategy is a bounded dual-shell model. Nushell remains the Primary
Shell for Alex's interactive and editor-terminal workflows, while
POSIX-compatible zsh/sh remains the Automation Shell contract for bootstrap
scripts, `just` recipes, installer docs, Codex-generated commands, and other
AI-executed commands.

This is not a Nu-only strategy. Shell parity must be generated or verified from
shared environment ownership before plain commands such as `node`, `pnpm`,
`corepack`, or `dotnet` are considered safe across Nu, zsh, Codex, `just`, and
editor contexts. Until then, automation should prefer explicit wrappers such as
`scripts/js_toolchain.sh`, full command names, and POSIX-compatible syntax
rather than aliases or interactive shell startup behavior.

## Considered Options

- zsh as Primary Shell
- Nushell as Primary Shell with zsh/POSIX as Automation Shell
- both shells supported through generated shared environment configuration
- Nushell retained only as an optional structured-data tool

## Evidence

`docs/plans/shell-parity-and-strategy-plan.md` records the current probe
evidence. The decisive facts are that repo-managed editor terminals point at
Nu, Codex and `just` run from zsh/current-process contexts, `fnm` activates only
in the Nu login probe, `pnpm` resolves through different sources across
contexts, and zsh/Codex/just keep literal tilde PATH entries that hide tools.

## Consequences

Codex-generated commands should target the zsh/Codex execution context by
default, but use POSIX-compatible command text unless a task explicitly needs a
zsh feature. `just` bootstrap should assume portable shell semantics, not
Nushell syntax or aliases. Future shell setup work should make shared PATH and
tool ownership explicit before removing compatibility sources.

Doctor shell parity checks should remain non-mutating by default. Login/startup
shell probes are opt-in because they execute user startup files and can write
caches or run hooks.
