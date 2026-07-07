# opencode

opencode is a Homebrew-managed AI Tool Surface. Its CLI is installed from the
upstream OpenCode tap, and its shared APM skill baseline is deployed.

Current local state:

- Package: Homebrew formula `anomalyco/tap/opencode`
- Version observed: `1.17.15`
- Binary observed: `/opt/homebrew/bin/opencode`
- State root: `~/.local/share/opencode`
- Config root: `~/.config/opencode`
- APM-managed skills root: `~/.config/opencode/skills`

The current zsh/Codex-compatible PATH exposes `opencode`. `open-code` is not
on PATH.

## Classification

The OpenCode CLI is canonical through Homebrew. Use the upstream
`anomalyco/tap/opencode` formula rather than the Homebrew core `opencode`
formula, because the upstream tap tracks current OpenCode releases and avoids
making Homebrew `node` an opencode dependency.

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

opencode consumes Shared AI Assets from APM-generated or APM-installed
adapters. It does not own the source copy of shared prompts, skills, commands,
MCP definitions, or agents.

The deprecated npm-global `opencode-ai` install was removed after the Homebrew
tap binary verified cleanly. Do not reintroduce `opencode-ai` as an npm global
unless a later ADR replaces the Homebrew tap policy.
