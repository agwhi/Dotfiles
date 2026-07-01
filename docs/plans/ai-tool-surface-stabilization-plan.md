# AI Tool Surface Stabilization Plan

Date: 2026-07-01.

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
Orchestrator Repo should declare only the laptop's Global AI Baseline and let
APM install, lock, link, verify, and adapt it.

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

- Homebrew declares `ollama`, `chatgpt`, `chatgpt-atlas`, and `codex`.
- Codex is installed as Homebrew cask `codex` version `0.142.4`; Homebrew
  metadata reports available cask version `0.142.5`. This task does not upgrade
  it.
- Codex app runtime also exposes `/Applications/Codex.app/Contents/Resources`
  commands in the current app context.
- APM is present at `/usr/local/bin/apm`, resolves to `/usr/local/lib/apm/apm`,
  and reports version `0.23.1`.
- APM uses `apm.yml` and `apm.lock.yaml` for package declarations and locks.
  `apm lock` writes a lockfile without deploying files, while `apm install`,
  `apm update`, `apm prune`, `apm uninstall`, and `apm self-update` mutate
  local state.
- Claude Code is present at `~/.local/bin/claude`, resolves to
  `~/.local/share/claude/versions/2.1.197`, and reports `2.1.197`.
- opencode is installed as npm global `opencode-ai` version `1.16.2` under the
  `fnm` default Node, with a binary under the `fnm` default alias path. It is
  not visible as `opencode` on the current Codex process PATH.
- Pi is installed as pnpm global `@mariozechner/pi-coding-agent` version
  `0.73.0`, exposed through `~/Library/pnpm/pi`, and is not declared in
  `system/packages/pnpm-global.txt`.
- `~/.codex`, `~/.claude`, `~/.local/share/opencode`, and `~/.config/opencode`
  contain sensitive User-Managed AI State, histories, caches, auth-adjacent
  files, trusted-project state, local databases, generated adapters, and plugin
  caches.
- `~/.codex/skills` currently includes system skills, runtime skills,
  `grill-with-docs`, and `using-superpowers`.
- Claude plugin caches include installed third-party or official plugin state,
  including cached superpowers versions.

## Tool Surface Classification

<!-- markdownlint-disable MD013 -->

| Tool or surface | Current binaries | Config and state paths | Current provenance | Classification | Recommendation |
| --- | --- | --- | --- | --- | --- |
| APM | `/usr/local/bin/apm` -> `/usr/local/lib/apm/apm` | future repo manifest under `system/ai/apm/`; current install tree under `/usr/local/lib/apm` | manual/pkg | canonical target plus managed exception | Use APM as the AI Asset Manager, but treat the current binary provenance as unresolved until the install/update path is declared. Do not run `apm install`, `apm update`, `apm prune`, `apm uninstall`, or `apm self-update` without approval. |
| Codex CLI | `/opt/homebrew/bin/codex`; app resource binary in `/Applications/Codex.app` | `~/.codex` plus app/runtime cache paths | Homebrew cask plus app runtime | canonical install surface | Keep Codex declared through Homebrew. Keep `~/.codex` as Sensitive Local State except for safe generated adapters or declarations explicitly added under `system/ai/codex`. |
| Codex runtime helpers | `codex-execve-wrapper`, `codex_chronicle` in Codex app/runtime paths | Codex app runtime directories and temporary command wrappers | app_runtime | managed context | Do not classify these as package-manager drift. They are execution context from the Codex app. |
| Codex skills | `~/.codex/skills/grill-with-docs`, `~/.codex/skills/using-superpowers`, system/runtime skills | `~/.codex/skills`, `~/.codex/plugins`, `~/.codex/vendor_imports` | manual/local plus app/runtime | mixed | Keep `grill-with-docs` as the only target baseline. Treat `using-superpowers` as approval-gated cleanup. Treat system/runtime skills and plugin caches as vendor/app state unless intentionally promoted. |
| Claude Code | `~/.local/bin/claude` -> `~/.local/share/claude/versions/2.1.197` | `~/.claude`, `~/.claude.json`, `~/.local/share/claude` | manual/local | managed exception | Keep documented as manual-local until APM or a declared installer owns cross-surface assets. Do not remove or migrate existing Claude state without a snapshot and approval. |
| Claude plugins and commands | plugin cache under `~/.claude/plugins` | `~/.claude/plugins/cache`, `~/.claude/plugins/marketplaces`, install manifests | Claude-managed local cache | manual local / approval-gated cleanup | Do not commit cache contents. Reinstall selected shared assets through APM later, then remove old cache copies only behind approval. |
| opencode | `opencode-ai` npm global binary under the `fnm` default alias path | `~/.local/share/opencode`, `~/.config/opencode` | npm global plus local config | legacy managed exception | Do not add to the Global AI Baseline now. Decide later whether opencode is a project-local tool, declared AI Tool Surface, or removal candidate. |
| Pi | `~/Library/pnpm/pi` | pnpm global package `@mariozechner/pi-coding-agent` | pnpm global | project-local / approval-gated removal | Do not add to `system/packages/pnpm-global.txt` as a canonical baseline. Migrate to APM or remove only after approval. |
| ChatGPT and ChatGPT Atlas | Homebrew casks | app-local state outside this repo | Homebrew cask | canonical app surface | Keep install declarations in `system/packages/Brewfile`; no shared asset policy needed yet. |
| Ollama | Homebrew formula | local model storage outside this repo | Homebrew formula | canonical app surface | Keep install declaration in `system/packages/Brewfile`; model downloads are local state and not repo assets. |

