# AI Tooling Stabilization Plan

Date: 2026-07-03.
Status: completed. Historical record; current state comes from `just doctor`
and the package manifests.

This plan documents the current AI Tool Surface and AI Asset state. The
original discovery pass was non-mutating. A later approved gate created the
repo APM lockfile and ran scratch-only APM installs with redirected HOME/XDG
state. No live AI tool home, auth state, history, cache, or unrelated target
asset was modified.

It is the current machine-state plan for the next implementation pass. It does
not make any tool reproducibility claim unless this repo already declares the
tool or asset owner.

## Evidence

Evidence gathered for this pass:

- `command -v`, `which -a`, and `type -a` for `codex`, `claude`,
  `opencode`, `open-code`, `pi`, and `apm`.
- Safe version checks for `codex`, `claude`, `opencode`, `pi`, and `apm`.
- `just doctor --json`, filtered for AI tool findings.
- Homebrew inventory for declared AI app surfaces.
- `fnm exec --using default npm ls -g --depth=0 --json`.
- `fnm exec --using default pnpm list -g --depth 0 --json`.
- Read-only APM help and `apm targets --json`.
- the previous `apm lock --target codex` approved repo lockfile gate.
- Scratch-only frozen APM installs under ignored `reports/apm-scratch/`.
- Name-only and metadata-only listings of AI asset directories.

No GUI or computer-use inspection was needed.

## Target Architecture

APM is the selected AI Asset Manager from ADR-0008. It should own declaration,
lock, audit, install, generated modules, and target output for reusable AI
Assets after sources are declared and target writes are approved. It does not
automatically own every AI binary on the laptop.

Homebrew remains the canonical installer for AI application and harness
surfaces already declared in `system/packages/Brewfile`, including APM, Codex,
Claude Desktop, Claude Code, ChatGPT, ChatGPT Atlas, and Ollama.

The Global AI Baseline stays intentionally small. The approved Codex baseline
is the public `grill-with-docs` workflow materialized as split skills:

- `grill-with-docs`
- `grilling`
- `domain-modeling`

Do not promote these into the Global AI Baseline yet:

- `using-superpowers`
- Pi-specific assets
- opencode-specific assets
- Claude plugin cache contents
- Codex system, runtime, or plugin skills
- broad language or framework skills
- project-specific prompts, rules, agents, and commands

Shared AI Assets should be authored once and consumed through APM-generated or
APM-installed adapters for Codex, Claude Code, opencode, or future supported
surfaces. Tool-specific files are adapters, not the source of truth.
`grill-with-docs` is already a public APM skill, not a repo-owned Codex skill
tree.

## Tool Provenance

<!-- markdownlint-disable MD013 -->

| Tool or surface | Current path | Version | Install source | Repo declared | Classification | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Codex CLI | `/opt/homebrew/bin/codex` -> `/opt/homebrew/Caskroom/codex/0.142.4/codex-aarch64-apple-darwin` | `codex-cli 0.142.4` | Homebrew cask | Yes, `cask "codex"` | Canonical AI Tool Surface | Reproducible as an installed app surface through Homebrew. Assets under `~/.codex` are not reproducible yet. |
| Codex app runtime | `/Applications/Codex.app/Contents/Resources/codex` | same runtime family as Codex app | app runtime | Indirect only | App runtime context | Doctor sees this alongside Homebrew Codex. Do not classify app runtime helpers as package-manager drift. |
| Codex runtime helpers | `codex-execve-wrapper`, `codex_chronicle` | not versioned separately | app runtime | No | App runtime context | Surfaced by doctor as Codex-provided helpers. They are not standalone tools to declare. |
| Claude Code | `/opt/homebrew/bin/claude` -> `/opt/homebrew/Caskroom/claude-code/2.1.195/claude` | `2.1.195 (Claude Code)` | Homebrew cask `claude-code` | Yes, `cask "claude-code"` | Canonical AI Tool Surface | The previous manual `~/.local/bin/claude` symlink and `~/.local/share/claude/versions` executables were removed during the approved migration. |
| Claude Desktop | `/Applications/Claude.app` | `1.18286.0` | Homebrew cask `claude` | Yes, `cask "claude"` | Canonical AI Tool Surface | Sensitive `~/.claude` state remains local and out of git. |
| opencode | `/opt/homebrew/bin/opencode` | `1.17.15` | Homebrew formula `anomalyco/tap/opencode`; APM skills deployed under `~/.config/opencode/skills` | Yes, Brewfile | Canonical CLI plus canonical shared skill target | `open-code` is not on PATH. Preserve IVCE AI Gateway / Bedrock config in local opencode config; do not commit it. Use the upstream tap rather than Homebrew core so opencode does not reintroduce Homebrew `node` ownership. |
| Pi | `/Users/alex/Library/pnpm/pi` | `0.80.3` | pnpm global, package `@earendil-works/pi-coding-agent`; extensions declared in `system/packages/pnpm-global.txt` | Yes, pnpm manifest | Declared AI Tool Surface | Restored on 2026-07-05 through the canonical fnm/pnpm global path after the deprecated `@mariozechner` package was removed. Pi-specific assets are not part of the shared APM baseline unless promoted later. |
| APM | `/opt/homebrew/bin/apm` -> `/opt/homebrew/Cellar/apm/0.23.1/bin/apm` | `0.23.1 (d1d926d)` | Homebrew formula `microsoft/apm/apm` | Yes, `brew "microsoft/apm/apm"` | Selected AI Asset Manager and canonical Homebrew binary | ADR-0008 selects APM for AI Assets. The active command resolves through Homebrew; the old `/usr/local` manual binary was removed on 2026-07-07. Do not self-update or mutate with APM without approval. |
| ChatGPT | Homebrew cask app | `1.2026.160,1781312926` | Homebrew cask | Yes, `cask "chatgpt"` | Canonical app surface | App state is local and out of repo. No shared asset policy is needed yet. |
| ChatGPT Atlas | Homebrew cask app | `1.2026.98.2,20260416164957000` | Homebrew cask | Yes, `cask "chatgpt-atlas"` | Canonical app surface | App state is local and out of repo. |
| Ollama | Homebrew formula | `0.30.11` | Homebrew formula | Yes, `brew "ollama"` | Canonical app surface | Model downloads and local server state are local state, not repo assets. |

