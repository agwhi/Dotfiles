# Use Bruno And HTTPie For API Development

Postman is removed from the Development Ecosystem baseline. API development is
owned by:

- Bruno for GUI API exploration and collection workflows.
- HTTPie for command-line API requests.

## Context

API tooling should fit the same source-of-truth model as the rest of the
development setup. The preferred workflow is lightweight, scriptable where
possible, and friendly to repo-reviewed API collections.

Postman is a capable API platform, but it is not the preferred tool on this
laptop. Keeping it in the Brewfile causes unnecessary cask drift and upgrade
noise for a tool that should not be part of the baseline.

## Consequences

`system/packages/Brewfile` declares `httpie` and the Bruno cask. It does not
declare Postman.

If Postman appears locally again, treat it as personal/manual state or a
cleanup candidate unless a future ADR reverses this decision.

Project-owned API collections should prefer Bruno when a GUI client is needed.
Scripts, docs, and automation should prefer HTTPie where an explicit CLI
request is clearer than a GUI collection.
