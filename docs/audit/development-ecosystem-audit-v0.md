# Development Ecosystem Audit v0

Audit date: 2026-06-30.
Status: HISTORICAL. This audit predates the 2026-07 stabilization work
(JS toolchain cleanup, .NET migration to mise, Nushell and Cursor removal,
AI baseline deployment); its findings and score reflect that earlier state
and have since been addressed. For current state run `just doctor`.

Primary evidence:

- `just doctor --json`, reviewed on 2026-06-30. The doctor emits a fresh
  per-run timestamp in JSON output.
- `CONTEXT.md`.
- `docs/adr/*.md`.
- `README.md`.
- `system/packages/*`.
- `system/ai/*/README.md`.

This report is intentionally non-mutating. It does not install, uninstall,
migrate, remove, start services, stop services, clean caches, or rewrite
manifests.

## 1. Executive Verdict

Overall rating: **61/100**.

Recommendation: **repair and stabilize, not rebuild**.

The ecosystem is usable, but it is not yet a trustworthy living source of
truth. The strongest parts are the new language model in `CONTEXT.md`, the
ADR direction, the package manifests, and the read-only doctor. The weakest
parts are provenance drift, runtime split-brain, editor extension sprawl,
manual AI tooling, and a README/automation layer that still describes an older
"dotfiles bootstrap" world more than the current Orchestrator Repo model.

Brutal summary:

- The repo can describe the desired ecosystem better than it can reproduce it.
- JavaScript has too many owners: `fnm`, Homebrew `node`, Homebrew `pnpm`,
  npm globals, Corepack visibility, and Codex runtime candidates all appear.
- `.NET` policy says "one SDK source", but the active SDK is the Microsoft pkg
  while Homebrew `dotnet@8` is the declared stabilization candidate.
- Cursor is mostly undeclared reality: 2 of 6 declared extensions are present,
  while 23 installed Cursor extensions are not declared.
- AI tooling exists mostly as local/manual state, while `system/ai` is still
  scaffolding.
- Shell strategy is not settled. Nushell is primary for Alex, but this audit
  ran from a zsh/Codex context and global automation still contains POSIX
  `sh -c`.

## 2. Scorecard

<!-- markdownlint-disable MD013 -->

| Area | Weight | Score | Reason |
| --- | ---: | ---: | --- |
| Functionality/tooling | 25 | 21 | Most core tools are installed and usable. Missing declared editor and .NET items reduce confidence. |
| Install provenance and reproducibility | 30 | 14 | Too many important tools are present but undeclared, manual, legacy, duplicate, or unknown. |
| Runtime/version-manager hygiene | 15 | 7 | `fnm` is configured, but Homebrew `node`, npm globals, Corepack split, and `.NET` SDK source drift remain. |
| Structure/source-of-truth clarity | 15 | 11 | `CONTEXT.md`, ADRs, manifests, and doctor are strong. README and AI manifests lag behind. |
| Drift | 10 | 4 | Doctor reports declared-absent, present-undeclared, duplicate, legacy, manual, and unknown findings. |
| Security/sensitive-config handling | 5 | 4 | Sensitive-state language is good. Manual AI/local tooling still needs explicit safe boundaries. |
| **Overall** | **100** | **61** | Repairable, but not yet reproducible enough to trust as the full laptop source of truth. |

<!-- markdownlint-enable MD013 -->

## 3. Critical Findings First

### Finding 1: The source of truth is incomplete

Fact:

- Doctor found 36 findings.
- Classification counts: 18 canonical, 4 declared absent, 6 present
  undeclared, 1 duplicate, 1 legacy, 1 manual, and 5 unknown.
- Present but undeclared surfaces include Homebrew dev tools, VS Code
  extensions, Cursor extensions, pnpm globals, `.NET` global tools, AI CLIs,
  and manual bin tools.

Recommendation:

Every present dev tool needs one of three states:

