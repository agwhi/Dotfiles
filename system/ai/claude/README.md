# Claude

Claude Desktop and Claude Code should be repo-owned AI Tool Surfaces through
Homebrew casks.

Current local state:

- CLI binary: `/opt/homebrew/bin/claude`
- Resolved CLI binary: `/opt/homebrew/Caskroom/claude-code/2.1.191/claude`
- CLI version observed: `2.1.191 (Claude Code)`
- CLI install source: Homebrew cask `claude-code`
- Desktop app: `/Applications/Claude.app`
- Desktop version observed: `1.18286.0`
- Desktop install source: Homebrew cask `claude`
- Config and cache roots: `~/.claude`, `~/.claude.json`,
  `~/.local/share/claude`
- The previous manual CLI symlink and versioned executable artifacts under
  `~/.local/share/claude/versions` were removed during the approved
  Homebrew migration.

## Classification

Claude Code and Claude Desktop are canonical Homebrew-owned AI Tool Surfaces:

- `cask "claude-code"` for the stable Claude Code terminal harness.
- `cask "claude"` for Claude Desktop.

The official Claude Code docs distinguish the stable `claude-code` cask from
`claude-code@latest`; use the stable cask unless a later ADR deliberately
chooses the latest release channel.

Local configuration, permissions, plugin caches, marketplace clones, histories,
backups, and app state are Sensitive Local State.

Claude plugin cache contents are not source-of-truth assets. If a plugin or
skill should become part of the Global AI Baseline, declare its package source
through APM and generate or install the Claude target from there.

## Assets

Target state:

- Claude is part of the shared APM baseline target set.
- Use the existing APM-managed split baseline: `grill-with-docs`, `grilling`,
  and `domain-modeling`.
- Do not write live Claude target output until a separate APM target-write gate
  previews and approves the generated files.
- Do not include `using-superpowers` in the global baseline.
- Keep project-specific commands, agents, and rules in the project repos that
  need them.

## Repo Ownership

This directory may contain Claude-safe generated adapters or redacted templates.
Do not commit raw `~/.claude`, `~/.claude.json`, or `~/.local/share/claude`
content.

Do not remove existing Claude plugin cache state, permissions, Homebrew casks,
or sensitive local state without a Rebuild Snapshot and explicit approval.