<!-- markdownlint-enable MD013 -->

Doctor already exposes enough AI command path and provenance detail for this
planning pass. A later implementation task should update doctor wording so
ADR-0008's APM selection is recognized, and so baseline AI Assets can be
verified after an APM manifest exists.

## Current Asset Layout

### Repo-Managed AI Files

Repo paths inspected:

- `system/ai/README.md`
- `system/ai/apm/README.md`
- `system/ai/claude/README.md`
- `system/ai/codex/README.md`
- `system/ai/opencode/README.md`
- `system/ai/pi/README.md`
- `system/ai/shared/README.md`

Classification: repo-managed documentation and sensitive-safe policy.

There is now a repo-owned `system/ai/apm/apm.yml` and
`system/ai/apm/apm.lock.yaml`. The lockfile pins the public
`grill-with-docs` package as package evidence. ADR-0009 makes those files the
repo source of truth and links them into `~/.apm` through normal setup.

### Codex

Name-only paths inspected:

- `/Users/alex/.codex`
- `/Users/alex/.codex/skills`
- `/Users/alex/.codex/plugins`
- `/Users/alex/.codex/vendor_imports`

Observed global skills:

- `.system`
- `codex-primary-runtime`
- `domain-modeling`
- `grill-with-docs`
- `grilling`

Observed Codex plugin cache roots:

- `openai-bundled`
- `openai-curated`
- `openai-curated-remote`
- `openai-primary-runtime`

Classification: mixed manual/local, vendor, plugin cache, and app runtime
state. Only the APM-managed split `grill-with-docs` workflow is target
baseline policy. The approved deployment materialized that split baseline and
removed `using-superpowers`.

Excluded as Sensitive Local State: Codex auth, histories, sessions, logs,
local databases, memory stores, trusted-project state, plugin caches,
attachments, temporary wrappers, shell snapshots, and runtime caches.

### Claude Code

Name-only paths inspected:

- `/Users/alex/.claude`
- `/Users/alex/.claude/plugins`
- `/Users/alex/.local/share/claude/versions`

Observed Claude plugin cache roots:

- `agent-plugins-for-aws`
- `agent-toolkit`
- `aws-skills`
- `claude-plugins-official`

Observed Claude marketplaces include:

- `agent-plugins-for-aws`
- `agent-toolkit`
- `aws-skills`
- `claude-code-plugins`
- `claude-plugins-official`
- `superpowers-marketplace`

No top-level `/Users/alex/.claude/skills`,
`/Users/alex/.claude/commands`, or `/Users/alex/.claude/agents`
directory was observed.

Classification: manual-local CLI plus Claude-managed local plugin and
marketplace state. It is not source-of-truth asset state.

Excluded as Sensitive Local State: Claude settings, permissions, histories,
sessions, projects, caches, debug files, telemetry, plugin install manifests,
marketplace metadata files, backups, shell snapshots, and versioned binaries.