- declared in a Package Manifest;
- documented as a Managed Exception;
- queued for later removal behind a Reset Approval Gate.

Until that is true, the repo is an audit log plus intent, not a full living
source of truth.

### Finding 2: Runtime ownership is not enforced

Fact:

- ADR-0005 says the ecosystem should use one Node runtime owner and one global
  JavaScript tool path.
- Doctor models `fnm exec --using default` as the trusted JS path.
- `fnm` default is `v22.17.1`.
- Current-process `node`, `npm`, and `npx` resolve to Homebrew paths in the
  reviewed Codex context.
- Current-process `pnpm` resolves to Codex runtime `pnpm`, while Homebrew
  `pnpm` `11.9.0` is also present as a candidate.
- Modeled `fnm` `pnpm` is `10.33.2`.
- npm globals exist under both `primary_fnm_default` and Homebrew npm.

Recommendation:

Treat `fnm` plus one pnpm path as the target unless ADR-0005 changes. Do not
remove anything yet. First, make the repair plan explicit and approval-gated.

### Finding 3: `.NET` SDK source violates the declared direction

Fact:

- ADR-0006 says the ecosystem should expose one canonical `.NET` SDK source.
- Homebrew `dotnet@8` is declared in `system/packages/Brewfile`.
- Doctor found active `dotnet` at `/usr/local/share/dotnet/dotnet` from the
  Microsoft pkg.
- Installed SDK reported by doctor: `8.0.412 [/usr/local/share/dotnet/sdk]`.

Recommendation:

Do a compatibility check before any removal. Then choose Homebrew `dotnet@8`
or Microsoft pkg as canonical and make the other a Managed Exception or
approval-gated removal candidate.

### Finding 4: Cursor is not reproducible from the repo

Fact:

- Cursor cask is declared and installed.
- Cursor extension manifest declares 6 extensions.
- Doctor found only 2 of 6 declared Cursor extensions installed.
- Doctor found 23 installed Cursor extensions not declared.

Recommendation:

Decide whether Cursor should mirror VS Code, be its own curated AI IDE, or be
treated as personal local state. Then update manifests later.

### Finding 5: AI tooling policy exists, but implementation does not

Fact:

- ADR-0002 defines AI Assets and an AI Asset Manager flow.
- ADR-0003 sets a minimal Global AI Baseline of only `grill-with-docs`.
- `system/ai` directories are placeholders.
- Doctor found `codex`, `pi`, `apm`, Codex runtime wrappers, and manual
  `claude` bin state.
- Doctor found `opencode-ai` as an npm global.

Recommendation:

Select an AI Asset Manager and declare AI Tool Surface install policy. Until
then, AI tools are mostly local state with good naming, not managed ecosystem
state.

### Finding 6: Shell friction is observable, but not resolved

Fact:

- Alex uses Nushell as the primary shell.
- Doctor execution context reported `shell_env_name` as `zsh`.
- Doctor did not appear to run from Nushell.
- Repo Nushell config is modeled as configuring `fnm`.
- Global just recipes still use POSIX `sh -c`.
- Cursor rules include old instructions to avoid bash/zsh, while ADR-0004 says
  automation and AI-executed commands should be POSIX-compatible unless a later
  ADR chooses otherwise.

Recommendation:

Make per-shell parity observable before choosing a shell future. The next
doctor iteration should compare Nu, zsh/login, zsh/non-login, and Codex
execution contexts.

## 4. Tool Provenance Table

Rows with grouped tool sets list all doctor-surfaced items in that set.

<!-- markdownlint-disable MD013 -->