<!-- markdownlint-enable MD013 -->

## Shared Asset Strategy

The shared source should be conceptual, not a copied tree per tool. Author each
Shared AI Asset once, then let APM produce or install the tool-specific adapter
for Codex, Claude Code, opencode, Pi, or another AI Tool Surface.

The first APM-managed baseline should contain only:

- `grill-with-docs`

Do not include these globally yet:

- `using-superpowers`
- broad language or framework skills
- project-specific prompts, rules, or agents
- experimental tool-specific plugins
- Pi or opencode assets

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
- Remove, rewrite, or replace `~/.codex/skills/grill-with-docs` before APM has
  reproduced the same intended baseline.
- Remove pnpm global `@mariozechner/pi-coding-agent` or `~/Library/pnpm/pi`.
- Remove npm global `opencode-ai` or its `fnm` alias binary.
- Remove or migrate `~/.local/bin/claude` or `~/.local/share/claude`.
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
3. Add an APM manifest under `system/ai/apm/` only after reviewing the exact
   schema and deciding the source for `grill-with-docs`.
4. Prefer `apm targets --json`, `apm lock`, and `apm audit --ci` before any
   command that deploys, prunes, updates, or uninstalls assets.
5. Record the intended generated targets for Codex, Claude Code, opencode, and
   future surfaces before running APM.
6. Add doctor checks for the selected baseline after an APM manifest exists.

### P1 Reproduce The Baseline

1. Use APM lock/audit commands in read-only mode first.
2. Install or compile only `grill-with-docs` into approved targets.
3. Verify Codex and Claude can discover the APM-installed baseline.
4. Compare installed outputs with current local `grill-with-docs`.
5. Decide whether opencode and Pi should consume the same shared baseline.

### P2 Cleanup Behind Approval

1. Snapshot current AI state.
2. Remove `using-superpowers` from global Codex and Claude surfaces if the APM
   baseline works.
3. Remove or migrate Pi if it is not a baseline AI Tool Surface.
4. Remove or migrate `opencode-ai` if it is not a declared AI Tool Surface.
5. Tighten doctor so undeclared AI tools and assets are actionable drift.

## Open Questions

1. Which repository or package source should own the canonical `grill-with-docs`
   asset consumed by APM?
2. Should Claude Code itself remain manually installed, or should a later task
   find a declared installer for the CLI binary separately from assets?
3. Should opencode remain available as a project-local experiment, or should it
   be removed after APM/Codex/Claude coverage is stable?
4. Should Pi be intentionally excluded, or is there a specific project that
   should own it locally?
