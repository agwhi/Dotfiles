# AI Tooling Stabilization Plan

Date: 2026-07-02.

This plan documents the current AI Tool Surface and AI Asset state without
installing, uninstalling, updating, pruning, deleting, moving, relinking, or
rewriting any AI tool, asset, config tree, cache, history, or auth-adjacent
state.

It is the current machine-state plan for the next implementation pass. It does
not make any tool reproducibility claim unless this repo already declares the
tool or asset owner.

## Evidence

Read-only evidence gathered for this pass:

- `command -v`, `which -a`, and `type -a` for `codex`, `claude`,
  `opencode`, `open-code`, `pi`, and `apm`.
- Safe version checks for `codex`, `claude`, `opencode`, `pi`, and `apm`.
- `just doctor --json`, filtered for AI tool findings.
- Homebrew inventory for declared AI app surfaces.
- `fnm exec --using default npm ls -g --depth=0 --json`.
- `fnm exec --using default pnpm list -g --depth 0 --json`.
- Read-only APM help and `apm targets --json`.
- Name-only and metadata-only listings of AI asset directories.

No GUI or computer-use inspection was needed.

## Target Architecture

APM is the selected AI Asset Manager from ADR-0008. It should own the future
declaration, lock, audit, install, and adapter path for reusable AI Assets. It
does not automatically own every AI binary on the laptop.

Homebrew remains the canonical installer for AI application surfaces already
declared in `system/packages/Brewfile`, including Codex, ChatGPT,
ChatGPT Atlas, and Ollama.

The Global AI Baseline stays intentionally small:

- `grill-with-docs`

Do not promote these into the Global AI Baseline yet:

- `using-superpowers`
- Pi assets
- opencode assets
- Claude plugin cache contents
- Codex system, runtime, or plugin skills
- broad language or framework skills
- project-specific prompts, rules, agents, and commands

Shared AI Assets should be authored once and consumed through APM-generated or
APM-installed adapters for Codex, Claude Code, opencode, Pi, or future
surfaces. Tool-specific files are adapters, not the source of truth.
`grill-with-docs` is already a public APM skill, not a companion-repo asset.

## Tool Provenance

<!-- markdownlint-disable MD013 -->

| Tool or surface | Current path | Version | Install source | Repo declared | Classification | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Codex CLI | `/opt/homebrew/bin/codex` -> `/opt/homebrew/Caskroom/codex/0.142.4/codex-aarch64-apple-darwin` | `codex-cli 0.142.4` | Homebrew cask | Yes, `cask "codex"` | Canonical AI Tool Surface | Reproducible as an installed app surface through Homebrew. Assets under `~/.codex` are not reproducible yet. |
| Codex app runtime | `/Applications/Codex.app/Contents/Resources/codex` | same runtime family as Codex app | app runtime | Indirect only | App runtime context | Doctor sees this alongside Homebrew Codex. Do not classify app runtime helpers as package-manager drift. |
| Codex runtime helpers | `codex-execve-wrapper`, `codex_chronicle` | not versioned separately | app runtime | No | App runtime context | Surfaced by doctor as Codex-provided helpers. They are not standalone tools to declare. |
| Claude Code | `/Users/alex/.local/bin/claude` -> `/Users/alex/.local/share/claude/versions/2.1.198` | `2.1.198 (Claude Code)` | manual/local | No | Managed exception | Older local versions `2.1.187`, `2.1.196`, and `2.1.197` are also present under the local Claude versions tree. |
| opencode | `/Users/alex/.local/share/fnm/aliases/default/bin/opencode` | `1.16.2` | npm global under fnm default Node, package `opencode-ai` | No | Legacy managed exception | `open-code` is not on PATH. Decide later whether opencode is project-local, managed, or removed behind approval. |
| Pi | `/Users/alex/Library/pnpm/pi` | `0.73.0` | pnpm global, package `@mariozechner/pi-coding-agent` | No | Approval-gated project-local or removal candidate | Not declared in `system/packages/pnpm-global.txt`; do not add it to the baseline by accident. |
| APM | `/usr/local/bin/apm` -> `/usr/local/lib/apm/apm` | `0.23.1 (d1d926d)` | manual/pkg | Role only, binary no | Selected AI Asset Manager, binary managed exception | ADR-0008 selects APM for AI Assets, but this install path is not yet declared. Do not self-update or mutate with APM. |
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
- `system/ai/shared/README.md`