| Tool | Detected source | Declared source | Classification | Drift | Recommended action |
| --- | --- | --- | --- | --- | --- |
| `brew` | `/opt/homebrew/bin/brew` | `system/packages/Brewfile` | canonical | None | Keep Homebrew as the main macOS package manifest. |
| Declared Homebrew formulae installed: `aws-sso-util`, `awscli`, `bat`, `carapace`, `direnv`, `dnscrypt-proxy`, `dotenv-linter`, `dotnet@8`, `editorconfig-checker`, `eza`, `fd`, `fnm`, `fzf`, `gh`, `git`, `gitleaks`, `gnupg`, `just`, `neovim`, `nushell`, `pnpm`, `ripgrep`, `ripsecrets`, `starship`, `topgrade`, `zlib`, `zoxide` | Homebrew formulae | `system/packages/Brewfile` | canonical | None reported for these formulae | Keep declared. Validate whether each still belongs in the baseline during later pruning. |
| Declared Homebrew casks installed: `arc`, `brave-browser`, `chatgpt`, `cursor`, `font-fira-code-nerd-font`, `ghostty`, `google-chrome`, `lulu`, `nordvpn`, `raycast`, `secretive`, `slack`, `spotify`, `visual-studio-code` | Homebrew casks | `system/packages/Brewfile` | canonical | None reported for these casks | Keep declared. Split dev, security, productivity, and personal apps later if useful. |
| `corepack` | Visible only through modeled `fnm` default, version `0.34.0` | Brewfile formula and ADR-0005 Corepack-managed pnpm policy | declared absent plus visible | Homebrew `corepack` formula missing, but `fnm` exposes Corepack | Decide whether Corepack should be managed by Node or Homebrew. Do not install yet. |
| `node` | Current process Homebrew `node` `26.4.0`; modeled `fnm` default `v22.17.1` | ADR-0005 favors one runtime owner, with `fnm` currently modeled | present undeclared and competing | Homebrew `node` competes with `fnm` | Migrate to one owner later, probably `fnm`, behind approval if uninstalling Homebrew node. |
| `npm` | Homebrew npm and modeled `fnm` npm `11.4.2` | npm globals prohibited except temporary migration exceptions | legacy and duplicate | npm globals exist in both trusted scopes | Freeze as migration debt. Remove npm globals only after approval. |
| `npx` | Homebrew and modeled `fnm` npm path | Implicit through Node/npm | canonical visibility | Multiple paths exist | Prefer `fnm` path once Node ownership is cleaned up. |
| `pnpm` | Homebrew `pnpm` `11.9.0`; modeled `fnm` pnpm `10.33.2`; Codex runtime candidate is current-process pnpm in the reviewed context | Brewfile plus `system/packages/pnpm-global.txt` | canonical plus unknown context | Current-process Codex/runtime pnpm cannot list globals because `~/Library/pnpm/bin` is not in PATH; trusted `fnm` scope works | Keep pnpm, but choose one canonical binary path and fix shell parity later. |
| `fnm` | Homebrew `fnm` `1.39.0` | Brewfile and Nushell config | canonical | 9 installed Node versions; no competing runtime managers found | Keep as current stabilization candidate. Document version-retention policy later. |
| Runtime managers: `asdf`, `goenv`, `jenv`, `mise`, `nodenv`, `nvm`, `pyenv`, `rbenv`, `rustup`, `sdkman`, `volta` | Not detected | Not declared | canonical absence | None | Keep absent unless a future ADR chooses a broader manager. |
| `dotnet` SDK | Active `/usr/local/share/dotnet/dotnet`, source `microsoft_dotnet_pkg` | Brewfile `dotnet@8`; ADR-0006 says one SDK source | unknown | Active SDK source differs from declared stabilization candidate | Evaluate compatibility, then select one SDK source behind approval. |
| `Amazon.Lambda.Tools` | Missing from installed `.NET` globals | `system/packages/dotnet-tools.txt` | declared absent | Declared but absent | Install later only after SDK source is resolved. |
| `Amazon.Lambda.TestTool-8.0` | Installed as `amazon.lambda.testtool-8.0` | `system/packages/dotnet-tools.txt` | canonical | Case/name normalization only | Keep declared. Verify command alias remains valid. |
| `amazon.lambda.testtool` | `.NET` global tool | Not declared | present undeclared | Extra test tool variant | Decide if needed, then declare or approval-gate removal. |
| `csharpier` | `.NET` global tool | Not declared | present undeclared | Extra formatter tool | Declare if intentional; otherwise approval-gate removal. |
| `deadcsharp` | `.NET` global tool | Not declared | present undeclared | Extra analysis tool | Declare if intentional; otherwise approval-gate removal. |
| `dotnet-ef` | `.NET` global tool | Not declared | present undeclared | Extra EF tool | Declare if intentional; otherwise approval-gate removal. |
| AWS CLI tools: `awscli`, `aws-sso-util` | Homebrew formulae | Brewfile | canonical | None reported | Keep. Avoid committing credentials or profile secrets. |
| VS Code app | Homebrew cask `visual-studio-code` | Brewfile | canonical | None for app | Keep. |
| VS Code declared extensions | `code --list-extensions`; 20 of 21 present | `system/packages/vscode-extensions.txt` and Brewfile `vscode` entries | declared absent | `github.copilot` missing | Install later or remove from manifest if intentionally absent. |
| VS Code undeclared extensions: `genaiscript.genaiscript-vscode`, `likec4.likec4-vscode` | VS Code extension inventory | Not declared | present undeclared | Extra extensions | Declare or approval-gate removal. |
| Cursor app | Homebrew cask `cursor`; manual `/usr/local/bin/cursor` also detected | Brewfile cask | canonical plus manual bin | CLI shim source is manual/app | Keep app; decide whether manual shim needs declaration. |
| Cursor declared extensions | Cursor extension inventory; 2 of 6 present | `system/packages/cursor-extensions.txt` | declared absent | Missing `biomejs.biome`, `ms-vscode.makefile-tools`, `ms-vscode.vscode-json`, `yzhang.markdown-all-in-one` | Decide Cursor policy, then install or trim manifest later. |
| Cursor undeclared extensions: `aliasadidev.nugetpackagemanagergui`, `amazonwebservices.aws-toolkit-vscode`, `anilkumarum.compile-ts`, `anysphere.cursorpyright`, `anysphere.remote-ssh`, `csharpier.csharpier-vscode`, `dbaeumer.vscode-eslint`, `dvirtz.parquet-viewer`, `editorconfig.editorconfig`, `esbenp.prettier-vscode`, `foxundermoon.shell-format`, `github.vscode-github-actions`, `ms-python.debugpy`, `ms-python.python`, `nrwl.angular-console`, `openai.chatgpt`, `saoudrizwan.claude-dev`, `sebastianbille.iam-legend`, `streetsidesoftware.code-spell-checker`, `streetsidesoftware.code-spell-checker-french`, `styled-components.vscode-styled-components`, `stylelint.vscode-stylelint`, `zixuanchen.vitest-explorer` | Cursor extension inventory | Not declared | present undeclared | 23 extra extensions | Curate Cursor as a first-class manifest or classify local state. |
| `@biomejs/biome` | pnpm global via trusted `primary_fnm_default` | `system/packages/pnpm-global.txt` | canonical | Cursor Biome extension missing | Keep CLI. Resolve editor extension policy separately. |
| `aws-cdk` / `cdk` | pnpm global declared; Homebrew npm also has `aws-cdk` | `system/packages/pnpm-global.txt` | duplicate | Duplicate npm global in Homebrew npm | Keep pnpm path. Remove npm duplicate only after approval. |
| `cdk-dia` | pnpm global via trusted `primary_fnm_default` | `system/packages/pnpm-global.txt` | canonical | None | Keep. |
| `markdownlint-cli` | pnpm global via trusted `primary_fnm_default` | Not declared | present undeclared | Used by repo lint recipe but absent from manifest | Add to pnpm manifest later if markdown lint remains part of baseline. |
| `opencode-ai` | npm global under `primary_fnm_default` | Not declared | legacy | npm global AI CLI package | Migrate to AI Asset Manager or pnpm/global manifest after tool choice. |
| `opencode` / `open-code` command | Not surfaced as PATH command by doctor | `system/ai/opencode` placeholder only | unknown absence | Package exists as `opencode-ai`, command not confirmed | Investigate before declaring or removing. |
| `pi` / `@mariozechner/pi-coding-agent` | pnpm command at `~/Library/pnpm/pi`; pnpm package undeclared | Not declared | present undeclared | AI CLI installed outside AI policy | Decide whether Pi belongs in Global AI Baseline or local state. |
| `codex` | Codex app resource plus Homebrew cask `codex` | Not declared in Brewfile; `system/ai/codex` placeholder | present undeclared | Homebrew cask is installed but undeclared; app runtime also present | Declare Codex install surface and managed config policy. |
| `codex-execve-wrapper`, `codex_chronicle` | Codex app/runtime paths | Not declared | unknown context | Runtime helper commands are environment context | Do not manage as normal tools unless Codex app policy requires it. |
| `claude` | Manual local bin `~/.local/bin/claude` | `system/ai/claude` placeholder only | manual | Manual AI CLI | Declare, migrate, or mark as local state after AI policy. |
| `apm` | Manual/pkg at `/usr/local/bin/apm` resolving to `/usr/local/lib/apm/apm` | `system/ai/apm` placeholder only | unknown/manual | Could be intended AI Asset Manager or unrelated legacy tool | Identify what this `apm` is before using it as canonical. |
| Docker/Colima tools: `colima`, `docker`, `docker-buildx`, `docker-completion`, `docker-compose` | Homebrew leaves | Not declared | present undeclared | Dev container stack exists outside manifests | Declare as baseline, move to manual manifest, or approval-gate removal. |
| `postman` | Homebrew cask | Not declared | present undeclared | API dev app outside manifest | Declare or approval-gate removal. |
| `composer` | Homebrew formula | Not declared | present undeclared | PHP package manager outside manifest | Declare if needed; otherwise approval-gate removal. |
| Manual bin tools: `apm`, `cursor`, `claude` | `/usr/local/bin`, `~/.local/bin` | `system/packages/manual-apps.md` has no candidates | manual | Manual local tools are not represented | Fill manual manifest or migrate to canonical installers later. |
| Manual apps manifest | Present | `system/packages/manual-apps.md` | canonical manifest | Empty despite manual tools | Use it for managed exceptions and approval-gated tools. |

