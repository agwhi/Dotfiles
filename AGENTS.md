# Development Ecosystem Agent Guide

This repo is the source of truth for Alex's macOS development ecosystem. Treat
it as the orchestrator for package manifests, symlinked configuration, runtime
managers, AI tool surfaces, and cleanup policy.

## Working Rules

- Prefer repo manifests and local helper scripts over ad hoc installs.
- Preserve the current decisions in `docs/adr/`; add or update an ADR when a
  durable tool choice, source-of-truth boundary, or cleanup policy changes.
- Use `docs/adr/README.md` and `docs/adr/AGENTS.md` before creating or
  substantially editing ADRs.
- Keep sensitive state out of git. Use ignored local files, redacted templates,
  or documented manual steps for credentials, auth stores, histories, sessions,
  local databases, and provider config.
- Use `zsh` as the primary interactive/editor shell and keep automation
  POSIX-compatible unless a task explicitly needs zsh.
- Use `scripts/dev_env.sh <command>` when a non-interactive tool launch needs
  the repo's standard development PATH.
- Use `scripts/js_toolchain.sh <command>` for Node, npm, pnpm, Corepack, and
  JavaScript global tooling.
- Use `scripts/dotnet_toolchain.sh <command>` for .NET commands that must run
  through the ADR-0006 `mise` SDK context.

## Validation

For most repo changes, run the narrowest useful validation plus:

- `git diff --check`
- relevant shell or Python syntax checks
- `just doctor --json | python3 -m json.tool >/dev/null`
- markdownlint for changed Markdown files
- `ripsecrets --strict-ignore .`
- `gitleaks detect --source . --no-git --redact --no-banner`

`just doctor` should print either a ready message or actionable issues only.
Use `just doctor --all` for the full read-only inventory.
