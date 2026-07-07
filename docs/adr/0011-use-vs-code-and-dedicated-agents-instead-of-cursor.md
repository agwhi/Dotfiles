# Use VS Code And Dedicated Agents Instead Of Cursor

Status: accepted.
Date: 2026-07-07.
Related: ADR-0001, ADR-0004, ADR-0008, ADR-0009,
system/packages/Brewfile, system/packages/vscode-extensions.txt, AGENTS.md,
scripts/doctor.py, scripts/setup_symlinks.sh.

## Context

Cursor was installed as a Homebrew cask and configured as a second GUI editor
surface alongside VS Code. The repo also carried Cursor-specific settings,
keybindings, extension recommendations, and `.cursor/rules` files.

After the AI tooling stabilization, the durable agent surfaces are Codex,
Claude Code, opencode, and Pi, with shared baseline skills managed through
APM. VS Code remains the main GUI IDE. Cursor's remaining local value would be
its editor-native AI UX, tab completion, and cloud/editor agent features, but
those overlap with the dedicated agent surfaces Alex now uses.

Cursor also became the only actionable `doctor` finding because its extension
manifest did not match the live installed extension state. Keeping it would
require maintaining another editor config, extension policy, symlink surface,
and agent-rule format.

## Decision Drivers

- Reduce duplicate editor and AI surfaces now that Codex, Claude Code,
  opencode, and Pi are canonical.
- Keep VS Code as the managed GUI IDE and Neovim as the terminal editor.
- Avoid maintaining a second VS Code fork with its own extensions, settings,
  rules, and drift checks.
- Keep shared AI behavior in APM-managed skills and repo-level agent guidance,
  not Cursor-specific `.cursor/rules`.
- Make `doctor` actionable by removing a surface that is no longer intended to
  be managed.

## Considered Options

- Keep Cursor as a first-class editor: rejected because its capabilities now
  overlap with the dedicated agents and it adds ongoing config and extension
  drift.
- Keep Cursor installed but unmanaged: rejected because an unmanaged AI editor
  in the development baseline weakens source-of-truth clarity.
- Keep only Cursor and remove VS Code: rejected because VS Code is the main GUI
  IDE and has broader baseline/tooling compatibility.
- Remove Cursor and use VS Code plus dedicated agents: selected.

## Decision

Remove Cursor from the managed Development Ecosystem.

The managed editor and agent model is:

- VS Code as the main GUI IDE.
- Neovim as the terminal editor.
- Codex, Claude Code, opencode, and Pi as dedicated AI agent surfaces.
- APM as the shared AI Asset Manager for reusable baseline skills.
- `AGENTS.md` and scoped `AGENTS.md` files for repo-level agent guidance.

Do not keep `system/cursor`, `.cursor/rules`, Cursor extension manifests, or
Cursor symlink setup as source-of-truth files.

## Consequences

- `system/packages/Brewfile` no longer declares the Cursor cask.
- `just edit` opens VS Code with `code .`.
- Doctor no longer audits Cursor extensions as a managed surface.
- If Cursor appears locally again, treat it as undeclared development tooling
  or personal/manual state until a future ADR reverses this decision.
- The downside is losing Cursor-specific editor AI affordances such as Cursor
  Tab, Cursor's editor-native agent UX, and Cursor cloud agents. That is an
  acceptable trade-off because those capabilities are not currently the
  preferred workflow.