<!-- markdownlint-enable MD013 -->

## 5. Dedicated Runtime-Manager Section

### Runtime Facts

- `fnm` is installed through Homebrew and declared in the Brewfile.
- Doctor statically models Nushell config as configuring `fnm`.
- `fnm default` is `v22.17.1`.
- `fnm` reports 9 installed Node versions:
  `v20.10.0`, `v20.13.1`, `v20.18.1`, `v22.10.0`, `v22.14.0`,
  `v22.17.1`, `v22.18.0`, `v24.14.1`, and `v25.9.0`.
- `fnm` reports `system_node_present: true`.
- No competing runtime manager signals were detected for `asdf`, `goenv`,
  `jenv`, `mise`, `nodenv`, `nvm`, `pyenv`, `rbenv`, `rustup`, `sdkman`, or
  `volta`.
- Current-process `node`, `npm`, and `npx` resolve through Homebrew paths in
  this zsh/Codex context.
- Current-process `pnpm` resolves through Codex runtime, while Homebrew `pnpm`
  `11.9.0` is also visible as a candidate.
- Trusted pnpm global drift is collected through `fnm exec --using default`.
- Current-process Codex/runtime pnpm failed global listing because the
  configured global bin directory `~/Library/pnpm/bin` is not in PATH.
- `corepack` is missing as a Homebrew formula, but visible through modeled
  `fnm` default.
