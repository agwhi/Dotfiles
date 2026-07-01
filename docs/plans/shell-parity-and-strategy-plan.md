# Shell Parity And Strategy Plan

Date: 2026-07-01.

This plan is non-mutating. It does not change shell startup files, switch the
Primary Shell, install tools, remove tools, relink files, or rewrite Nushell or
zsh configuration. It records current shell behavior and turns the shell
strategy into an implementation plan.

## Recommendation

Keep Nushell as Alex's Primary Shell for interactive work, including the
repo-managed VS Code, Cursor, and Ghostty terminal defaults.

Use POSIX-compatible automation as the stable command contract. `just`
bootstrap recipes, setup scripts, installer docs, and AI-generated commands
should not require Nushell syntax, Nushell aliases, or an interactive shell
startup path. Codex commands should target the zsh/Codex execution context, but
the command text should stay POSIX-compatible unless a task explicitly needs a
zsh feature.

Keep dual-shell support, but only as a bounded policy:

- Nushell is the ergonomic interactive shell.
- zsh is the macOS, login, Codex, and compatibility shell.
- POSIX `sh` is the recipe and script portability floor.
- Shared PATH and tool ownership should be generated or modeled from one source
  of truth instead of hand-maintained twice.

Confidence: high for the policy split, medium for the eventual implementation
shape. The evidence clearly rejects Nu-only automation, but the exact shared
environment generator still needs design.

## Evidence Summary

Grounding from `./scripts/doctor.py --json` generated at
`2026-07-01T12:06:10.584889+00:00`:

- Doctor now reports `shell_parity.contexts`.
- Safe default doctor probes cover Codex process, zsh non-login, plain
  `nu --commands`, and a synthetic `just` recipe shell.
- Login/startup probes for zsh login and `nu --login --commands` are opt-in via
  `DOTFILES_DOCTOR_ALLOW_STARTUP_PROBES=1` because they execute user startup
  files and may write caches or run hooks.
- The evidence captured for this plan included those opt-in startup probes.
- Safe default doctor currently reports 7 shell drift areas across 4 executable
  contexts.
- The opt-in full probe found 12 shell drift areas: `pnpm`, Corepack, `fnm`,
  `PNPM_HOME`, `.NET` global tools, `dotnet`, `mise`, AI CLI visibility,
  aliases, `just`, and editor terminal policy.
- VS Code, Cursor, and Ghostty repo-managed settings all choose `nu`.
- The repo `justfile` does not declare a shell, so recipes use the task runner
  default shell and inherit the caller environment.

Additional local probes on 2026-07-01:

- Live Nushell config paths are the repo files:
  `system/nushell/config.nu` and `system/nushell/env.nu`.
- `nu --login --commands` loads the repo config and exports `FNM_*`.
- Plain `nu --commands` does not behave like the configured login shell.
- zsh login probing emitted `(eval):1: can't change option: zle`, which means
  zsh startup is not clean in this non-interactive probe mode.
- `system/nushell/config.nu` currently creates a Starship autoload directory
  and writes a generated `starship.nu` file during startup, so Nu login probes
  must remain opt-in until startup side effects are removed.

## Context Evidence Table

<!-- markdownlint-disable MD013 -->

