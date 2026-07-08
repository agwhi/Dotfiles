# AI Tool Surface Stabilization Plan

Date: 2026-07-01.
Status: completed. Historical record; current state comes from `just doctor`
and the package manifests.

This plan is non-mutating. It classifies current AI Tool Surface state without
installing, uninstalling, upgrading, relinking, deleting, moving, or rewriting
any AI tool, config tree, package, cache, history, or asset.

## Recommended Target State

Select APM as the AI Asset Manager for this Development Ecosystem. The local
binary identifies itself as `Agent Package Manager (APM)` version `0.23.1`,
and its command surface includes dependency resolution, lockfiles, policy,
audit, marketplace, install, update, prune, and target compilation workflows.

Keep the Global AI Baseline minimal. ADR-0003 remains the baseline policy:
`grill-with-docs` is the only Baseline AI Asset, and `using-superpowers` is not
part of the target baseline.

Treat Custom AI Assets exactly like Third-Party AI Assets. ADR-0002 remains the
source policy: custom skills, prompts, agents, templates, and workflow artifacts
can live in a Companion Repo, local bundle, Git source, or marketplace, but the
Orchestrator Repo should declare the laptop's Global AI Baseline through APM.
ADR-0009 links the repo APM manifest and lockfile into `~/.apm`; APM remains
responsible for generated modules and target placement after target-write
approval.

Keep project-specific AI Assets project-local unless Alex promotes them to the
Global AI Baseline after repeated cross-project use.

## Evidence

Read-only commands used:

- `just doctor --json`
- `which -a codex claude opencode open-code pi apm`
- direct `--version` checks for Codex, APM, Claude Code, Pi, and opencode
- `apm --help`, `apm init --help`, `apm lock --help`, `apm audit --help`, and
  `apm targets --help`
- read-only `find`, `stat`, `file`, and directory listings for AI paths
- `fnm exec --using default npm ls -g --depth=0 --json`
- `fnm exec --using default pnpm list -g --depth 0 --json`
- `brew list --cask --versions codex chatgpt chatgpt-atlas`
- `brew list --formula --versions ollama`
- `brew info --cask codex --json=v2`

Current local facts:

- Homebrew declares `ollama`, `chatgpt`, `chatgpt-atlas`, `codex`,
  `claude`, and `claude-code`.
- Codex is installed as Homebrew cask `codex` version `0.142.4`; Homebrew
  metadata reports available cask version `0.142.5`. This task does not upgrade
  it.
- Codex app runtime also exposes `/Applications/Codex.app/Contents/Resources`
  commands in the current app context.
- APM is present at `/opt/homebrew/bin/apm`, resolves through the Homebrew
  formula `microsoft/apm/apm`, and reports version `0.23.1`. The old
  `/usr/local/bin/apm` -> `/usr/local/lib/apm/apm` manual install was removed
  on 2026-07-07.
- APM uses `apm.yml` and `apm.lock.yaml` for package declarations and locks.
  `apm lock` writes a lockfile without deploying files, while `apm install`,
  `apm update`, `apm prune`, `apm uninstall`, and `apm self-update` mutate
  local state.
- Claude Code is installed through Homebrew cask `claude-code`;
  `/opt/homebrew/bin/claude` resolves to
  `/opt/homebrew/Caskroom/claude-code/2.1.195/claude` and reports
  `2.1.195 (Claude Code)`.
- Claude Desktop is present at `/Applications/Claude.app` version `1.18286.0`.
  It is installed through Homebrew cask `claude`.
- opencode is installed through the upstream Homebrew tap
  `anomalyco/tap/opencode` version `1.17.15`. `opencode` is visible on PATH;
  `open-code` is not. The old npm-global `opencode-ai` install was removed
  after the Homebrew binary verified cleanly.
- Pi is installed through the canonical fnm/pnpm global path as
  `@earendil-works/pi-coding-agent` version `0.80.3`, with declared Pi
  extension packages in `system/packages/pnpm-global.txt`. The declared Pi
  extension packages were refreshed on 2026-07-07.
- `~/.codex`, `~/.claude`, `~/.local/share/opencode`, and `~/.config/opencode`
  contain sensitive User-Managed AI State, histories, caches, auth-adjacent
  files, trusted-project state, local databases, generated adapters, and plugin
  caches.