- `FNM_COREPACK_ENABLED` was reported as `false`.
- Active `.NET` comes from Microsoft pkg, not the declared Homebrew `dotnet@8`
  candidate.

### Policy

`fnm` should remain the stabilization candidate unless ADR-0005 is superseded.
The policy should be:

- one Node runtime owner;
- one global JS package path;
- no npm globals except temporary migration exceptions;
- one `.NET` SDK source;
- all runtime exceptions explicitly declared.

### Tool-Choice ADR Need

ADR-0005 and ADR-0006 already cover the target direction. The next ADRs should
not repeat those decisions unless Alex wants to change them.

Potential next ADRs:

- final shell strategy after per-shell parity evidence;
- AI Asset Manager choice;
- Docker/Colima baseline policy;
- editor extension boundary between VS Code and Cursor.

## 6. Shell Strategy Section

### Nushell Strengths

Facts:

- Nushell is declared in the Brewfile and installed.
- `system/nushell/config.nu` configures Homebrew paths, `fnm`, `.NET` tools,
  aliases, Starship, zoxide, carapace, and direnv.
- `system/nushell/env.nu` declares `PNPM_HOME` and prepends it to PATH.
- `CONTEXT.md` now defines Primary Shell, Compatibility Shell, Shell Parity,
  AI Shell Friction, and Automation Shell.

