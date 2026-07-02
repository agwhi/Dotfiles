# Claude

Claude Code is currently a manual-local AI Tool Surface.

Current local state:

- Binary: `~/.local/bin/claude`
- Resolved binary: `~/.local/share/claude/versions/2.1.198`
- Version observed: `2.1.198`
- Config and cache roots: `~/.claude`, `~/.claude.json`,
  `~/.local/share/claude`
- Older local versions observed: `2.1.187`, `2.1.196`, and `2.1.197`

## Classification

Claude Code is a managed exception until the repo declares the intended install
path for the CLI binary. Its local configuration, permissions, plugin caches,
marketplace clones, histories, backups, and app state are Sensitive Local State.

Claude plugin cache contents are not source-of-truth assets. If a plugin or
skill should become part of the Global AI Baseline, declare its package source
through APM and generate or install the Claude target from there.

## Assets

Target state:

- Consume `grill-with-docs` from the APM-managed baseline only after the Codex
  baseline source mismatch is resolved.
- Do not include `using-superpowers` in the global baseline.
- Keep project-specific commands, agents, and rules in the project repos that
  need them.

## Repo Ownership

This directory may contain Claude-safe generated adapters or redacted templates.
Do not commit raw `~/.claude`, `~/.claude.json`, or `~/.local/share/claude`
content.

Do not remove existing Claude plugin cache state, permissions, or installed CLI
versions without a Rebuild Snapshot and explicit approval.
