# APM

APM is the selected AI Asset Manager for this Development Ecosystem.

Current local state:

- Binary: `/usr/local/bin/apm`
- Resolved binary: `/usr/local/lib/apm/apm`
- Version: `0.23.1`
- Current provenance: manual/pkg install
- Target role: Canonical Installer for AI Assets

The current APM binary is a managed exception. Official APM installation docs
list the Homebrew tap formula `microsoft/apm/apm`, and
`system/packages/Brewfile` now declares that formula as the intended installer:
<https://microsoft.github.io/apm/getting-started/installation/#package-managers>.
Selecting APM for assets does not approve self-updating, reinstalling,
pruning, or migrating existing AI state.

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

## Repo Files

The repo now carries the source-of-truth APM files:

- `system/ai/apm/apm.yml`
- `system/ai/apm/apm.lock.yaml`

The manifest pins the first APM target to Codex only so the repo's active
`.cursor/` directory is not selected by auto-detection during an AI-only
stabilization pass.
Run project-scoped APM checks from `system/ai/apm` until a repo wrapper exists.

Generated APM dependencies and target output under this directory are ignored:
`apm_modules/`, `.agents/`, `.codex/`, `AGENTS.md`, and `CLAUDE.md`.

Global APM mode does not consume this repo manifest directly. It expects
`~/.apm/apm.yml`, so `~/.apm` remains generated/local state and must not become
the source of truth.

Read-only commands to prefer before any install:

- `apm targets --json`
- `apm view mattpocock/skills/skills/engineering/grill-with-docs versions`
- `apm audit --ci`

Do not run `apm lock` until a later task explicitly approves creating or
rewriting `system/ai/apm/apm.lock.yaml`. The first lockfile has been approved
and created; this warning now applies to future rewrites.

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

The first scratch preview found that this public package is not equivalent to
the currently installed live Codex skill. The package contains a thin
`SKILL.md` wrapper that invokes `/grilling` and `/domain-modeling`; the live
Codex skill is self-contained and includes the detailed workflow plus format
references. Do not deploy this package over the live skill until the baseline
source decision is resolved.

## Non-Deploying Codex Gate

On 2026-07-02, the first approved non-deploying Codex gate ran from
`system/ai/apm`:

- `apm targets --json`
- `apm view mattpocock/skills/skills/engineering/grill-with-docs versions`
- `apm compile --dry-run --target codex`

The read-only remote view resolved tag `v1.0.1` for the public package, but
the dry-run compile did not produce Codex files because no APM package content
has been installed or locked into this repo yet. The dry-run reported the
generic Codex placement set as `AGENTS.md`, `.agents/skills/`,
`.codex/agents/`, and `.codex/hooks.json`, then stopped with no proposed
asset files. No `using-superpowers` asset was proposed.

This gate is superseded by the lockfile and scratch-preview gate below.

## Scratch-Root Materialization Gate

On 2026-07-02 UTC, the first scratch-root materialization gate ran from
`system/ai/apm` with:

```sh
SCRATCH=/Users/alex/Dev/dotfiles/reports/apm-scratch/20260702T221350Z
env HOME="$SCRATCH/home" \
  XDG_CACHE_HOME="$SCRATCH/xdg-cache" \
  XDG_CONFIG_HOME="$SCRATCH/xdg-config" \
  XDG_DATA_HOME="$SCRATCH/xdg-data" \
  apm install --root "$SCRATCH"
env HOME="$SCRATCH/home" \
  XDG_CACHE_HOME="$SCRATCH/xdg-cache" \
  XDG_CONFIG_HOME="$SCRATCH/xdg-config" \
  XDG_DATA_HOME="$SCRATCH/xdg-data" \
  apm compile --dry-run --target codex --root "$SCRATCH"
```

`apm install --root` resolved
`mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1` to commit
`2454c95dc305c158b21a0cdafeb728879dd0359a` and wrote only under the ignored
scratch root. The high-level scratch outputs were:

- `apm.lock.yaml`
- `apm_modules/mattpocock/skills/skills/engineering/grill-with-docs/`
- `.agents/skills/grill-with-docs/SKILL.md`
- `.codex/`
- redirected `home/` and `xdg-cache/` APM/Git state

The materialized skill is `grill-with-docs`. `using-superpowers` was not
present in the scratch root. The generated `.codex/` directory was empty.

`apm compile --dry-run --target codex --root "$SCRATCH"` still did not preview
concrete package files when run from `system/ai/apm`; APM reported no content
found to compile. Running the same dry-run from the scratch root failed because
the scratch root is not an APM project and has no `apm.yml`. Treat this as a
compile-source limitation to resolve before any live deploy.

## Lockfile And Codex Preview Gate

On 2026-07-03, the repo lockfile was intentionally created with:

```sh
apm lock --target codex
```

The lockfile pins only
`mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1` at commit
`2454c95dc305c158b21a0cdafeb728879dd0359a`. `apm_modules/` was created as a
generated cache and is ignored.

A frozen scratch install using copied `apm.yml` and `apm.lock.yaml`
materialized only `grill-with-docs`; `using-superpowers` was absent. Default
Codex output went to `.agents/skills/grill-with-docs/SKILL.md`.

The current Codex desktop global skill discovery path is `~/.codex/skills`.
APM can produce that legacy layout with:

```sh
apm install --frozen --target codex --legacy-skill-paths --root "$SCRATCH"
```

That command was tested only with redirected HOME/XDG state and an ignored
scratch root. It produced `.codex/skills/grill-with-docs/SKILL.md` and no
`using-superpowers` output.

Live deployment remains blocked because the materialized public skill is only a
wrapper over `/grilling` and `/domain-modeling`.

`apm audit --ci` currently reports expected drift because it wants the
project-scoped deployed file `.agents/skills/grill-with-docs/SKILL.md` to exist
beside the lockfile. Do not satisfy that drift by committing generated target
output until the source mismatch is resolved.

## Deployment Model

The live deployment model is not `apm install --global` from this repo.
Redirected-HOME testing showed that global mode looks for `~/.apm/apm.yml` and
does not consume `system/ai/apm/apm.yml` directly.

Preferred model after the source mismatch is resolved:

- keep `system/ai/apm/apm.yml` and `system/ai/apm/apm.lock.yaml` as source
- run a repo-owned command or wrapper from `system/ai/apm`
- snapshot live Codex skill names and metadata before writing
- deploy only reviewed Codex target paths
- use `--legacy-skill-paths` if Codex desktop still requires
  `~/.codex/skills`
- treat `~/.apm`, `apm_modules/`, and generated target output as local state

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

- lockfile rewrites
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