Assessment:

Nushell remains a strong interactive shell for Alex because it provides
structured data, explicit config, and good daily ergonomics. The risk is not
Nushell itself. The risk is pretending the rest of the ecosystem speaks Nu.

### zsh/POSIX Compatibility Friction

Facts:

- This audit ran from Codex with `SHELL=/bin/zsh`.
- Doctor reported no Nushell parent process.
- Several global just recipes use `sh -c`.
- `install-node-tools` sources a Nushell env file from a just recipe in a way
  that is suspicious for POSIX execution.
- Cursor rules still contain old "use Nushell, not bash/zsh" guidance.
- ADR-0004 says automation and AI-executed commands should be POSIX-compatible
  unless a later Tool-Choice ADR chooses otherwise.

Assessment:

AI/Codex, installers, README examples, and common package documentation assume
POSIX shell semantics. Nushell can stay primary only if POSIX automation remains
healthy and visible.

### Observability

Current repo observability is better than before because doctor records:

- process chain;
- `SHELL`;
- PATH entries;
- Nushell environment signals;
- modeled `fnm` behavior;
- current-process vs trusted JS toolchain scopes.

Still missing:

- explicit doctor modes for Nu, zsh login, zsh non-login, and Codex;
- a shell parity table for PATH, `PNPM_HOME`, `FNM_*`, `.NET`, and aliases;
- pass/fail policy for which shell contexts must be supported.

### Investigation Before a Shell Decision

Do not choose Nu-only, zsh+Nu, or zsh-primary yet. First answer:

- Which shell launches the GUI editors' integrated terminals?
- Which shell should `just bootstrap` assume?
- Which shell should Codex-generated commands target?
- Does Nu provide enough daily advantage to justify dual-shell support?
- Can shared environment generation remove most duplication?

## 7. AI Tooling Section

### AI Tooling Facts

- `system/ai` exists but only contains placeholder README files.
- ADR-0002 says custom AI assets should be consumed through the AI Asset
  Manager flow.
- ADR-0003 says the Global AI Baseline starts with only `grill-with-docs`.
- Doctor found Codex commands from the app/runtime and Homebrew cask.
- Doctor found `pi` from pnpm.
- Doctor found `apm` from a manual/pkg path.
- Doctor found `claude` as a manual local bin.
- Doctor found `opencode-ai` as an npm global.
- No canonical AI package source is declared yet.

### Assessment

Codex, Claude, opencode/opencode-ai, Pi, and APM are the least reproducible
part of the ecosystem. The repo has the right vocabulary but not the install
or verification model.

### Shared Skills, Prompts, and Assets Policy

Keep the policy small:

