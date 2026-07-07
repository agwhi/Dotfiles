# ADR Agent Instructions

Follow `docs/adr/README.md` before creating or substantially editing any ADR.

## Required Behavior

- Inspect related ADRs, plans, manifests, scripts, and current repo state before
  writing.
- Record one durable decision per ADR.
- Include status, exact date, context, decision drivers, considered options,
  decision, consequences, and related links.
- Include negative consequences and rejected alternatives when there is a real
  trade-off.
- Preserve accepted ADR history. Supersede materially changed decisions with a
  new ADR instead of rewriting the old rationale.
- Link supersession both ways when editing an older ADR is part of the task.

## Boundaries

- Keep ADRs focused on architecture-level policy and durable workflow contracts.
- Put implementation task lists in `docs/plans/` unless they are direct
  consequences or validation gates for the decision.
- Do not promote project-local ADR rules into global AI skills or the APM
  baseline without a separate ADR.