- `~/.codex/skills` currently includes system/runtime skills plus the
  APM-managed split baseline skills `grill-with-docs`, `grilling`, and
  `domain-modeling`. `using-superpowers` is intentionally excluded.
- Claude plugin caches include installed third-party or official plugin state,
  including cached superpowers versions.

## Tool Surface Classification

<!-- markdownlint-disable MD013 -->

| Tool or surface | Current binaries | Config and state paths | Current provenance | Classification | Recommendation |
| --- | --- | --- | --- | --- | --- |
| APM | `/opt/homebrew/bin/apm` -> `/opt/homebrew/Cellar/apm/0.23.1/bin/apm` | repo manifest and lockfile under `system/ai/apm/`; live project symlinks under `~/.apm` | Homebrew formula `microsoft/apm/apm` | canonical binary | Use APM as the AI Asset Manager. The old `/usr/local` binary was removed on 2026-07-07. Do not run `apm install`, `apm update`, `apm prune`, `apm uninstall`, or `apm self-update` without approval. |
| Codex CLI | `/opt/homebrew/bin/codex`; app resource binary in `/Applications/Codex.app` | `~/.codex` plus app/runtime cache paths | Homebrew cask plus app runtime | canonical install surface | Keep Codex declared through Homebrew. Keep `~/.codex` as Sensitive Local State; mutate baseline skills only through approved APM target-write gates. |
| Codex runtime helpers | `codex-execve-wrapper`, `codex_chronicle` in Codex app/runtime paths | Codex app runtime directories and temporary command wrappers | app_runtime | managed context | Do not classify these as package-manager drift. They are execution context from the Codex app. |
| Codex skills | APM-managed split baseline under `~/.codex/skills`: `grill-with-docs`, `grilling`, and `domain-modeling`; system/runtime skills | `~/.codex/skills`, `~/.codex/plugins`, `~/.codex/vendor_imports` | APM target output plus app/runtime | canonical baseline plus vendor state | Keep the split `grill-with-docs` workflow as the only target baseline. Keep `using-superpowers` absent. Treat system/runtime skills and plugin caches as vendor/app state unless intentionally promoted. |
| Claude Code and Desktop | CLI: `/opt/homebrew/bin/claude` -> `/opt/homebrew/Caskroom/claude-code/2.1.195/claude`; Desktop: `/Applications/Claude.app` | `~/.claude`, `~/.claude.json`, `~/.local/share/claude` | Homebrew casks `claude-code` and `claude` | canonical install surface | Keep both harness surfaces declared through Homebrew. Do not remove or migrate existing Claude state without a snapshot and approval. |
| Claude plugins and commands | plugin cache under `~/.claude/plugins` | `~/.claude/plugins/cache`, `~/.claude/plugins/marketplaces`, install manifests | Claude-managed local cache | manual local / approval-gated cleanup | Do not commit cache contents. Reinstall selected shared assets through APM later, then remove old cache copies only behind approval. |
| opencode | `/opt/homebrew/bin/opencode` | `~/.local/share/opencode`, `~/.config/opencode`, APM skills under `~/.config/opencode/skills` | Homebrew formula `anomalyco/tap/opencode` plus local config plus APM skill output | canonical CLI plus canonical shared skill target | Keep IVCE AI Gateway / Bedrock config local. Keep using the upstream tap rather than Homebrew core so opencode does not reintroduce Homebrew `node` ownership. |
| Pi | `/Users/alex/Library/pnpm/pi`; extension commands such as `pi-lens-mcp`, `pi-mcp-adapter`, and `pi-subagents` | pnpm global package state under `~/Library/pnpm`; sensitive local state under `~/.pi` | pnpm global manifest | declared AI Tool Surface | Keep Pi declared in `system/packages/pnpm-global.txt`. Pi is not excluded; only Pi-specific assets are outside the shared APM baseline until a future adapter policy promotes them. |
| ChatGPT and ChatGPT Atlas | Homebrew casks | app-local state outside this repo | Homebrew cask | canonical app surface | Keep install declarations in `system/packages/Brewfile`; no shared asset policy needed yet. |
| Ollama | Homebrew formula | local model storage outside this repo | Homebrew formula | canonical app surface | Keep install declaration in `system/packages/Brewfile`; model downloads are local state and not repo assets. |

<!-- markdownlint-enable MD013 -->

## Shared Asset Strategy