- Global AI Baseline stays minimal until repeated cross-project use proves
  expansion is worth it.
- Shared assets should be authored once and adapted per AI Tool Surface.
- Tool-specific generated adapters are allowed if safe to commit.
- Built-in vendor assets, auth, histories, caches, trusted-project databases,
  and local logs stay out of git.
- Third-party and custom AI assets should use the same declared package flow.

### What Is Manual or Undeclared

- Codex app/cask state.
- `claude` local CLI.
- `opencode-ai` npm global.
- Pi coding agent pnpm global.
- `apm` manual/pkg CLI.
- Shared AI asset declarations.
- Tool-specific managed configs for Codex, Claude, opencode, and Pi.

### What Should Move to APM or Package Manifests Later

- The selected AI Asset Manager itself.
- Baseline AI assets.
- Third-party AI assets.
- Custom companion-repo AI assets.
- Tool-surface adapters for Codex, Claude, Cursor, opencode, and Pi.
- Verification checks that prove each tool surface can see the intended assets.

## 8. Drift Matrix

### Declared but Absent

- Homebrew formula: `corepack`.
- VS Code extension: `github.copilot`.
- Cursor extensions: `biomejs.biome`, `ms-vscode.makefile-tools`,
  `ms-vscode.vscode-json`, `yzhang.markdown-all-in-one`.
- `.NET` global tool: `Amazon.Lambda.Tools`.

### Present but Undeclared

- Homebrew formulae: `colima`, `composer`, `docker`, `docker-buildx`,
  `docker-completion`, `docker-compose`, `node`.
- Homebrew casks: `codex`, `postman`.
- VS Code extensions: `genaiscript.genaiscript-vscode`,
  `likec4.likec4-vscode`.
- Cursor extensions: 23 undeclared extensions listed in the provenance table.
- pnpm globals: `@mariozechner/pi-coding-agent`, `markdownlint-cli`.
- `.NET` global tools: `amazon.lambda.testtool`, `csharpier`, `deadcsharp`,
  `dotnet-ef`.
- AI/dev PATH commands without canonical AI package source: `codex`, `pi`,
  `apm`, Codex runtime helpers.

### Duplicate

- `aws-cdk` appears in the canonical pnpm globals and Homebrew npm globals.
- Node runtime ownership is effectively duplicated by `fnm` and Homebrew
  `node`.
- pnpm visibility is split across Homebrew, modeled `fnm`, and Codex runtime
  candidates.

### Manual or Local

- `/usr/local/bin/apm`.
- `/usr/local/bin/cursor`.
- `~/.local/bin/claude`.
- Codex app runtime helper commands.
- Empty manual-apps manifest despite manual bin tools.

### Legacy

- npm globals under `primary_fnm_default`: `corepack`, `npm`, `opencode-ai`.
- Homebrew npm global: `npm`.
- Homebrew `node` if ADR-0005 remains unchanged.

### Unknown Provenance or Policy

- Active `.NET` Microsoft pkg source relative to ADR-0006.
- Whether `apm` is the intended AI Asset Manager.
- Whether `opencode-ai` is intended, legacy, or experimental.
- Whether Postman, Docker/Colima, Composer, and Codex cask belong in the
  baseline.
- Whether current Codex/zsh PATH should be expected to match Nushell PATH.

## 9. Recommendations

### Keep

- Keep `just doctor` as the read-only audit entrypoint.
- Keep `CONTEXT.md` as the language authority.
- Keep ADR-0001 through ADR-0006 as current governance.
- Keep Homebrew, pnpm globals, `.NET` globals, VS Code extensions, Cursor
  extensions, and manual apps as separate manifest categories.
- Keep `fnm` as the current Node stabilization candidate unless ADR-0005
  changes.
- Keep Reset Approval Gates for destructive cleanup.

### Add

- Add a manual/local tools manifest entry for `apm`, `cursor`, and `claude`,
  or migrate them later.
