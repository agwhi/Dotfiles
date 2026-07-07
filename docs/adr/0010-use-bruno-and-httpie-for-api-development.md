# Use Bruno And HTTPie For API Development

Status: accepted.
Date: 2026-07-07.
Related: ADR-0001, system/packages/Brewfile,
docs/plans/homebrew-provenance-stabilization-plan.md, scripts/doctor.py.

## Context

API tooling is part of the Development Ecosystem baseline because it affects
local development, project debugging, and repeatable API exploration. Postman
was installed and later declared, but Alex prefers HTTPie and Bruno.

The repo should not keep Postman in the Brewfile merely because it was already
installed. Keeping an unused API client creates cask upgrade noise and weakens
the source-of-truth model.

## Decision Drivers

- API collections should be friendly to source control and project review.
- Command-line API examples should be easy to paste into docs, scripts, and AI
  prompts.
- The GUI API client should be optional workflow tooling, not a hosted platform
  dependency.
- The Brewfile should avoid tools Alex does not intend to use.
- Doctor should recognize Bruno and HTTPie as development-related tools if
  they drift later.

## Considered Options

- Keep Postman: rejected because it is no longer the preferred workflow and
  created unnecessary cask maintenance.
- Use Insomnia: rejected because there was no current user preference or repo
  evidence showing it should replace Bruno.
- Use only `curl`: rejected because it is always available but less ergonomic
  for daily API exploration than HTTPie and does not provide a GUI collection
  workflow.
- Use only Bruno: rejected because CLI-first examples and automation still need
  a clear command-line API client.
- Use Bruno plus HTTPie: selected because it covers GUI collections and
  scriptable terminal requests.

## Decision

Postman is removed from the Development Ecosystem baseline.

API development is owned by:

- Bruno for GUI API exploration and collection workflows.
- HTTPie for command-line API requests.

`system/packages/Brewfile` declares `httpie` and the Bruno cask. It does not
declare Postman.

## Consequences

- Postman appearing locally again is personal/manual state or a cleanup
  candidate unless a future ADR reverses this decision.
- Project-owned API collections should prefer Bruno when a GUI client is
  needed.
- Scripts, docs, and automation should prefer HTTPie where an explicit CLI
  request is clearer than a GUI collection.
- The downside is that Postman-specific team collections or environments would
  need import/migration before they fit the baseline.