The shared source should be conceptual, not a copied tree per tool. Author each
Shared AI Asset once, declare and lock it through APM, and let APM materialize
the tool-specific output after target writes are approved.

The first Global AI Baseline should contain only:

- `grill-with-docs`

Do not include these globally yet:

- `using-superpowers`
- broad language or framework skills
- project-specific prompts, rules, or agents
- experimental tool-specific plugins
- Pi-specific assets and opencode-specific assets

If an asset is useful in one project, keep it in that project. Promote it only
after it has clear repeated cross-project value.

## Sensitive State Policy

Never commit these categories directly:

- auth tokens, API keys, OAuth material, session data, account identifiers, or
  credential helper state
- chat history, transcript files, local databases, logs, and memory stores
- trusted-project lists and per-project allow/permission lists
- vendor cache directories and plugin cache directories
- generated temporary files, shell snapshots, process-manager state, and app
  runtime helpers
- opencode gateway/account/auth state and local provider wrappers unless a
  future task extracts a sensitive-safe template

Safe repo-owned content belongs under `system/ai/` and should be limited to
declarations, documentation, redacted templates, generated adapters that contain
no secrets, and validation rules.

## Reset Approval Gate List

The following actions are destructive or state-moving and require explicit
approval in a later task:

- Run `apm install`, `apm update`, `apm prune`, `apm uninstall`,
  `apm self-update`, or any equivalent command that changes tool state.
- Add an APM manifest and then overwrite existing Codex, Claude, opencode, or
  Pi assets with generated adapters.
- Remove `~/.codex/skills/using-superpowers`.
- Remove cached Claude superpowers plugin versions or related installed plugin
  cache state.
- Remove, rewrite, or replace `~/.codex/skills/grill-with-docs` before APM can
  reproduce the intended baseline and a live deployment gate is approved.
- Remove Homebrew Claude casks or migrate `~/.local/share/claude`.
- Remove or migrate `~/.local/share/opencode` or `~/.config/opencode`.
- Delete or rewrite `~/.codex`, `~/.claude`, or any auth/history/cache/database
  subpaths.
- Change Codex trusted-project state, Claude permissions, or opencode provider
  configuration.
- Upgrade or relink Homebrew Codex or any AI cask/formula as part of cleanup.

Any cleanup task should first capture a Rebuild Snapshot outside the repo and
name exactly which files or directories are in scope.

## Later Implementation Roadmap

### P0 Declare Without Mutating

1. Accept ADR-0008 selecting APM as the AI Asset Manager.
2. Keep `system/packages/Brewfile` as the owner for AI app install surfaces:
   Codex, ChatGPT, ChatGPT Atlas, and Ollama.
3. Accept ADR-0009 selecting repo APM project files linked into `~/.apm`.
4. Keep the APM manifest and lockfile under `system/ai/apm/` as package
   evidence and source of truth for `grill-with-docs`.
5. Prefer `apm targets --json`, `apm lock`, and `apm audit --ci` before any
   command that deploys, prunes, updates, or uninstalls assets.
6. Record the intended generated targets for Codex, Claude Code, opencode, and
   future surfaces before running APM. Done for the shared baseline.
7. Add doctor checks for the selected baseline after an APM manifest exists.
   Done for Codex, Claude Code, and opencode.

### P1 Expose The APM Project

1. Link `~/.apm/apm.yml` to `system/ai/apm/apm.yml` through normal setup.
2. Link `~/.apm/apm.lock.yaml` to `system/ai/apm/apm.lock.yaml` through normal setup.
3. Let setup back up any existing live APM project files before replacing them.
4. Keep live target deployment blocked until a per-target write gate is
   approved. Done for Codex, Claude Code, and opencode.
5. Verify doctor reports repo APM files separately from live APM symlink state.

### P2 Cleanup Behind Approval

1. Snapshot current AI state.
2. Remove `using-superpowers` from global Codex and Claude surfaces only if a
   later ADR changes the Global AI Baseline.
3. Keep Pi declared through the pnpm global manifest unless a later policy
   moves it.
4. Keep opencode CLI ownership on the upstream Homebrew tap unless a later ADR
   chooses a better installer.
5. Tighten doctor so undeclared AI tools and assets are actionable drift.

## Open Questions

1. Should Pi receive any APM-managed shared assets if APM adds a confirmed Pi
   target or adapter model?
