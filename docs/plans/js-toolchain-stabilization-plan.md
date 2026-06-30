# JavaScript Toolchain Stabilization Plan

Date: 2026-07-01.

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

Treat `mise` as a credible future Consolidating Tool, not as the stabilization
choice for this task. Revisit it only if Alex decides to consolidate multiple
runtimes behind one manager, not just because `fnm` has cleanup debt.

## Evidence

Grounding from `just doctor --json` generated at
`2026-06-30T22:10:20.362360+00:00`, reviewed locally on 2026-07-01:

- `fnm` is declared in `system/packages/Brewfile`, installed through Homebrew,
  and visible at `/opt/homebrew/bin/fnm`.
- Doctor models `fnm exec --using default` as the trusted JS scope.
- `fnm default` is `v22.17.1`.
- Modeled `fnm` commands are available: `node` `v22.17.1`, `npm` `11.4.2`,
  `npx` `11.4.2`, `pnpm` `10.33.2`, and `corepack` `0.34.0`.
- Current-process `node`, `npm`, and `npx` resolve through Homebrew paths.
- Current-process `pnpm` resolves through Codex runtime and is context only.
- Homebrew `pnpm` `11.9.0` is present as another candidate.
- `corepack` is declared in the Brewfile but the Homebrew formula is absent.
- `FNM_COREPACK_ENABLED` is currently `false`.
- Trusted pnpm globals include all three declared packages plus two undeclared
  packages: `@mariozechner/pi-coding-agent` and `markdownlint-cli`.
- npm globals exist in both trusted scopes: `corepack`, `npm`, and
  `opencode-ai` under `primary_fnm_default`; `aws-cdk` and `npm` under
  Homebrew npm.
- No competing runtime manager signals were detected for `mise`, `asdf`,
  `nodenv`, `nvm`, `volta`, or related managers.

Repo grounding:

- ADR-0005 says the ecosystem should have one Node runtime owner and one global
  JS tool path.
- `system/nushell/config.nu` loads `fnm env --json`, prepends the
  `FNM_MULTISHELL_PATH` bin directory, and runs `fnm use --install-if-missing`
  on directory changes.
- `system/nushell/env.nu` sets `PNPM_HOME` to `~/Library/pnpm` and prepends it
  to PATH.
- `justfile` currently uses `corepack`, `pnpm`, and `fnm` directly from the
  current shell context.

External primary sources used:

- [fnm README](https://github.com/Schniz/fnm/blob/master/README.md)
- [Corepack README](https://github.com/nodejs/corepack#readme)
- [mise Node docs](https://mise.jdx.dev/lang/node.html)
- [mise activate docs](https://mise.jdx.dev/cli/activate.html)

## Decision Matrix

<!-- markdownlint-disable MD013 -->

| Option | Laptop reproducibility | Nushell support | POSIX/zsh/Codex friendliness | Project-local version files | Corepack/pnpm behavior | AI-agent ergonomics | Long-term maintenance risk | Migration cost | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Keep `fnm` | Strongest current fit: declared, installed, modeled by doctor, and already configured in repo Nu files. | Good enough in this repo through `fnm env --json`; official shell output lists bash/zsh/fish/powershell, so Nu support is repo-integrated rather than first-class shell output. | Good when commands use `fnm exec --using default`; current Codex/zsh PATH still needs parity work. | Strong: fnm supports `.node-version`, `.nvmrc`, and engines resolution; current Nu hook already runs `fnm use --install-if-missing`. | Good with the `fnm` default Node. Corepack is visible now, but `FNM_COREPACK_ENABLED=false` and Node 25+ needs a caveat. | Strong: explicit `fnm exec --using default` gives Codex a deterministic command prefix independent of runtime PATH. | Medium-low: specialized scope, few moving parts, but Corepack distribution changes after Node 24 must be watched. | Low: no runtime-manager migration; cleanup is mostly removing duplicates later. | Select. |
| Replace `fnm` with `mise` | Potentially strong if multiple runtimes move under one manager; currently no repo or doctor evidence needs that. | Strong: `mise activate` has an explicit `nu` shell type. | Strong: supports activation and shims across common shells, but would require new parity policy. | Strong but not free: `.nvmrc`, `.node-version`, and `devEngines` support require explicit enabling. | Strong potential: `node.corepack` can install Corepack shims after Node installs. | Good after migration, but agents would need new commands, shims, and docs. | Medium: broader surface area and more settings, useful if consolidation is wanted, extra complexity if only Node needs fixing. | High: replace installed/configured runtime manager, update docs, doctor, Nu, zsh, recipes, manifests, and cleanup old fnm state. | Do not choose for stabilization. Keep as future Stabilizing Replacement candidate. |
| Use Homebrew `node` only | Weak for a living laptop source of truth because it makes the Node version track Homebrew rather than project/runtime policy. | Simple PATH behavior, but no runtime-manager integration in Nu. | Simple in zsh/Codex, but only because it ignores project-local switching. | Weak: no native `.node-version` or `.nvmrc` switching. | Mixed: Homebrew `pnpm` is present, Homebrew `corepack` is absent, and local metadata says Homebrew `corepack` depends on Homebrew `node` and conflicts with `pnpm`. | Weak: current simplicity hides global version drift and encourages current-process assumptions. | Medium-high: Homebrew upgrades can change Node major versions outside project intent. | Medium: would need to discard ADR-0005's modeled direction and migrate fnm-owned state. | Reject. |
| Other specialized Node manager (`volta`, `nvm`, `nodenv`) | No current repo or doctor evidence supports introducing one. | Unknown to this repo; would require new shell work. | Variable; no candidate beats current `fnm` evidence. | Variable, but not enough to justify churn. | Variable; no stronger Corepack/pnpm story is proven here. | Worse initially: new agent commands and docs without local evidence. | Medium-high because it adds a new owner while solving the same class of problem. | High relative to benefit. | Do not pursue unless a specific blocker appears. |

<!-- markdownlint-enable MD013 -->

## Why `fnm` Wins For Alex

`fnm` is the best Tool Fit for the current Stabilization goal. It is already
declared, installed, configured in Nushell, and trusted by doctor. It is a
Specialized Tool, which is a feature here: the problem is not that Alex lacks a
generic runtime manager, it is that one existing Node manager has not been made
the only owner yet.

`mise` is a serious Consolidating Tool. Its official docs show Node management,
explicit `nu` activation, optional idiomatic Node version files, and
`node.corepack`. That makes it worth remembering, especially if Python, Ruby,
Go, Java, or more runtimes later need one shared manager. It does not make
`mise` the right stabilization step today because doctor found no competing
runtime-manager signals and `fnm` is already the modeled trusted path.

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
from Nushell, zsh, the Codex app, or an editor terminal.

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
Not a steady-state owner. It is a present undeclared cleanup candidate. Remove
later only behind a Reset Approval Gate and after confirming no Homebrew formula
dependency needs it.

Homebrew `pnpm`:
Not a steady-state owner. Remove from the Brewfile later if Corepack-managed
pnpm remains the target, then uninstall the formula only behind approval.

Homebrew `corepack`:
Not a steady-state owner. Remove from the Brewfile later. It is currently
declared but absent, and installing it would pull toward Homebrew `node`
ownership.

npm globals under `primary_fnm_default`:
Migration exceptions only. Current packages are `corepack`, `npm`, and
`opencode-ai`. Remove or migrate later behind approval. `opencode-ai` should
wait for the AI Tool Surface and AI Asset Manager decision.

npm globals under Homebrew npm:
Migration exceptions only. Current packages are `aws-cdk` and `npm`; `aws-cdk`
duplicates the declared pnpm global. Remove later behind approval after proving
`cdk` resolves through the trusted pnpm path.

pnpm global packages:
Keep `@biomejs/biome`, `aws-cdk`, and `cdk-dia` as declared globals for now.
Classify `markdownlint-cli` as likely source-of-truth drift because repo
validation uses markdownlint. Classify `@mariozechner/pi-coding-agent` as AI
tooling drift until AI policy decides whether Pi is baseline or local state.

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
- Do not remove Homebrew `node`, Homebrew `pnpm`, npm globals, pnpm globals, or
  `fnm` Node versions without a Reset Approval Gate.
- Do not treat Codex runtime `pnpm` as laptop state.

## Reset Approval Gate List

Destructive or state-moving actions that need explicit approval later:

- Uninstall Homebrew formula `node`.
- Uninstall Homebrew formula `pnpm`.
- Remove Homebrew npm global `aws-cdk`.
- Remove Homebrew npm global `npm`.
- Remove `primary_fnm_default` npm global `corepack`.
- Remove `primary_fnm_default` npm global `npm`.
- Remove or migrate `primary_fnm_default` npm global `opencode-ai`.
- Remove or migrate pnpm global `@mariozechner/pi-coding-agent`.
- Remove pnpm global `markdownlint-cli` if Alex decides it is not baseline.
- Remove old `fnm` Node versions after a retention policy is documented:
  `v20.10.0`, `v20.13.1`, `v20.18.1`, `v22.10.0`, `v22.14.0`, `v22.18.0`,
  `v24.14.1`, and `v25.9.0`.
- Replace `fnm` with `mise` if a future ADR chooses that Stabilizing
  Replacement.
- Rewrite shell PATH ownership for zsh/Nushell/Codex after shell parity checks.
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
- Add `markdownlint-cli` if markdown lint remains part of the baseline.
- Do not add `@mariozechner/pi-coding-agent` until AI tooling policy decides
  whether Pi is baseline, local state, or a Managed Exception.

`system/nushell/config.nu` and `system/nushell/env.nu`:

- Keep the `fnm env --json` approach unless a future shell ADR changes it.
- Add an explicit Corepack enablement policy for the `fnm` path.
- Verify whether `PNPM_HOME` should stay `~/Library/pnpm` for trusted `fnm`
  pnpm, and document why current-process Codex runtime `pnpm` is excluded.

`justfile`:

- Change JS recipes to use `fnm exec --using default` instead of whatever
  `corepack` or `pnpm` appears first in the current shell.
- Remove the suspicious POSIX recipe pattern that sources a Nushell env file.
- Make `install-node-tools` install from `system/packages/pnpm-global.txt`
  through the trusted `fnm`/Corepack path.

`scripts/doctor.py`:

- Keep current-process Codex/runtime `pnpm` as context only.
- Add strict JS policy after cleanup: Homebrew `node`, Homebrew `pnpm`,
  Homebrew `corepack`, and npm globals should fail unless declared as Managed
  Exceptions.
- Report `FNM_COREPACK_ENABLED` as actionable when the target state is accepted.
- Add explicit zsh, Nushell, and Codex parity checks before enforcing PATH
  strictness.

## Ordered Implementation Roadmap

### P0 Make Source Of Truth Accurate

1. Accept ADR-0007 as the specific owner decision for ADR-0005.
2. Update Brewfile intent: `fnm` yes, Homebrew `node` no, Homebrew `pnpm` no,
   Homebrew `corepack` no.
3. Update JS recipes to use `fnm exec --using default`.
4. Add or document the `fnm` Corepack enablement policy.
5. Add `markdownlint-cli` to `system/packages/pnpm-global.txt` if markdownlint
   remains required validation tooling.
6. Classify `@mariozechner/pi-coding-agent` and `opencode-ai` under the AI
   Tool Surface policy instead of generic JS globals.

### P1 Migrate Or Remove Duplicates

1. Confirm `node`, `npm`, `npx`, `corepack`, and `pnpm` resolve through the
   trusted `fnm` path in Nushell, zsh, and Codex-command contexts.
2. After approval, remove Homebrew npm global `aws-cdk` once `cdk` resolves
   through pnpm.
3. After approval, remove Homebrew `pnpm`.
4. After approval, remove Homebrew `node` if no dependency or Managed Exception
   requires it.
5. After approval, remove npm global `corepack` and rely on `fnm` Node
   Corepack for Node versions that provide it.
6. After approval, migrate or remove `opencode-ai` and Pi according to AI
   tooling policy.

### P2 Docs And Doctor Strictness

1. Update README/setup docs to say Homebrew installs `fnm`; `fnm` owns Node.
2. Document `fnm` Node version retention and cleanup rules.
3. Document the Node 25+ Corepack caveat.
4. Add doctor strictness for forbidden JS owners after cleanup.
5. Add shell parity sections to doctor for Nu, zsh, and Codex.
6. Add a short troubleshooting note for current-process Codex runtime `pnpm`.

## Open Questions For Alex

1. Should `markdownlint-cli` become a declared pnpm global?
2. Is Pi a baseline AI Tool Surface or personal local state?
3. Should Node 25+ experimentation stay installed after the retention policy is
   written?
4. Is there any Homebrew formula or workflow that intentionally requires
   Homebrew `node`?
