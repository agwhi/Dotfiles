# Pi

Pi is a declared AI Tool Surface installed through the canonical fnm/pnpm
global path. It is not an intentional exclusion from this development
ecosystem.

Current local state:

- CLI package: `@earendil-works/pi-coding-agent`
- CLI version observed: `0.80.3`
- Binary observed: `/Users/alex/Library/pnpm/pi`
- Package manifest: `system/packages/pnpm-global.txt`
- Local state root: `~/.pi`

Declared Pi packages:

- `@earendil-works/pi-coding-agent`
- `@plannotator/pi-extension`
- `pi-lens`
- `pi-mcp-adapter`
- `pi-subagents`
- `pi-web-access`

Current command entry points observed:

- `pi`
- `pi-lens-mcp`
- `pi-mcp-adapter`
- `pi-subagents`

`@plannotator/pi-extension` and `pi-web-access` are declared package state but
do not expose top-level binaries in the current pnpm global install.

## Classification

Pi is a canonical AI Tool Surface when the declared pnpm packages are installed
and `pi` resolves through `/Users/alex/Library/pnpm`. Rebuilds should install
or refresh Pi through `just install-node-tools`, which consumes
`system/packages/pnpm-global.txt`.

The old `@mariozechner/pi-coding-agent` package is deprecated for this repo.
Do not reintroduce it; use `@earendil-works/pi-coding-agent`.

## Local State

`~/.pi` is Sensitive Local State. It can contain auth, local package state,
extensions, generated adapters, caches, and tool-managed files. Do not commit
or rewrite it without an explicit snapshot and approval.

Sensitive local paths include:

- `~/.pi/agent/auth.json`
- `~/.pi/agent/npm`
- `~/.pi/agent/extensions`

The `pi-subagents` command is an installer or refresher for the local subagent
extension, not a version probe. Do not use `pi-subagents --version` in doctor
or validation scripts.

## APM Policy

Pi-specific assets are not part of the shared APM baseline today because APM
does not have a confirmed Pi target in this repo. That does not make Pi
out-of-scope. If APM later supports a Pi target or adapter, promote shared
assets through an ADR and a target-write gate.
