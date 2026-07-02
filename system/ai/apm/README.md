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

`grill-with-docs` is a public APM skill from
`mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1`. It is not part
of a future custom companion repo.

## Draft Repo Files

The repo now carries a non-deploying draft manifest:

- `system/ai/apm/apm.yml`

The manifest is intentionally not locked or installed yet. It pins the first
APM target to Codex only so the repo's active `.cursor/` directory is not
selected by auto-detection during an AI-only stabilization pass.
Run project-scoped APM checks from `system/ai/apm` until a repo wrapper exists.

Future source-of-truth files for this repo are:

- `system/ai/apm/apm.yml`
- `system/ai/apm/apm.lock.yaml`

If global APM mode is later needed, `~/.apm/apm.yml` is local generated state
unless a task explicitly documents how it is produced from this repo.

Read-only commands to prefer before any install:

- `apm targets --json`
- `apm audit --ci`

Do not run `apm lock` or `apm compile --dry-run --target codex` until a later
task explicitly approves creating or rewriting `system/ai/apm/apm.lock.yaml`
or previewing generated Codex placement.

## Schema Findings

Read-only APM inspection identified these `0.23.1` conventions:

- project manifest filename: `apm.yml`
- project lockfile filename: `apm.lock.yaml`
- APM dependencies live under `dependencies.apm`
- target mappings can be pinned with top-level `targets`
- supported targets include `codex`, `claude`, `cursor`, `opencode`,
  `gemini`, `windsurf`, `kiro`, `copilot`, `agent-skills`, and `all`
- package sources include shorthand Git refs, full Git URLs, local paths,
  packed bundles, marketplace refs, registry refs, per-primitive path refs
  such as `owner/repo/path#ref`, and object forms with fields such as `git`
  and `ref`

The canonical source for `grill-with-docs` is the public APM package
`mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1`. Read-only APM
inspection resolved tag `v1.0.1` to commit
`2454c95dc305c158b21a0cdafeb728879dd0359a`. Do not point the baseline at
`/Users/alex/.codex/skills/grill-with-docs`; that path is machine-local AI
tool state and not reproducible from this repo.

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

- `apm lock`
- `apm install`
- `apm update`
- `apm prune`
- `apm uninstall`
- `apm self-update`
- any APM command that writes target files or rewrites lockfiles

Read-only APM inspection commands are acceptable when a task allows them.

## Unresolved

- Whether APM itself should be installed through Homebrew, a package installer,
  a bootstrap script, or another declared source.
- Which generated target paths are safe for Codex after dry-run review.
- Which custom AI assets Alex will later place in a companion repo.