- Add a shell parity doctor section for Nu and zsh contexts.
- Add AI package declarations once the AI Asset Manager is selected.
- Add `markdownlint-cli` to pnpm globals later if markdown lint is intended.
- Add declared policy for Docker/Colima, Postman, Composer, and Codex.
- Add a version-retention policy for installed `fnm` Node versions.

### Remove

Do not remove anything in this task.

Later removal candidates:

- npm global `aws-cdk` duplicate.
- npm global `opencode-ai` if migrated.
- Homebrew `node` if `fnm` remains canonical.
- undeclared editor extensions that Alex does not want.
- unused `.NET` global tools.
- obsolete `fnm` Node versions.

### Migrate

- Migrate JavaScript global tools to one pnpm path.
- Migrate `.NET` to one SDK source.
- Migrate AI CLIs and assets to the selected AI Asset Manager or package
  manifests.
- Migrate manual bin shims into declared install paths or Managed Exceptions.
- Migrate README setup docs from old bootstrap claims to the current
  Orchestrator Repo model.

### Rewrite

- Rewrite README runtime sections after Node and `.NET` source decisions.
- Rewrite shell docs around Primary Shell, Compatibility Shell, and Automation
  Shell.
- Rewrite bootstrap recipes that append directly to local config or assume a
  shell that is not guaranteed by `just`.
- Rewrite Cursor AI rules that conflict with ADR-0004.

### Needs ADR

- Shell strategy final decision.
- AI Asset Manager selection.
- Docker/Colima development-container baseline.
- VS Code vs Cursor extension policy.

### Needs User Approval Before Destructive Action

- Removing Homebrew `node`.
- Removing npm globals.
- Removing Microsoft `.NET` pkg or Homebrew `dotnet@8`.
- Removing editor extensions.
- Removing manual bin tools.
- Removing old `fnm` Node versions.
- Removing or replacing AI assets, AI configs, caches, histories, or trusted
  state.

## 10. Prioritized Roadmap

### P0 Reproducibility and Source-of-Truth Failures

1. Decide canonical ownership for Node, pnpm, npm globals, and Corepack.
2. Decide canonical `.NET` SDK source after compatibility checks.
3. Declare or classify all present undeclared Homebrew dev tools and casks.
4. Declare or classify AI Tool Surface CLIs and manual bin tools.
5. Add shell parity checks to doctor for Nu and zsh/Codex contexts.
6. Make manual-apps manifest useful for approval-gated tools.

### P1 Inconsistent Install Methods

1. Move npm globals out of the steady-state path.
2. Resolve pnpm current-process PATH failure.
3. Normalize VS Code and Cursor extension policy.
4. Decide whether Docker/Colima/Postman/Composer are baseline tools.
5. Decide whether `markdownlint-cli` belongs in pnpm globals.
6. Decide Codex install source: Homebrew cask, app-managed, or manual.

### P2 Cleanup and Docs

1. Rewrite README to match Orchestrator Repo language.
2. Refresh Cursor rules so they do not fight ADR-0004.
3. Document Node version retention.
4. Document `.NET` tool naming and alias policy.
5. Add AI asset package docs once APM or replacement is selected.
6. Consider stricter doctor exit behavior once drift classifications are stable.

## 11. Open Questions for Alex

1. Should the shell future be Nushell primary plus POSIX automation, zsh
   primary, or generated parity for both?
2. Is Homebrew `node` intentional, or should `fnm` be the only Node owner?
3. Should active `.NET` remain Microsoft pkg, or should Homebrew `dotnet@8`
   become the real SDK source?
4. Are Docker/Colima, Postman, Composer, and Codex part of the baseline?
5. Should Cursor mirror VS Code extensions, or have its own curated AI IDE
   manifest?
6. Is `/usr/local/bin/apm` the intended AI Asset Manager?
7. Should `opencode-ai`, Pi, Claude, and Codex all be managed AI Tool Surfaces?
