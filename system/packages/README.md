# Package Manifests

This directory declares installable software for the Development Ecosystem.
Keep manifests declarative and one-purpose; bootstrap and doctor logic should
consume these files rather than embedding desired package lists.

## JavaScript Toolchain

`system/packages/Brewfile` declares Homebrew as the installer for `fnm` only.
Per ADR-0007, `fnm` owns the Node runtime, and Corepack/pnpm should be reached
through the selected `fnm` default Node path. Global JavaScript tools belong in
`system/packages/pnpm-global.txt` and are installed by `just install-node-tools`.

## Read-only Doctor

Run `just doctor` from the repo root to audit installed tools against these
manifests without changing the machine. The doctor reports drift and install
provenance only; it does not install, uninstall, migrate, back up, start
services, or rewrite files.

Use `just doctor --json` when another agent or script needs structured output.
