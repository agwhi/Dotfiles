# Freeze Accepted ADRs Against Reconstruction

Status: accepted.
Date: 2026-07-08.
Related: docs/adr/README.md, docs/adr/AGENTS.md, ADR-0001 through ADR-0011.

## Context

On 2026-07-07 all eleven existing ADRs were reconstructed in place to meet the
new ADR quality bar (commit e823381 and the follow-up reconciliation in
ea2c252): section structure was normalized, decision history was rewritten,
and dates were reset to the original decision date (2026-06-30) with a shared
"Amended: 2026-07-07. Reconstructed decision history and ADR quality
structure." note.

That reconstruction conflicts with the lifecycle rule in
`docs/adr/README.md` ("Do not silently rewrite old rationale after reality
changes"). A decision log only earns trust if records are stable: when past
records can be rewritten wholesale, readers cannot tell recorded rationale
from retrofitted rationale. The reconstruction is not being reverted — the
rewritten records are the best available statement of those decisions — but
the practice must not repeat.

## Decision Drivers

- ADRs are valuable precisely because they are immutable history, not living
  documents.
- The repo's own lifecycle rules forbid silent rewrites; policy and practice
  should agree.
- One-time cleanup to adopt a quality bar is understandable; recurring
  reconstruction erases the decision log's audit value.

## Considered Options

- Revert the 2026-07-07 reconstruction: rejected; the reconstructed records
  are clearer than the originals, and the originals remain available in git
  history.
- Allow periodic reconstruction as the quality bar evolves: rejected; it makes
  the log unauditable and violates the stated lifecycle rules.
- Accept the reconstruction as a one-time event and freeze accepted ADRs from
  now on: selected.

## Decision

The 2026-07-07 reconstruction of ADR-0001 through ADR-0011 is recorded as a
one-time quality-bar alignment. From this ADR forward, accepted ADRs are
frozen:

- Allowed edits to an accepted ADR: dated amendment notes, status changes
  (deprecated / superseded with links), and typo-level fixes that do not touch
  rationale.
- Everything else — changed decisions, changed rationale, restructured
  history — requires a new ADR that supersedes the old one, linked in both
  directions.
- Future quality-bar changes apply to new ADRs only; old records stay as
  written.

## Consequences

- The decision log becomes append-only and auditable from this point.
- Older ADRs may look inconsistent with future templates; that inconsistency
  is intentional and documents when each record was written.
- Anyone tempted to "clean up" an accepted ADR must write a superseding ADR
  instead, which is more work per change — the cost of a trustworthy log.
- Pre-reconstruction versions of ADR-0001 through ADR-0011 remain retrievable
  via git history (before commit e823381).