Classification: repo-managed documentation and sensitive-safe policy.

There is a non-deploying draft `system/ai/apm/apm.yml` and no
`system/ai/apm/apm.lock.yaml` yet. The Global AI Baseline is therefore
declared as intent but not reproducible through APM yet.

### Codex

Name-only paths inspected:

- `/Users/alex/.codex`
- `/Users/alex/.codex/skills`
- `/Users/alex/.codex/plugins`
- `/Users/alex/.codex/vendor_imports`

Observed global skills:

- `.system`
- `codex-primary-runtime`
- `grill-with-docs`
- `using-superpowers`

Observed Codex plugin cache roots:

- `openai-bundled`
- `openai-curated`
- `openai-curated-remote`
- `openai-primary-runtime`

Classification: mixed manual/local, vendor, plugin cache, and app runtime
state. Only `grill-with-docs` is target baseline policy. It is declared in the
draft APM manifest but not yet APM-locked by this repo.

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
an APM-managed shared asset target yet.

Excluded as Sensitive Local State: account files, auth files, MCP auth files,
local databases, logs, snapshots, storage, repos, provider configuration,
local wrappers, npm package state, and generated dependencies.

### Pi

Name-only paths inspected:

- `/Users/alex/Library/pnpm/pi`
- `/Users/alex/Library/pnpm/global/5/node_modules/@mariozechner/pi-coding-agent`

Classification: pnpm-global package state. Pi is not part of the Global AI
Baseline and is not declared in the repo's pnpm global package manifest.

Excluded as Sensitive Local State: package-manager store internals and any
future Pi auth, project, history, or cache state.

### APM

Name-only paths inspected:

- `/usr/local/lib/apm`
- `/Users/alex/.apm`
- `system/ai/apm`

Classification: selected AI Asset Manager with a manual/pkg binary managed
exception. `~/.apm/config.json` is local state and was not read.

`apm targets --json` currently reports only the repo's `.cursor/` target as
active. Codex, Claude, opencode, and other AI targets are inactive because the
repo does not yet contain target files such as `.codex/`, `.opencode/`, or
`CLAUDE.md`. The draft `system/ai/apm/apm.yml` pins `targets: [codex]` so
APM target auto-detection is not used for the first AI-only baseline pass.
Run project-scoped APM checks from `system/ai/apm` until a repo wrapper exists.

Excluded as Sensitive Local State: `~/.apm/config.json`, future global APM
manifests under `~/.apm`, caches, credentials, and generated target output.

APM schema findings from read-only inspection:

- project manifest filename: `apm.yml`
- project lockfile filename: `apm.lock.yaml`
- APM dependencies live under `dependencies.apm`
- target mappings can be pinned with top-level `targets`
- package sources include shorthand Git refs, full Git URLs, local paths,
  packed bundles, marketplace refs, registry refs, per-primitive path refs
  such as `owner/repo/path#ref`, and object forms with fields such as `git`
  and `ref`
- `apm compile --dry-run --target codex` is the preferred placement preview,
  and was approved once for the 2026-07-02 non-deploying Codex gate
- `apm install --dry-run` exists but is still blocked here because all
  `apm install` variants require later approval

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

## Shared Assets, Prompts, And Commands

The shared source should be an AI Package Source consumed by APM, not copied
files under each tool's home directory.

Source policy:

- Keep source assets in an APM package source.
- Use the Orchestrator Repo only for the laptop's Global AI Baseline
  declarations, lockfiles, target mappings, validation, and redacted
  templates.
- Put project-specific prompts, rules, commands, agents, and workflows in the
  project repos that need them.
- Promote a project-local asset only after repeated cross-project use.
- Treat Custom AI Assets the same as Third-Party AI Assets: declare source,
  lock, audit, and adapt through APM.

