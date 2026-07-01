# opencode

opencode is currently present as a legacy npm-global AI Tool Surface, not as a
declared global baseline tool.

Current local state:

- Package: npm global `opencode-ai`
- Version observed: `1.16.2`
- Binary observed: `~/.local/share/fnm/aliases/default/bin/opencode`
- State root: `~/.local/share/opencode`
- Config root: `~/.config/opencode`

The current Codex process PATH did not expose `opencode` or `open-code`, but the
binary exists under the `fnm` default Node alias path.

## Classification

`opencode-ai` is a legacy managed exception and possible project-local tool. It
is not part of the Global AI Baseline.

`~/.local/share/opencode` and `~/.config/opencode` are Sensitive Local State.
They include account/auth files, local databases, logs, snapshots, storage, and
provider configuration. Do not commit them directly.

## Target Policy

If opencode remains in the ecosystem, it should consume Shared AI Assets from
APM-generated or APM-installed adapters. It should not own the source copy of
shared prompts or skills.

Later options:

- keep opencode as a documented project-local or manual-local tool
- declare opencode as a managed AI Tool Surface with APM adapters
- remove npm global `opencode-ai` behind a Reset Approval Gate

No option is implemented in this task.
