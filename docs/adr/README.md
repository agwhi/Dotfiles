# Architecture Decision Records

This directory is the decision log for architecture-level choices in the
Development Ecosystem. ADRs explain why durable tool, runtime, source-of-truth,
and operating-model choices exist so future agents can change them deliberately
instead of rediscovering the same trade-offs.

This standard is based on the ADR guidance in
<https://github.com/architecture-decision-record/architecture-decision-record>
and the consistent Context / Decision / Status / Consequences practice in
<https://github.com/arachne-framework/architecture>.

## When To Write An ADR

Write an ADR when a decision has durable consequences for this repo, including:

- a Canonical Installer, runtime owner, AI Asset Manager, or package source
- a Managed Exception, Stabilizing Replacement, or approval-gated cleanup path
- a source-of-truth boundary between this repo, companion repos, and local state
- a cross-tool workflow contract that future agents or bootstrap scripts must
  preserve
- a reversal or supersession of an earlier ADR

Do not write an ADR for routine implementation details, temporary experiments,
small local cleanups, or choices already fully covered by an accepted ADR.

## Required Shape

Every new ADR must be one decision, not a bundle of loosely related changes.
Use this shape unless the decision is intentionally tiny and the omitted section
is explicitly not relevant.

```markdown
# Use Present-Tense Verb Phrase For The Decision

Status: proposed | accepted | rejected | deprecated | superseded by ADR-XXXX.
Date: YYYY-MM-DD.

Supersedes: ADR-XXXX when applicable.
Superseded by: ADR-XXXX when applicable.
Related: ADR-XXXX, docs/path.md, scripts/name.sh, manifests/path.txt.

## Context

What problem, constraint, or drift forced a decision now? Include repo-local
facts, relevant current state, and business or workflow priorities.

## Decision Drivers

- Driver that makes one option better or worse.
- Driver that future agents should preserve.

## Considered Options

- Option A: selected or rejected, with the reason.
- Option B: selected or rejected, with the reason.

## Decision

State the chosen option and the boundary it creates. Include what is in scope
and what remains a separate decision.

## Consequences

- Positive consequence.
- Negative consequence or trade-off.
- Follow-up work, validation, cleanup gates, or future ADRs required.
```

Add an `## Evidence` section when the decision depends on discovered local
state, external primary sources, current tool behavior, or dated observations.

## Lifecycle Rules

- Start uncertain decisions as `proposed`; mark decisions `accepted` only when
  the repo should treat them as active policy.
- Keep accepted ADRs historically honest. Do not silently rewrite old rationale
  after reality changes.
- Add dated amendment notes for small clarifications. Create a new ADR when a
  decision is replaced or materially invalidated.
- When superseding, link both directions: the new ADR names what it supersedes,
  and the old ADR status points to the replacement.
- Use exact dates for time-sensitive facts, tool versions, prices, support
  windows, or migration state.

Existing ADRs may predate this quality bar. New ADRs and substantial edits to
old ADRs should meet it.

## Naming

Use a zero-padded sequence number and a lowercase dash-separated slug:

```text
0011-use-example-tool-for-example-workflow.md
```

Prefer present-tense imperative or declarative verb phrases. The filename should
make the decision recognizable without opening the file.

## Review Checklist

Before committing an ADR, verify:

- The ADR records exactly one decision.
- Status and date are present.
- The context explains why the decision exists now.
- The decision drivers are explicit.
- Considered options include rejected alternatives when a real trade-off exists.
- Consequences include downsides, follow-ups, and cleanup or approval gates.
- Related ADRs and repo artifacts are linked.
- Supersession is explicit when prior decisions are replaced.
- The ADR is short enough to be read, but detailed enough to preserve the why.