| Context | Node/npm | pnpm/Corepack | .NET | PATH/env | AI and local tools |
| --- | --- | --- | --- | --- | --- |
| Codex process | `node` and `npm` resolve through `/opt/homebrew/bin`. No `FNM_*`. | `pnpm` resolves through `/Users/alex/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pnpm`; `corepack` absent. | `dotnet` resolves through `/usr/local/share/dotnet/dotnet`; `DOTNET_ROOT` unset. | `PNPM_HOME=~/Library/pnpm`; PATH has literal `~/.dotnet/tools`, not expanded. | `codex` and `apm` visible; `claude`, `opencode`, `pi`, and .NET global tool commands are not directly visible. |
| zsh non-login | Same as Codex process for Node/npm and no `FNM_*`. | Same as Codex process: Codex runtime `pnpm`; `corepack` absent. | Same as Codex process: Microsoft pkg `dotnet`; `DOTNET_ROOT` unset. | Same literal `~/Library/pnpm` and `~/.dotnet/tools` entries. | Same visibility as Codex process. |
| zsh login | `node` and `npm` resolve through `/opt/homebrew/bin`; no `FNM_*`. | `pnpm` resolves through `/opt/homebrew/bin/pnpm`; `corepack` absent. | `dotnet` resolves through `/usr/local/share/dotnet/dotnet`; `DOTNET_ROOT` unset. | zsh reorders PATH but keeps literal `~/.dotnet/tools` and `~/Library/pnpm`. | `codex` and `apm` visible; Nu-only or expanded-path tools remain absent. |
| `nu --commands` | `node` and `npm` resolve through `/opt/homebrew/bin`; no `FNM_*`. | `pnpm` resolves through Codex runtime; `corepack` absent. | `dotnet` resolves through `/usr/local/share/dotnet/dotnet`; `.dotnet/tools` is expanded and commands are visible. | PATH conversions expand tilde entries, but `PNPM_HOME` remains `~/Library/pnpm`. | `pi` and .NET global tool commands become visible because Nu expands PATH. |
| `nu --login --commands` | `node` and `npm` resolve through `/Users/alex/.local/state/fnm_multishells/<id>/bin`; `FNM_DIR=/Users/alex/.local/share/fnm`; `FNM_COREPACK_ENABLED=false`. | `pnpm` and `corepack` resolve through the `fnm` multishell path. | `dotnet` resolves through `/opt/homebrew/opt/dotnet@8/bin/dotnet`; `DOTNET_ROOT` unset. | `PNPM_HOME=/Users/alex/Library/pnpm`; `.dotnet/tools` expanded; `mise` shims absent. | `claude`, `opencode`, `pi`, and .NET global tool commands are visible. |
| Synthetic `just` recipe | Same as Codex process for Node/npm and no `FNM_*`. | Same as Codex process: Codex runtime `pnpm`; `corepack` absent. | Same as Codex process: Microsoft pkg `dotnet`; `DOTNET_ROOT` unset. | Inherits caller PATH. The repo justfile has no explicit shell declaration. | Same visibility as Codex process. |
| Editor policy | Repo settings choose Nu, not live-probed here. | Editor terminals are expected to inherit Nu behavior once launched. | Editor SDK discovery still needs a live check before SDK cleanup. | `system/vscode/settings.jsonc`, `system/cursor/settings.jsonc`, and `system/ghostty/config` point at `/opt/homebrew/bin/nu`. | Editor terminals are Nu-first; Codex is zsh/current-process-first. |

<!-- markdownlint-enable MD013 -->

## Parity Gaps

<!-- markdownlint-disable MD013 -->

