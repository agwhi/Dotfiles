# opencode

opencode is currently present as a legacy npm-global AI Tool Surface, not as a
declared global baseline tool.

Current local state:

- Package: npm global `opencode-ai`
- Version observed: `1.17.13`
- Binary observed: `~/.local/share/fnm/aliases/default/bin/opencode`
- State root: `~/.local/share/opencode`
- Config root: `~/.config/opencode`

The current zsh/Codex-compatible PATH exposes `opencode`. `open-code` is not
on PATH.

## Classification

`opencode-ai` is a legacy managed exception and possible project-local tool.
The opencode target is still included in the shared APM baseline target set so
that, if opencode remains installed, it receives the same global skills and AI
assets as Codex and Claude Code.

`~/.local/share/opencode` and `~/.config/opencode` are Sensitive Local State.
They include account/auth files, local databases, logs, snapshots, storage, and
provider configuration. Do not commit them directly.

## Target Policy

If opencode remains in the ecosystem, it should consume Shared AI Assets from
APM-generated or APM-installed adapters. It should not own the source copy of
shared prompts, skills, commands, MCP definitions, or agents.

Later options:

- keep opencode as a documented project-local or manual-local tool
- preview and deploy the shared APM target output for opencode
- remove npm global `opencode-ai` behind a Reset Approval Gate

No option is implemented in this task.
