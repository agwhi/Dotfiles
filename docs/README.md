# Documentation

This directory explains how to understand, change, and audit the Development
Ecosystem managed by this Orchestrator Repo.

Use this map before changing tools, manifests, shell startup files, AI assets,
or local setup automation. The same fact should have one home; other docs should
link to that home instead of repeating it.

## Documentation Model

These docs follow the Diataxis model:

- Tutorials teach a complete workflow from beginning to end.
- How-to guides solve a specific task.
- Reference docs describe exact current state, commands, files, and contracts.
- Explanation docs describe why the system is shaped this way.

Not every category needs a folder on day one. Add a document when a real task
or reader need exists, not to fill the framework.

## Start Here

| Need | Start with | Type |
| --- | --- | --- |
| Bootstrap or use the repo | [`../README.md`](../README.md) | How-to |
| Understand the domain language | [`../CONTEXT.md`](../CONTEXT.md) | Explanation |
| Understand the architecture | [`architecture.md`](architecture.md) | Explanation |
| Audit local drift | [`how-to/audit-drift.md`](how-to/audit-drift.md) | How-to |
| Add or classify a tool | [`how-to/add-managed-tool.md`](how-to/add-managed-tool.md) | How-to |
| Secure public Wi-Fi use | [`how-to/secure-public-networks.md`](how-to/secure-public-networks.md) | How-to |
| Look up managed tools | [`reference/tools.md`](reference/tools.md) | Reference |
| Look up commands and aliases | [`reference/commands.md`](reference/commands.md) | Reference |
| Review durable decisions | [`adr/`](adr/) | Decision log |
| Review stabilization work | [`plans/`](plans/) | Plans |
| Review historical audit evidence | [`audit/`](audit/) | Audit reports |
| Review package ownership | [`../system/packages/README.md`](../system/packages/README.md) | Reference |
| Review AI asset policy | [`../system/ai/README.md`](../system/ai/README.md) | Reference |

## What Goes Where

Use `README.md` for the shortest useful bootstrap path and links to deeper
docs. Avoid turning it into the complete architecture or operations manual.

Use `CONTEXT.md` for the project glossary and ubiquitous language. Add a term
there when it is needed across docs, scripts, ADRs, or future agent work.

Use `docs/architecture.md` for the current system shape: scope, boundaries,
major building blocks, runtime flow, and cross-cutting rules.

Use `docs/how-to/` for task guides that can be followed step by step. A how-to
should state the task, prerequisites, commands, expected result, and rollback or
approval gates when relevant.

Use `docs/adr/` for durable decisions with meaningful trade-offs. Follow
`docs/adr/README.md` and `docs/adr/AGENTS.md` when creating or materially
editing ADRs.

Use `docs/plans/` for implementation plans, migrations, acceptance criteria,
and validation checklists. A plan can become historical after the work completes;
do not rewrite it into the current source of truth.

Use `docs/audit/` for dated audit reports and evidence snapshots. Audits can be
superseded by later work, so current policy should live in ADRs, package docs,
architecture docs, or manifests.

Use `system/packages/README.md` for package ownership rules and manifest
contracts. Keep exact installable package lists in the package manifests.

Use `system/ai/README.md` and the `system/ai/*/README.md` files for AI Tool
Surface and AI Asset Manager policy.

## Maintenance Rules

- Prefer linking over duplicating facts.
- Use exact dates for time-sensitive state.
- Treat `just doctor` output as current evidence, not historical policy.
- Do not commit Sensitive Local State, generated caches, histories, credentials,
  or runtime databases.
- Add an ADR when a change creates or reverses a durable ownership boundary.
- Add or update a how-to when a repeated task needs a safe operating path.