| Area | Finding | Impact | Recommendation |
| --- | --- | --- | --- |
| PATH | `PNPM_HOME` is literal `~/Library/pnpm` in Codex, zsh, and just, but expanded in Nu login. | Tools under `~/Library/pnpm` are not equally visible. `pi` appears in Nu contexts but not zsh/Codex/just. | Use an expanded shared PATH source and generate shell-specific fragments later. |
| fnm | `FNM_*` variables are exported only by `nu --login --commands`. | Plain `node`, `npm`, `pnpm`, and `corepack` do not mean the same thing across contexts. | Keep automation on `fnm exec --using default` or `scripts/js_toolchain.sh` until parity is strict. |
| pnpm | `pnpm` resolves to Codex runtime, Homebrew, or `fnm` depending on context. | Plain `pnpm` can inspect or mutate the wrong package scope. | Treat Codex runtime `pnpm` as context only; use the ADR-0007 trusted wrapper. |
| pnpm | `corepack` is visible only when the `fnm` multishell path is active. | Corepack commands fail in zsh/Codex/just unless wrapped. | Run Corepack through `scripts/js_toolchain.sh` or `fnm exec --using default`. |
| dotnet | `.dotnet/tools` is literal in zsh/Codex/just and expanded in Nu. | Installed .NET global tool commands are invisible from zsh/Codex/just. | Put expanded `/Users/alex/.dotnet/tools` in shared PATH later. |
| dotnet | `dotnet` resolves to Microsoft pkg in zsh/Codex/just/plain Nu, and Homebrew `dotnet@8` in Nu login. | Recipes and editors can use different SDK patch lines. | Do not remove any SDK source until ADR-0006 `mise` parity is proven. |
| mise | `mise` and `mise` shims are absent in every probed context. | The ADR-0006 target is not active yet. | Install and activate `mise` only in a later approved implementation step. |
| ai_tools | `claude`, `opencode`, `pi`, and some .NET global tool commands are visible only in Nu-derived contexts. | AI CLI examples can fail when Codex runs them in zsh/current-process context. | Declare intended AI Tool Surface CLI paths before enforcing parity. |
| aliases | `system/nushell/config.nu` defines 28 aliases; zsh startup files define no comparable repo-managed aliases. | Alias-based instructions work in Nu but fail in automation and Codex. | Do not use aliases in scripts, recipes, README setup steps, or Codex-generated commands. |
| just | The repo justfile has no `set shell`. | Recipes inherit environment drift from the caller and task runner defaults. | Treat just recipes as POSIX-compatible automation and make tool paths explicit. |
| editor_terminal | VS Code, Cursor, and Ghostty are configured for Nu. | Editor terminals and Codex do not share a shell by default. | Keep Nu editor terminals only if shared PATH ownership makes tools equivalent. |
| zsh | zsh login probe emitted `zle` option warnings. | Non-interactive zsh login is not clean enough to use as a silent automation contract. | Investigate later; do not require zsh login startup for recipes. |

<!-- markdownlint-enable MD013 -->

## Target Shell Model

Primary Shell:
Nushell remains the Primary Shell for Alex's interactive terminal, editor
terminal, structured data exploration, and shell-native daily ergonomics.

Compatibility Shell:
zsh remains supported because macOS, Codex, GUI launch paths, vendor docs, and
many installers assume zsh/POSIX semantics.

Automation Shell:
The automation contract is POSIX `sh`-compatible command text with explicit
tool wrappers. It should not depend on aliases, `FNM_*` already being exported,
Nushell PATH conversions, or zsh login startup behavior.

Codex command shell:
Codex-generated commands should target the zsh/Codex context by default, while
remaining POSIX-compatible unless a task explicitly needs zsh. For JavaScript
tooling, Codex should prefer:

```sh
./scripts/js_toolchain.sh node --version
./scripts/js_toolchain.sh corepack --version
./scripts/js_toolchain.sh pnpm --version
fnm exec --using default pnpm list -g --depth 0 --json
```

Editor terminals:
VS Code, Cursor, and Ghostty may continue launching Nu. They should be treated
as interactive user surfaces, not proof that automation can use Nu syntax.

## Shared PATH Ownership

The target is one shell-neutral environment source that can generate or verify
Nushell and zsh fragments. It should own:

- expanded paths, never literal tilde entries;
- `PNPM_HOME`;
- `FNM_DIR`, `FNM_MULTISHELL_PATH`, and Corepack policy;
- `.dotnet/tools`;
- future `DOTNET_ROOT` and `mise` shim paths;
- AI CLI path policy after AI Tool Surface ownership is declared.

Until that exists, the repo should prefer explicit wrappers:

- `scripts/js_toolchain.sh` for Node, npm, pnpm, and Corepack;
- future `.NET` wrapper or `mise exec` commands after ADR-0006 implementation;
- full command names instead of aliases;
- recipe-local environment setup instead of inherited interactive startup.

## Answers To The Strategy Questions

Should Nushell remain Alex's primary interactive shell?
Yes. The editor and terminal configuration already point at Nu, and Nu has the
richest interactive setup. The evidence does not support Nu-only automation.

