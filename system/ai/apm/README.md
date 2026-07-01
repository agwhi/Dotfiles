# APM

APM is the selected AI Asset Manager for this Development Ecosystem.

Current local state:

- Binary: `/usr/local/bin/apm`
- Resolved binary: `/usr/local/lib/apm/apm`
- Version: `0.23.1`
- Current provenance: manual/pkg install
- Target role: Canonical Installer for AI Assets

The current APM binary is a managed exception until the repo declares how APM
itself is installed and updated. Selecting APM for assets does not approve
self-updating, reinstalling, pruning, or migrating existing AI state.

## What APM Should Manage

APM should eventually own:

- the Global AI Baseline
- lockfiles for baseline AI Asset sources
- third-party AI Asset packages
- Custom AI Assets from normal AI Package Sources
- generated adapters for Codex, Claude Code, opencode, Pi, or future targets
- audit and policy checks for installed assets

The initial baseline should contain only:

- `grill-with-docs`

## Future Repo Files

Do not create or run an APM manifest until the canonical source for
`grill-with-docs` and the target surfaces are chosen.

Candidate source-of-truth files for this repo are:

- `system/ai/apm/apm.yml`
- `system/ai/apm/apm.lock.yaml`

If global APM mode is later needed, `~/.apm/apm.yml` is local generated state
unless a task explicitly documents how it is produced from this repo.

Read-only or non-deploying commands to prefer before any install:

- `apm targets --json`
- `apm lock`
- `apm lock --global`
- `apm audit --ci`

## What APM Should Not Manage Yet

APM should not be used yet to change:

- `~/.codex`
- `~/.claude`
- `~/.local/share/claude`
- `~/.local/share/opencode`
- `~/.config/opencode`
- `~/Library/pnpm/pi`
- npm global `opencode-ai`
- any auth, history, database, log, trusted-project, or cache state

## Approval Gates

Do not run these commands without a later explicit approval:

- `apm install`
- `apm update`
- `apm prune`
- `apm uninstall`
- `apm self-update`
- any APM command that writes target files or rewrites lockfiles

Read-only APM inspection commands are acceptable when a task allows them.

## Unresolved

- The exact APM manifest path and schema for this repo.
- The source package or repository for canonical `grill-with-docs`.
- Whether APM itself should be installed through Homebrew, a package installer,
  a bootstrap script, or another declared source.
- Which generated target paths are safe for Codex and Claude before cleanup.