Initial target baseline:

- Declare only `grill-with-docs`.
- Generate or install adapters only for approved target surfaces.
- Do not include `using-superpowers` in the baseline.

The baseline source is the public APM package
`mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1`. The
machine-local path `/Users/alex/.codex/skills/grill-with-docs` is useful
evidence for current content, but it must not be the baseline source because
it is live AI tool state and not portable. A future companion repo is reserved
for Alex's custom AI assets.

## APM Role And Open Questions

APM should eventually own:

- `system/ai/apm/apm.yml`
- `system/ai/apm/apm.lock.yaml`
- Global AI Baseline package declarations
- target mappings for Codex, Claude Code, opencode, Pi, and future surfaces
- audit and policy checks for installed AI Assets
- generated or installed adapters that contain no secrets

Open questions before implementation:

1. Which generated Codex target paths are safe after dry-run review?
2. How should APM itself be installed and updated reproducibly?
3. Should opencode and Pi remain local experiments, become declared AI Tool
   Surfaces, or be removed behind approval?
4. How should doctor distinguish APM-selected policy from the current
   undeclared APM binary install path?
5. Should APM target detection be pinned so `.cursor/` does not pull editor
   rules into an AI-only stabilization pass?

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
- Run `apm lock` in a repo state where the user has not approved creating or
  rewriting `apm.lock.yaml`.
- Add an APM manifest and deploy generated adapters into Codex, Claude Code,
  opencode, Pi, or Cursor target directories.
- Remove or replace `/Users/alex/.codex/skills/grill-with-docs`.
- Remove `/Users/alex/.codex/skills/using-superpowers`.
- Remove or rewrite Claude plugin cache state.
- Remove or migrate `~/.local/bin/claude` or
  `~/.local/share/claude`.
- Remove npm global `opencode-ai`.
- Remove pnpm global `@mariozechner/pi-coding-agent`.
- Remove or migrate `~/.local/share/opencode` or
  `~/.config/opencode`.
- Delete, rewrite, or move `~/.codex`, `~/.claude`, `~/.apm`, or any auth,
  history, cache, database, permission, trusted-project, or session subpath.
- Upgrade, relink, or reinstall Codex, Claude Code, opencode, Pi, or APM as
  part of asset cleanup.

## Prioritized Roadmap

### P0: Freeze Current Policy

1. Keep this plan as the current machine-state handoff.
2. Accept ADR-0008 as the APM role decision while keeping the APM binary as a
   managed exception.
3. Do not run APM mutation commands.
4. Do not broaden the Global AI Baseline beyond `grill-with-docs`.

### P1: Declare The Baseline Without Deploying

1. Keep `system/ai/apm/apm.yml` pinned to
   `mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1` with the
   only active target as Codex.
2. Decide whether `apm.lock.yaml` creation is approved for the next pass, or
   whether a scratch-root materialization gate is safer first.
3. Repeat `apm compile --dry-run --target codex` after package content is
   materialized by an approved non-live gate.
4. Use `apm targets --json` and non-deploying checks before any install or
   compile step.
5. Update doctor to recognize ADR-0008, the APM manifest, and target baseline
   checks.

### P2: Reproduce Shared Skills

1. Generate or install the `grill-with-docs` adapter into the first approved
   target surface.
2. Verify tool discovery for that target.
3. Compare generated output with the current local `grill-with-docs` intent.
4. Expand to Claude Code, opencode, or Pi only after target behavior is
   understood.

### P3: Cleanup Behind Approval

1. Capture a Rebuild Snapshot for AI local state.
2. Remove duplicate or non-baseline global assets only after APM reproduction
   works.
3. Decide whether opencode and Pi remain local tools, become declared surfaces,
   or are removed.
4. Tighten doctor so undeclared AI tools and shared assets are actionable
   drift.

## Recommended Next Implementation Task

Approve the next APM gate: either create `system/ai/apm/apm.lock.yaml` with
`apm lock`, or materialize package content in an explicitly non-live scratch
path, then repeat `apm compile --dry-run --target codex`. Do not run update,
prune, or target deployment commands in that task.
