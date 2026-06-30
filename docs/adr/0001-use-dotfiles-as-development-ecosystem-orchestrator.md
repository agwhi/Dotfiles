# Use Dotfiles as the Development Ecosystem Orchestrator

This repository is the living source of truth for the user's Development Ecosystem: a new laptop should be reproducible from this repo plus any Companion Repos it installs and verifies. We choose an Orchestrator Repo model rather than storing every artifact directly here, because specialized assets such as custom AI skills or templates may deserve their own lifecycle while still being pulled, linked, and checked from this repo.

## Consequences

Tool choices that establish or change a Canonical Installer, introduce a Managed Exception, or adopt a Stabilizing Replacement should be captured in ADRs when there is a real trade-off worth preserving.
