# APM

APM is the selected AI Asset Manager for this Development Ecosystem.

Current local state:

- Binary: `/usr/local/bin/apm`
- Resolved binary: `/usr/local/lib/apm/apm`
- Version: `0.23.1`
- Current provenance: manual/pkg install
- Target role: AI Asset discovery, locking, audit, and later materialization

The current APM binary is a managed exception. Official APM installation docs
list the Homebrew tap formula `microsoft/apm/apm`, and
`system/packages/Brewfile` now declares that formula as the intended installer:
<https://microsoft.github.io/apm/getting-started/installation/#package-managers>.
Selecting APM for assets does not approve self-updating, reinstalling,
pruning, or migrating existing AI state.

## What APM Should Manage

APM should eventually support:

- source/package discovery for the Global AI Baseline
- lockfiles for baseline AI Asset sources
- third-party AI Asset packages
- Custom AI Assets from normal AI Package Sources
- generated modules and target output after target-write approval
- audit and policy checks for installed assets

The initial baseline should contain only:

- `grill-with-docs`

`grill-with-docs` is a public APM skill from
`mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1`. It is not part
of a future custom companion repo. The public skill is a thin wrapper, so the
APM manifest also pins its public dependencies:

- `mattpocock/skills/skills/productivity/grilling#v1.0.1`
- `mattpocock/skills/skills/engineering/domain-modeling#v1.0.1`

## Repo Files

The repo now carries the source-of-truth APM files:

- `system/ai/apm/apm.yml`
- `system/ai/apm/apm.lock.yaml`

The normal dotfiles symlink setup maps those files into the live APM project:

- `~/.apm/apm.yml`
- `~/.apm/apm.lock.yaml`

When setup is eventually run, existing files at those two paths are backed up
before being replaced with symlinks.

The manifest pins the first APM target to Codex only so the repo's active
`.cursor/` directory is not selected by auto-detection during an AI-only
stabilization pass.
Run project-scoped APM checks from `system/ai/apm` when package or lock
evidence is needed.

Generated APM dependencies and target output under this directory are ignored:
`apm_modules/`, `.agents/`, `.codex/`, `AGENTS.md`, and `CLAUDE.md`.

Global APM mode does not consume this repo manifest directly. It expects
`~/.apm/apm.yml`, so `~/.apm` consumes the repo source of truth through
symlinks and must not become the source of truth itself.

Read-only commands to prefer before any install:

- `apm targets --json`
- `apm view mattpocock/skills/skills/engineering/grill-with-docs versions`
- `apm audit --ci`

Do not run `apm lock` until a task explicitly approves creating or rewriting
`system/ai/apm/apm.lock.yaml`. The current lockfile rewrite was approved for
the public dependency-source correction; this warning applies to future
rewrites.

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

The APM lock evidence for `grill-with-docs` is the public package plus the
public dependency skills above. Read-only APM inspection resolved tag `v1.0.1`
to commit `2454c95dc305c158b21a0cdafeb728879dd0359a`.

The first scratch preview found that the `grill-with-docs` package alone is
not equivalent to the currently installed live Codex skill. The package
contains a thin `SKILL.md` wrapper that invokes `/grilling` and
`/domain-modeling`; the live Codex skill is self-contained and includes the
detailed workflow plus format references.

The 2026-07-03 source investigation found the missing public dependency:
`grilling` exists at
`mattpocock/skills/skills/productivity/grilling#v1.0.1`, not under
`skills/engineering/grilling`. A scratch lock and frozen scratch install
validated the three public package entries above. Do not replace this with a
repo-owned Codex skill tree. Let APM materialize generated modules and target
output only after a later deployment gate approves live target writes.

The public AI Hero `grill-with-docs` page recommends installing from
`mattpocock/skills` with `--skill=grill-with-docs` and links the source to
`skills/engineering/grill-with-docs` on GitHub. The AI Hero v1 changelog says
`grill-with-docs` was simplified to run `/grilling` using `/domain-modeling`,
which matches the three public APM entries above.

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
compile-source limitation for APM target previews, not as a reason to use APM
for live Codex placement.

## Lockfile And Codex Preview Gate

On 2026-07-03, the repo lockfile was intentionally created with:

```sh
apm lock --target codex
```

The first lockfile pinned only
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

On 2026-07-03, a scratch source-resolution gate found and validated the
missing public dependency path:

- `mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1`
- `mattpocock/skills/skills/productivity/grilling#v1.0.1`
- `mattpocock/skills/skills/engineering/domain-modeling#v1.0.1`

The scratch lock resolved all three entries to commit
`2454c95dc305c158b21a0cdafeb728879dd0359a`. A frozen scratch install with
redirected HOME/XDG state and `--root` under `reports/apm-scratch/` produced:

- `.codex/skills/domain-modeling/SKILL.md`
- `.codex/skills/domain-modeling/ADR-FORMAT.md`
- `.codex/skills/domain-modeling/CONTEXT-FORMAT.md`
- `.codex/skills/grill-with-docs/SKILL.md`
- `.codex/skills/grilling/SKILL.md`

No `using-superpowers` output was generated. The live Codex
`ADR-FORMAT.md` and `CONTEXT-FORMAT.md` files match the public
`domain-modeling` reference files. The live self-contained
`grill-with-docs/SKILL.md` differs from the public split form, so live Codex
deployment still needs a later approval gate and review of the generated target
layout.

`apm audit --ci` currently reports expected drift because it wants the
project-scoped deployed file `.agents/skills/grill-with-docs/SKILL.md` to exist
beside the lockfile. Do not satisfy that drift by committing generated target
output or by writing live Codex state.

## Deployment Model

The live deployment model is not `apm install --global` from this repo.
Redirected-HOME testing showed that global mode looks for `~/.apm/apm.yml` and
does not consume `system/ai/apm/apm.yml` directly.

Preferred model:

- keep `system/ai/apm/apm.yml` and `system/ai/apm/apm.lock.yaml` as the repo
  source of truth
- link those files to `~/.apm/apm.yml` and `~/.apm/apm.lock.yaml` through the
  normal dotfiles symlink setup
- keep the corrected public package source in the APM manifest and lockfile
- let APM materialize generated modules and target output after target writes
  are approved
- treat `~/.apm`, `apm_modules/`, and generated target output as local state

Do not satisfy APM audit drift by writing live Codex state or committing
generated `.agents/` or `.codex/` target output.

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

- When the current manual `/usr/local/bin/apm` binary should be replaced by
  the declared Homebrew `microsoft/apm/apm` formula.
- Which generated target paths are safe for Codex after dry-run review.
- Which custom AI assets Alex will later place in a companion repo.