### opencode

Name-only paths inspected:

- `/Users/alex/.local/share/opencode`
- `/Users/alex/.config/opencode`

No `/Users/alex/.config/opencode/command` or
`/Users/alex/.config/opencode/agent` directory was observed.

Classification: sensitive local state and manual tool configuration. It is not
source-of-truth asset state. The approved APM opencode target deployment has
materialized the shared split skill baseline under
`/Users/alex/.config/opencode/skills`.

Excluded as Sensitive Local State: account files, auth files, MCP auth files,
local databases, logs, snapshots, storage, repos, provider configuration,
local wrappers, npm package state, generated dependencies, and IVCE AI Gateway
/ Bedrock config values.

### Pi

Current state: Pi is installed through the canonical fnm/pnpm global path and
is declared in `system/packages/pnpm-global.txt`.

Declared packages:

- `@earendil-works/pi-coding-agent`
- `@plannotator/pi-extension`
- `pi-lens`
- `pi-mcp-adapter`
- `pi-subagents`
- `pi-web-access`

Classification: declared AI Tool Surface and user workflow tool. Pi packages
were refreshed through the canonical pnpm global path on 2026-07-07:
`@plannotator/pi-extension` to `0.22.0`, `pi-lens` to `3.8.66`, and
`pi-subagents` to `0.34.0`. Pi-specific assets are not part of the shared APM
baseline unless a later policy promotes them.

### APM

Name-only paths inspected:

- `/opt/homebrew/bin/apm`
- `/opt/homebrew/Cellar/apm/0.23.1`
- `/Users/alex/.apm`
- `system/ai/apm`

Classification: selected AI Asset Manager with a Homebrew-managed canonical
binary. `~/.apm/config.json` is local state and was not read.

`apm targets --json` can auto-detect unrelated repo targets. The repo APM
manifest pins the shared harness target set explicitly as
`codex`, `claude`, and `opencode` so APM target auto-detection is not used for
AI baseline decisions.
Run project-scoped APM checks from `system/ai/apm` when package or lock
evidence is needed.

Excluded as Sensitive Local State: `~/.apm/config.json`, future global APM
manifests under `~/.apm`, caches, credentials, and generated target output.

The live APM project should consume the repo source-of-truth files through
normal dotfiles symlinks:

- `~/.apm/apm.yml` -> `system/ai/apm/apm.yml`
- `~/.apm/apm.lock.yaml` -> `system/ai/apm/apm.lock.yaml`

When setup is eventually run, it may back up existing files at those two paths
before replacing them with symlinks.

APM schema findings from read-only inspection and the approved lockfile gate:

- project manifest filename: `apm.yml`
- project lockfile filename: `apm.lock.yaml`
- APM dependencies live under `dependencies.apm`
- target mappings can be pinned with top-level `targets`
- package sources include shorthand Git refs, full Git URLs, local paths,
  packed bundles, marketplace refs, registry refs, per-primitive path refs
  such as `owner/repo/path#ref`, and object forms with fields such as `git`
  and `ref`
- `apm lock --target codex` creates `apm.lock.yaml` and may materialize an
  `apm_modules/` cache; the lockfile is source, while `apm_modules/` is
  generated and ignored
- `apm install --frozen --target codex --legacy-skill-paths --root <dir>`
  previews Codex's legacy `skills/` layout in an ignored scratch root
- `apm compile --global --dry-run` does not consume the repo manifest; global
  mode looks under `~/.apm`

Read-only APM evidence resolves `grill-with-docs` as the public package
`mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1`. The tag
resolves to commit `2454c95dc305c158b21a0cdafeb728879dd0359a`.

The 2026-07-02 Codex dry-run confirmed that APM can see the pinned public tag
through `apm view`, and that `apm compile --dry-run --target codex` does not
write target files. It did not preview concrete `grill-with-docs` files
because no package content has been materialized by an approved lock or install
gate. The generic Codex placement set was `AGENTS.md`, `.agents/skills/`,
`.codex/agents/`, and `.codex/hooks.json`; no `using-superpowers` asset was
proposed.

The 2026-07-02 UTC scratch-root gate materialized the public dependency under
`reports/apm-scratch/20260702T221350Z` with redirected HOME and XDG cache
state. It wrote only ignored scratch files, including scratch
`apm.lock.yaml`, `apm_modules/`,
`.agents/skills/grill-with-docs/SKILL.md`, an empty `.codex/` directory, and
scratch-local APM/Git cache state. The repo lockfile remained absent, and
`using-superpowers` was not present in the scratch root.

