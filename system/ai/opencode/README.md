# opencode

opencode is currently present as a legacy npm-global AI Tool Surface. Its CLI
installer is not canonical yet, but its shared APM skill baseline is deployed.

Current local state:

- Package: npm global `opencode-ai`
- Version observed: `1.17.13`
- Binary observed: `~/.local/share/fnm/aliases/default/bin/opencode`
- State root: `~/.local/share/opencode`
- Config root: `~/.config/opencode`
- APM-managed skills root: `~/.config/opencode/skills`

The current zsh/Codex-compatible PATH exposes `opencode`. `open-code` is not
on PATH.

## Classification

`opencode-ai` is a legacy managed exception and possible project-local tool.
The opencode target is included in the shared APM baseline target set, and the
approved APM deployment has materialized the same split skill baseline as Codex
and Claude Code:

- `grill-with-docs`
- `grilling`
- `domain-modeling`

`~/.local/share/opencode` and `~/.config/opencode` are Sensitive Local State.
They include account/auth files, local databases, logs, snapshots, storage, and
provider configuration. The IVCE AI Gateway / Bedrock configuration remains
local in `~/.config/opencode/opencode.json` and
`~/.config/opencode/ai-gateway-sigv4-wrapper/`; do not commit those files
directly.

## Target Policy

If opencode remains in the ecosystem, it should consume Shared AI Assets from
APM-generated or APM-installed adapters. It should not own the source copy of
shared prompts, skills, commands, MCP definitions, or agents.

Later options:

- keep opencode as a documented npm-global managed exception
- migrate opencode CLI installation to a better canonical installer if one is
  chosen
- remove npm global `opencode-ai` behind a Reset Approval Gate