Should zsh/POSIX be the automation and AI-command shell?
Yes. Use POSIX-compatible commands for automation and Codex. zsh is the
practical Codex/macOS shell context, but commands should avoid zsh-only syntax
unless explicitly needed.

Is dual-shell support worth the maintenance cost?
Yes, if bounded. It is worth supporting Nu for interactive work and
zsh/POSIX for automation. It is not worth maintaining two independent copies of
PATH, aliases, and runtime activation logic.

How should shared PATH/tool ownership be kept in sync?
Use one shell-neutral source of truth and generate or verify shell-specific
fragments. Do not keep hand-copied Nu and zsh PATH logic as the steady state.

Which shell context should just bootstrap assume?
POSIX `sh` semantics with no aliases and no interactive startup assumptions.
Recipes can run from Nu or zsh, but recipe bodies should be portable and use
explicit wrappers.

Which shell should Codex-generated commands target by default?
Target zsh/Codex execution with POSIX-compatible command text. Use explicit
toolchain wrappers where PATH drift is known.

What exact drift exists today?
The drift is captured in the context evidence table and the parity gaps above.
The highest-impact drift is `pnpm` source switching, `fnm` only activating in
Nu login, literal tilde PATH entries in zsh/Codex/just, mismatched `dotnet`
sources, and Nu-only aliases/tool visibility.

## Migration Plan

### P0 Record And Observe

Completed in this task:

1. Add `shell_parity.contexts` to doctor output.
2. Keep login/startup shell probes opt-in so default doctor remains
   non-mutating.
3. Record the target policy in ADR-0004.
4. Add this non-mutating shell parity plan.

### P1 Define Shared Environment Ownership

1. Choose the shell-neutral source format for PATH and tool environment.
2. Include expanded `PNPM_HOME`, `.dotnet/tools`, Homebrew paths, Codex context
   exclusions, and future `mise` paths.
3. Generate or validate Nu and zsh fragments from that source.
4. Keep aliases out of the automation contract.

### P2 Normalize Automation

1. Make `just` shell assumptions explicit if needed.
2. Keep JS recipes on `scripts/js_toolchain.sh`.
3. Use POSIX-compatible recipes for bootstrap and setup.
4. Add a future `.NET` wrapper or `mise exec` contract after `mise` is active.

### P3 Align Interactive Shells

1. Update Nu and zsh startup files only after approval.
2. Remove literal tilde PATH entries.
3. Ensure `fnm` activation, `PNPM_HOME`, `.dotnet/tools`, and AI CLI paths are
   equivalent where the policy says they should be.
4. Investigate the zsh login `zle` warning.
5. Consider moving Nu startup cache generation out of routine startup if doctor
   parity probes must remain strictly side-effect-free.

### P4 Prove Editor And Codex Parity

1. Run the doctor from Nu, zsh, Codex, VS Code terminal, and Cursor terminal.
   Use `DOTFILES_DOCTOR_ALLOW_STARTUP_PROBES=1` only when the task explicitly
   accepts startup hook execution.
2. Verify `node`, `npm`, `pnpm`, `corepack`, `dotnet`, and AI CLI commands.
3. Only then make strict doctor failures for forbidden owners or missing paths.

## What Not To Do

- Do not switch the Primary Shell in this task.
- Do not make Nu the automation language.
- Do not rely on zsh login startup for recipes.
- Do not use aliases in generated instructions or recipes.
- Do not remove Homebrew `node`, Homebrew `pnpm`, Microsoft pkg `.NET`,
  Homebrew `dotnet@8`, npm globals, pnpm globals, or AI CLI state as part of
  shell strategy work.
- Do not activate `mise` for `.NET` until its own implementation step.

## Followups

1. Design the shell-neutral environment source and generator.
2. Decide whether `justfile` should explicitly set `shell := ["sh", "-cu"]`.
3. Update Cursor rules that still say to avoid bash/zsh once ADR-0004 is
   accepted.
4. Run live checks from VS Code and Cursor integrated terminals.
5. Decide which AI CLI paths are baseline, managed exceptions, or local state.
