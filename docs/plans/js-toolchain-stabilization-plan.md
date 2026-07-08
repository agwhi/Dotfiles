# JavaScript Toolchain Stabilization Plan

Date: 2026-07-01.
Status: completed. Historical record; current state comes from `just doctor`
and the package manifests.

This plan is non-mutating. It does not install, uninstall, migrate, delete, edit
PATH, or clean local state. It turns the current JavaScript toolchain drift into
an approval-gated implementation plan.

## Recommended Target State

Use `fnm` as the Node runtime owner. Homebrew remains the Canonical Installer
for `fnm`, but Homebrew `node` is not a steady-state runtime owner.

Use one pnpm global tool path: the `fnm` default Node plus Corepack/pnpm path
that doctor already models with `fnm exec --using default`. Keep
`system/packages/pnpm-global.txt` as the Package Manifest for global JavaScript
tools.

Use Corepack from the selected `fnm` default Node for the stabilization target.
Do not install Homebrew `corepack` now: local `brew info corepack --json=v2`
reports that it depends on Homebrew `node` and conflicts with Homebrew `pnpm`,
which would preserve split ownership.

Treat `mise` as a credible runtime manager for other runtimes, not as the Node
owner for this ecosystem. The repo's general philosophy is to choose the
best-fit tool for each runtime rather than consolidating under one generic
manager.

## Evidence

Grounding from `just doctor --json` generated at
`2026-06-30T22:10:20.362360+00:00`, reviewed locally on 2026-07-01:

- `fnm` is declared in `system/packages/Brewfile`, installed through Homebrew,
  and visible at `/opt/homebrew/bin/fnm`.
- Doctor models `fnm exec --using default` as the trusted JS scope.
- `fnm default` is `v22.17.1`.
- Modeled `fnm` commands are available: `node` `v22.17.1`, `npm` `11.4.2`,
  `npx` `11.4.2`, `pnpm` `10.33.2`, and `corepack` `0.34.0`.
- Current-process `node`, `npm`, and `npx` now resolve through the `fnm`
  default Node path after the 2026-07-05 cleanup.
- Current-process `pnpm` resolves through the `fnm`/Corepack path. A Codex
  runtime `pnpm` can still appear as an execution-context candidate, but it is
  not treated as canonical laptop state.
- Homebrew `node` and Homebrew `pnpm` were removed on 2026-07-05.
- Homebrew `corepack` is absent and intentionally not declared.
- `FNM_COREPACK_ENABLED` is not set in the current shell probes.
- Trusted pnpm globals now include declared development CLIs plus the declared
  Pi CLI and extension packages. Declared non-Pi pnpm globals were refreshed
  on 2026-07-07: `@biomejs/biome` `2.5.2`, `aws-cdk` `2.1129.0`,
  `cdk-dia` `0.12.3`, and `markdownlint-cli` `0.49.0`.
- npm reports only `corepack` and `npm` under `primary_fnm_default`; doctor
  classifies those as runtime-owned packages from the selected fnm Node
  installation rather than user-global drift.
- The undeclared npm global `context-mode` was removed on 2026-07-07 after no
  current AI harness config referenced it and Alex did not recognize it.
- The old Homebrew npm scope was removed with Homebrew `node`, and
  `opencode-ai` was removed when opencode CLI ownership moved to Homebrew.
- Stale Homebrew-prefix Node-global leftovers under
  `/opt/homebrew/lib/node_modules` and `/opt/homebrew/bin/cdk` were removed on
  2026-07-07 so `cdk` resolves through the declared pnpm global path.
- No competing runtime manager signals were detected for `mise`, `asdf`,
  `nodenv`, `nvm`, `volta`, or related managers.

Repo grounding:

- ADR-0005 says the ecosystem should have one Node runtime owner and one global
  JS tool path.
- `system/zsh/.zshrc` activates `fnm` with `fnm env --shell zsh --use-on-cd`
  for interactive zsh.
- `system/zsh/.zshenv` sets expanded `PNPM_HOME`.
- `justfile` should use the repo JS wrapper instead of trusting whatever
  `node`, `corepack`, or `pnpm` appears first in the current shell context.

External primary sources used:

- [fnm README](https://github.com/Schniz/fnm/blob/master/README.md)
- [Corepack README](https://github.com/nodejs/corepack#readme)
- [mise Node docs](https://mise.jdx.dev/lang/node.html)
- [mise activate docs](https://mise.jdx.dev/cli/activate.html)

## Decision Matrix

<!-- markdownlint-disable MD013 -->

| Option | Laptop reproducibility | Shell integration | POSIX/zsh/Codex friendliness | Project-local version files | Corepack/pnpm behavior | AI-agent ergonomics | Long-term maintenance risk | Migration cost | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Keep `fnm` | Strongest current fit: declared, installed, modeled by doctor, and already configured in repo Nu files. | Good enough in this repo through `fnm env --json`; official shell output lists bash/zsh/fish/powershell, so Nu support is repo-integrated rather than first-class shell output. | Good when commands use `fnm exec --using default`; current Codex/zsh PATH still needs parity work. | Strong: fnm supports `.node-version`, `.nvmrc`, and engines resolution; current Nu hook already runs `fnm use --install-if-missing`. | Good with the `fnm` default Node. Corepack is visible now, but `FNM_COREPACK_ENABLED=false` and Node 25+ needs a caveat. | Strong: explicit `fnm exec --using default` gives Codex a deterministic command prefix independent of runtime PATH. | Medium-low: specialized scope, few moving parts, but Corepack distribution changes after Node 24 must be watched. | Low: no runtime-manager migration; cleanup is mostly removing duplicates later. | Select. |
| Replace `fnm` with `mise` | Credible for projects that already standardize on `mise`, but no local evidence shows better Node-specific Tool Fit than `fnm`. | Strong: `mise activate` supports common shells and shim-based workflows. | Strong: supports activation and shims across common shells, but would require new parity policy. | Strong but not free: `.nvmrc`, `.node-version`, and `devEngines` support require explicit enabling. | Strong potential: `node.corepack` can install Corepack shims after Node installs. | Good after migration, but agents would need new commands, shims, and docs. | Medium: broader surface area and more settings for a problem already solved by `fnm`. | High: replace installed/configured runtime manager, update docs, doctor, zsh, recipes, manifests, and cleanup old fnm state. | Reject for this ecosystem unless a later Node-specific ADR proves stronger Tool Fit. |
| Use Homebrew `node` only | Weak for a living laptop source of truth because it makes the Node version track Homebrew rather than project/runtime policy. | Simple PATH behavior, but no runtime-manager integration in Nu. | Simple in zsh/Codex, but only because it ignores project-local switching. | Weak: no native `.node-version` or `.nvmrc` switching. | Mixed: Homebrew `pnpm` is present, Homebrew `corepack` is absent, and local metadata says Homebrew `corepack` depends on Homebrew `node` and conflicts with `pnpm`. | Weak: current simplicity hides global version drift and encourages current-process assumptions. | Medium-high: Homebrew upgrades can change Node major versions outside project intent. | Medium: would need to discard ADR-0005's modeled direction and migrate fnm-owned state. | Reject. |
| Other specialized Node manager (`volta`, `nvm`, `nodenv`) | No current repo or doctor evidence supports introducing one. | Unknown to this repo; would require new shell work. | Variable; no candidate beats current `fnm` evidence. | Variable, but not enough to justify churn. | Variable; no stronger Corepack/pnpm story is proven here. | Worse initially: new agent commands and docs without local evidence. | Medium-high because it adds a new owner while solving the same class of problem. | High relative to benefit. | Do not pursue unless a specific blocker appears. |

<!-- markdownlint-enable MD013 -->

## Why `fnm` Wins For Alex

`fnm` is the best Tool Fit for the current Stabilization goal. It is already
declared, installed, configured in zsh, and trusted by doctor. It is a
Specialized Tool, which is a feature here: the problem is not that Alex lacks a
generic runtime manager, it is that one existing Node manager has not been made
the only owner yet.

`mise` is a serious runtime manager, and it may be the right owner for another
runtime. That does not make it the right Node owner. This ecosystem optimizes
for Tool Fit over consolidation, and `fnm` is already the specialized, declared,
installed, and modeled trusted Node path.

Homebrew `node` should not be selected as owner. It is currently present and
usable, but that is drift, not a policy. Making it canonical would trade away
project-local Node switching and would let Homebrew upgrades decide the active
Node major version.

## Why `fnm` Wins For AI And Codex Workflows

Codex runs in a zsh/current-process context where PATH can include Codex
runtime tools. The current doctor output proves that: current-process `pnpm`
is Codex runtime `pnpm`, while trusted laptop pnpm is available through
`fnm exec --using default`.

The stable agent contract should therefore be explicit:

```sh
fnm exec --using default node --version
fnm exec --using default corepack --version
fnm exec --using default pnpm --version
fnm exec --using default pnpm list -g --depth 0 --json
```

That keeps AI-executed commands independent of whether the session was launched
from zsh, the Codex app, another AI command surface, or an editor terminal.

## Corepack Decision

Corepack policy: `fnm_node`.

Use the Corepack that comes from the selected `fnm` default Node for the current
stabilization target. Corepack's primary README says Corepack is distributed
with Node from `14.19.0` up to, but not including, `25.0.0`; this machine's
default is `v22.17.1`, so the current target is valid.

Node 25+ caveat: if the default Node moves to 25 or newer, re-evaluate Corepack
before changing the default. At that point, the options are an npm-installed
Corepack under the `fnm` Node, a different Node LTS default, or a new tool
choice. Do not preemptively choose Homebrew `corepack`, because local Homebrew
metadata says it depends on Homebrew `node` and conflicts with Homebrew `pnpm`.

Later implementation should enable Corepack in the `fnm` path deliberately,
probably by adding `--corepack-enabled` to the `fnm env --json` flow or by
running an explicit `fnm`-scoped Corepack setup command after Alex approves the
cleanup plan. This task does neither.

## Steady-State Policy

Homebrew `node`:
Not a steady-state owner. It was removed on 2026-07-05 after shell parity
confirmed `node`, `npm`, and `npx` resolve through the `fnm` default Node path.
Do not reintroduce it unless a future Homebrew formula or workflow requires it
explicitly.

Homebrew `pnpm`:
Not a steady-state owner. It was removed on 2026-07-05 after pnpm resolved
through the `fnm`/Corepack path and global packages were verified there.

Homebrew `corepack`:
Not a steady-state owner. It is absent and not declared. Installing it would
pull toward Homebrew `node` ownership.

npm globals under `primary_fnm_default`:
Runtime-owned packages only. Current packages are `corepack` and `npm`, both
inside the selected fnm Node installation. Do not manually remove them as
user-global cleanup; reinstall or repair the fnm Node version if either becomes
corrupt.

npm globals under Homebrew npm:
Removed on 2026-07-05 with Homebrew `node`. A stale Homebrew-prefix
`aws-cdk` copy and `cdk` symlink were removed on 2026-07-07. `aws-cdk`
remains available through the declared pnpm global path.

pnpm global packages:
Keep `@biomejs/biome`, `aws-cdk`, `cdk-dia`, and `markdownlint-cli` as
declared globals for now. Keep Pi declared through the maintained
`@earendil-works/pi-coding-agent` package plus the declared Pi extension
packages because Alex uses Pi as part of the AI workflow. Declared pnpm
globals are intentionally unpinned and should be refreshed through the
canonical fnm/pnpm path.

Current-process Codex runtime `pnpm`:
Non-canonical context only. Do not use it to make laptop drift claims or install
global tools. Prefer `fnm exec --using default pnpm ...` in doctor, docs, and
AI-executed recipes until shell parity is strict.

`npx`:
Owned by the selected `fnm` Node/npm path. Use current-process `npx` only as
context until PATH parity proves Homebrew `npx` is no longer first.

## What Not To Do

- Do not install `mise` during this stabilization pass.
- Do not make Homebrew `node` the runtime owner.
- Do not install Homebrew `corepack` while trying to remove Homebrew `node`
  ownership.
- Do not keep both Homebrew `pnpm` and Corepack/fnm pnpm as equal owners.
- Do not add new npm globals except as explicitly approved migration steps.
- Do not manually remove runtime-owned `npm` or `corepack` from the active fnm
  Node installation.
- Do not remove Homebrew `node`, Homebrew `pnpm`, pnpm globals, or `fnm` Node
  versions without a Reset Approval Gate.
- Do not treat Codex runtime `pnpm` as laptop state.

## Reset Approval Gate List

Destructive or state-moving actions that need explicit approval later:

- Remove pnpm global `markdownlint-cli` if Alex decides it is not baseline.
- Remove old `fnm` Node versions after a retention policy is documented:
  `v20.10.0`, `v20.13.1`, `v20.18.1`, `v22.10.0`, `v22.14.0`, `v22.18.0`,
  `v24.14.1`, and `v25.9.0`.
- Replace `fnm` with `mise` if a future ADR chooses that Stabilizing
  Replacement.
- Rewrite shell PATH ownership for zsh/Codex/AI command surfaces after shell
  parity checks.
- Move or remove any AI CLI, cache, config, history, or trusted-project state.

## Later Manifest Changes

Do not make these changes in this task. They are the expected source-of-truth
edits after Alex approves the target state.

`system/packages/Brewfile`:

- Keep `brew "fnm"`.
- Remove `brew "corepack"`.
- Remove `brew "pnpm"`.
- Do not add `brew "node"`.
- Consider a comment that Homebrew installs the manager, not the Node runtime.

`system/packages/pnpm-global.txt`:

- Keep `@biomejs/biome`.
- Keep `aws-cdk`.
- Keep `cdk-dia`.
- Keep `markdownlint-cli` because markdown lint is part of the repo validation
  path.
- Do not reintroduce the deprecated `@mariozechner/pi-coding-agent` package;
  use the declared `@earendil-works/pi-coding-agent` package instead.

`system/zsh/.zshenv` and `system/zsh/.zshrc`:

- Keep `fnm env --shell zsh --use-on-cd` for interactive zsh unless a future
  ADR changes it.
- Add an explicit Corepack enablement policy for the `fnm` path.
- Keep `PNPM_HOME` expanded for trusted `fnm` pnpm, and document why
  current-process Codex runtime `pnpm` is excluded.

`justfile`:

- Change JS recipes to use `fnm exec --using default` instead of whatever
  `corepack` or `pnpm` appears first in the current shell.
- Keep recipes on explicit wrappers rather than shell startup side effects.
- Make `install-node-tools` install from `system/packages/pnpm-global.txt`
  through the trusted `fnm`/Corepack path.

`scripts/doctor.py`:

- Keep current-process Codex/runtime `pnpm` as context only.
- Add strict JS policy after cleanup: Homebrew `node`, Homebrew `pnpm`,
  Homebrew `corepack`, and npm globals should fail unless declared as Managed
  Exceptions.
- Report `FNM_COREPACK_ENABLED` as actionable when the target state is accepted.
- Add explicit zsh, Codex, and AI command-surface parity checks before
  enforcing PATH strictness.

## Ordered Implementation Roadmap

### P0 Make Source Of Truth Accurate

1. Accept ADR-0007 as the specific owner decision for ADR-0005.
2. Update Brewfile intent: `fnm` yes, Homebrew `node` no, Homebrew `pnpm` no,
   Homebrew `corepack` no.
3. Update JS recipes to use `fnm exec --using default`.
4. Add or document the `fnm` Corepack enablement policy.
5. Keep `markdownlint-cli` in `system/packages/pnpm-global.txt` because
   markdownlint remains required validation tooling.
6. Keep Pi declared in `system/packages/pnpm-global.txt`; keep opencode CLI
   ownership out of npm globals through the upstream Homebrew tap.

### P1 Migrate Or Remove Duplicates

1. Confirm `node`, `npm`, `npx`, `corepack`, and `pnpm` resolve through the
   trusted `fnm` path in zsh and Codex-command contexts. Done.
2. Homebrew npm global `aws-cdk` removal is complete; the stale Homebrew-prefix
   `cdk` symlink and package copy were removed, and `cdk` resolves through the
   declared pnpm global path.
3. Homebrew `pnpm` removal is complete.
4. Homebrew `node` removal is complete.
5. Treat `npm` and `corepack` under the active fnm Node as runtime-owned
   packages, not user globals.
6. Keep Pi declared through pnpm unless a later policy changes it.

### P2 Docs And Doctor Strictness

1. Update README/setup docs to say Homebrew installs `fnm`; `fnm` owns Node.
2. Document `fnm` Node version retention and cleanup rules.
3. Document the Node 25+ Corepack caveat.
4. Add doctor strictness for forbidden JS owners after cleanup.
5. Add shell parity sections to doctor for Nu, zsh, and Codex.
6. Add a short troubleshooting note for current-process Codex runtime `pnpm`.

## Open Questions For Alex

1. Should Pi eventually receive APM-managed assets if APM gains a confirmed Pi
   target or adapter model?
2. Should Node 25+ experimentation stay installed after the retention policy is
   written?