On 2026-07-03, `apm lock --target codex` created the repo lockfile. A frozen
scratch install from copied `apm.yml` and `apm.lock.yaml` materialized only
`grill-with-docs`, and `using-superpowers` was absent. Default Codex target
output went to `.agents/skills/grill-with-docs/SKILL.md`; with
`--legacy-skill-paths`, output went to `.codex/skills/grill-with-docs/SKILL.md`.

That preview also found the blocker for deploying the package by itself: the
locked public package's `SKILL.md` is only a wrapper that says to run
`/grilling` using `/domain-modeling`. The fix was to materialize the single
public workflow as the split Codex skills `grill-with-docs`, `grilling`, and
`domain-modeling`.

The 2026-07-03 follow-up compared the pinned public package with the live
Codex skill and tested expanded scratch manifests. `domain-modeling` exists at
`mattpocock/skills/skills/engineering/domain-modeling#v1.0.1`, and its format
reference files match the live `grill-with-docs` reference files. The first
expanded test used the wrong path:
`mattpocock/skills/skills/engineering/grilling#v1.0.1` does not exist.

The corrected public path is
`mattpocock/skills/skills/productivity/grilling#v1.0.1`. Public Git inspection
showed that `grilling` is a skill, not a command, and that the upstream
`.claude-plugin/plugin.json` includes `grill-with-docs`, `domain-modeling`, and
`grilling`. The public AI Hero `grill-with-docs` page recommends installing
from `mattpocock/skills` with `--skill=grill-with-docs`; the AI Hero v1
changelog says `grill-with-docs` now runs `/grilling` using
`/domain-modeling`. A scratch APM lock and frozen scratch install validated
this public dependency set:

- `mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1`
- `mattpocock/skills/skills/productivity/grilling#v1.0.1`
- `mattpocock/skills/skills/engineering/domain-modeling#v1.0.1`

The generated scratch Codex output contained `grill-with-docs`, `grilling`, and
`domain-modeling`; it did not contain `using-superpowers`. Do not work around
this with a repo-owned Codex skill tree. The later approved deployment
materialized this split target output under `~/.codex/skills`.

Global APM mode was tested with redirected `HOME` and XDG paths. It does not
consume the repo manifest directly; `apm install --global` expects
`~/.apm/apm.yml`. Therefore `~/.apm` consumes the repo source of truth through
symlinks, while APM owns generated modules and target output after target-write
approval.

`apm audit --ci` currently reports expected APM drift because generated target
output is intentionally absent from `system/ai/apm`. Do not make the audit pass
by committing `.agents/` output or by writing live Codex state.

## Shared Assets, Prompts, And Commands

The shared source should be an AI Package Source consumed by APM, not a
repo-owned copy of a tool-specific skill tree.

Source policy:

- Keep package-source evidence in APM manifests and lockfiles.
- Link the repo APM manifest and lockfile into `~/.apm`.
- Let APM materialize generated modules and target output after target-write
  approval.
- Put project-specific prompts, rules, commands, agents, and workflows in the
  project repos that need them.
- Promote a project-local asset only after repeated cross-project use.
- Treat Custom AI Assets the same as Third-Party AI Assets: declare source,
  lock, audit, and adapt through APM.

Initial target baseline:

- Declare only the public split `grill-with-docs` workflow.
- Generate or install adapters only for approved target surfaces.
- Do not include `using-superpowers` in the baseline.

The current baseline source is the public APM package
`mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1` plus the public
`grilling` and `domain-modeling` dependency skills for APM lock evidence. A
future companion repo is reserved for Alex's custom AI assets that need their
own lifecycle.

## APM Role And Open Questions

APM should eventually support:

- `system/ai/apm/apm.yml`
- `system/ai/apm/apm.lock.yaml`
- Global AI Baseline package evidence
- target mappings for Codex, Claude Code, opencode, and future surfaces
- future Pi integration if APM adds a confirmed Pi target or adapter model
- audit and policy checks for installed AI Assets
- generated modules and target output through approved target-write gates

Open questions after live deployment:

1. When should the legacy manual `/usr/local/bin/apm` duplicate be removed?
   Answered on 2026-07-07: it was removed after Homebrew APM ownership was
   verified.

## Repo Versus Companion Repo

This Orchestrator Repo should own:

- AI Tool Surface policy and ADRs.
- APM baseline manifests and lockfiles after schema and source are chosen.
- redacted templates and sensitive-safe generated adapters.
- doctor checks that verify declared tools and declared baseline assets.
- reset gates and rebuild procedures.

