# Claude

Claude Desktop and Claude Code should be repo-owned AI Tool Surfaces through
Homebrew casks.

Current local state:

- CLI binary: `~/.local/bin/claude`
- Resolved CLI binary: `~/.local/share/claude/versions/2.1.198`
- CLI version observed: `2.1.198 (Claude Code)`
- CLI install source: `manual/local`; migrate to the declared Homebrew stable
  cask `claude-code` in a later approved reinstall task.
- Desktop app: `/Applications/Claude.app`
- Desktop version observed: `1.18286.0`
- Desktop install source: manual app install; migrate to the declared
  Homebrew cask `claude` in a later approved reinstall task.
- Config and cache roots: `~/.claude`, `~/.claude.json`,
  `~/.local/share/claude`
- Older versioned executable artifacts observed: `2.1.187`, `2.1.196`, and
  `2.1.197`

## Classification

Claude Code and Claude Desktop are migration-pending until the live installs
are replaced by the Brewfile-declared casks:

- `cask "claude-code"` for the stable Claude Code terminal harness.
- `cask "claude"` for Claude Desktop.

The official Claude Code docs distinguish the stable `claude-code` cask from
`claude-code@latest`; use the stable cask unless a later ADR deliberately
chooses the latest release channel.

Local configuration, permissions, plugin caches, marketplace clones, histories,
backups, and app state are Sensitive Local State.

Older versioned executable artifacts are approval-gated cleanup candidates
only. Do not remove them in a documentation, doctor, or APM baseline task. A
later reinstall task should snapshot safe metadata, uninstall the manual CLI
and app surfaces, install the Homebrew casks, and verify `claude` resolves
through Homebrew before cleaning old version files.

Claude plugin cache contents are not source-of-truth assets. If a plugin or
skill should become part of the Global AI Baseline, declare its package source
through APM and generate or install the Claude target from there.

## Assets

Target state:

- No APM deployment or baseline requirement applies to Claude yet.
- If Claude receives the shared baseline later, use the existing APM-managed
  split baseline: `grill-with-docs`, `grilling`, and `domain-modeling`.
- Do not include `using-superpowers` in the global baseline.
- Keep project-specific commands, agents, and rules in the project repos that
  need them.

## Repo Ownership

This directory may contain Claude-safe generated adapters or redacted templates.
Do not commit raw `~/.claude`, `~/.claude.json`, or `~/.local/share/claude`
content.

Do not remove existing Claude plugin cache state, permissions, or installed CLI
versions without a Rebuild Snapshot and explicit approval.