A future Custom AI Companion Repo may own Alex's custom AI assets:

- user-authored skills
- reusable prompts
- reusable agents
- templates
- workflow packages
- package metadata and tests for those assets

The companion repo must still be consumed as an AI Package Source through APM.
It should not become a special manual clone path.

## Sensitive Local State Policy

Never commit raw contents from:

- `~/.codex`
- `~/.claude`
- `~/.claude.json`
- `~/.local/share/claude`
- `~/.local/share/opencode`
- `~/.config/opencode`
- `~/.apm`
- `~/Library/pnpm` AI package state
- app runtime helper directories
- temporary command wrappers

Never commit these categories:

- tokens, API keys, OAuth data, credentials, account identifiers, or session
  data
- chat history, transcripts, local databases, logs, memories, and telemetry
- trusted-project state and allow or permission lists
- vendor cache directories and plugin cache directories
- package-manager store internals
- generated temporary files, shell snapshots, and app runtime helpers
- provider wrappers or gateway config unless converted into a redacted
  template

Only extract sensitive-safe declarations, redacted templates, or generated
adapters when a later task explicitly needs them.

## Reset And Rebuild Gates

These actions require a later explicit approval and a Rebuild Snapshot first:

- Run `apm install`, `apm update`, `apm prune`, `apm uninstall`,
  `apm self-update`, or any APM command that writes target files.
- Rewrite `apm.lock.yaml` without approval.
- Add another APM manifest or deploy generated adapters into Codex, Claude
  Code, opencode, or any future Pi adapter target directories.
- Remove or replace the APM-managed split Codex skills under
  `/Users/alex/.codex/skills`.
- Remove any reintroduced `/Users/alex/.codex/skills/using-superpowers`.
- Remove or rewrite Claude plugin cache state.
- Remove Homebrew Claude casks or migrate `~/.local/share/claude`.
- Remove or migrate `~/.local/share/opencode` or
  `~/.config/opencode`.
- Delete, rewrite, or move `~/.codex`, `~/.claude`, `~/.apm`, or any auth,
  history, cache, database, permission, trusted-project, or session subpath.
- Upgrade, relink, or reinstall Codex, Claude Code, opencode, Pi, or APM as
  part of asset cleanup.

## Prioritized Roadmap

### P0: Freeze Current Policy

1. Keep this plan as the current machine-state handoff.
2. Accept ADR-0008 as the APM role decision with the active APM binary managed
   by the Homebrew formula.
3. Accept ADR-0009 as the APM project-file placement decision: repo manifest
   and lockfile symlinked into `~/.apm`.
4. Keep APM binary ownership with the declared Homebrew formula. The legacy
   `/usr/local/bin/apm` manual binary was removed on 2026-07-07.
5. Do not broaden the Global AI Baseline beyond the split `grill-with-docs`
   workflow.

### P1: Declare And Verify The Baseline

1. Keep `system/ai/apm/apm.yml` pinned to the public `grill-with-docs`
   wrapper plus its `grilling` and `domain-modeling` dependency skills, with
   explicit shared harness targets `codex`, `claude`, and `opencode`.
2. Treat repo `apm.lock.yaml` creation and the current dependency-source
   correction as approved and complete for the public baseline source.
3. Treat scratch-root materialization as proven for the corrected dependency
   set, with output confined to ignored local state.
4. Treat `~/.apm/apm.yml` and `~/.apm/apm.lock.yaml` symlink state as
   canonical when they point to the repo source files.
5. Update doctor to report repo APM validity, live APM symlink state, and the
   live split Codex, Claude, and opencode baselines separately. Done.

### P2: Keep The Corrected Deployment Canonical

1. Keep the approved split-skill Codex, Claude, and opencode layouts canonical
   in doctor.
2. Keep old `grill-with-docs/` format references absent.
3. Keep `using-superpowers` intentionally excluded unless a later ADR changes
   the Global AI Baseline.

### P3: Cleanup Behind Approval

1. Capture a Rebuild Snapshot for AI local state.
2. Remove duplicate or non-baseline global assets only after the APM-generated
   baseline is verified.
3. Keep Pi declared through pnpm unless a later policy moves it.
4. Tighten doctor so undeclared AI tools and shared assets are actionable
   drift.

## Recommended Next Implementation Task

Keep doctor aligned with the deployed split Codex baseline. The repo source of
truth remains `system/ai/apm/apm.yml` plus `system/ai/apm/apm.lock.yaml`,
consumed by `~/.apm` symlinks. Do not run APM update, prune, global install, or
target deployment commands without a new explicit gate.
