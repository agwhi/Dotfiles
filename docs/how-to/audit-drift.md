# Audit Local Drift

Use this guide when you want to know whether the laptop still matches the
Development Ecosystem source of truth.

The doctor is read-only. It reports local state, package provenance, and
actionable drift without installing, uninstalling, migrating, backing up,
starting services, stopping services, or rewriting files.

## Run The Default Audit

From the repo root:

```sh
just doctor
```

The default output is intentionally short. If there are no actionable findings,
the ecosystem is ready. If findings appear, treat them as triage input rather
than as automatic cleanup instructions.

## Show The Full Inventory

```sh
just doctor --all
```

Use the full inventory when you need to inspect canonical tools, managed
exceptions, unknown state, or drift that is not shown in the default concise
output.

## Produce Machine-Readable Evidence

```sh
just doctor --json
```

Use JSON output for agents, scripts, audit reports, and dated evidence. When
capturing evidence in docs, include the review date because local tool state can
change after every install or upgrade.

## Classify Each Finding

For each finding, choose exactly one path:

- Declare it in `system/packages/*` when it belongs in the Development Ecosystem
  baseline.
- Document a Managed Exception in `system/packages/manual-apps.md` when it is
  intentional but cannot use the normal installer.
- Mark it as personal local state when it should stay on this laptop but not in
  the development baseline.
- Queue cleanup in `system/packages/manual-apps.md` when it should be removed
  later behind a Reset Approval Gate.
- Investigate further in `docs/plans/` or a dated audit note when ownership,
  provenance, or safety is unclear.

Do not remove credential-adjacent, root-owned, generated, or tool-managed state
just because doctor reports it. Cleanup can require a Rebuild Snapshot and a
Reset Approval Gate.

## Check Current Policy Before Acting

Use these references before changing manifests or cleanup plans:

- `system/packages/README.md` for package ownership rules.
- `system/packages/Brewfile` for Homebrew formulae and casks.
- `system/packages/pnpm-global.txt` for global JavaScript tools.
- `system/packages/dotnet-tools.txt` for .NET global tools.
- `system/packages/manual-apps.md` for Managed Exceptions and cleanup
  candidates.
- `system/ai/README.md` for AI Tool Surface and AI Asset boundaries.
- `docs/adr/` for durable ownership decisions.

## Validate After A Change

After a manifest or docs-only classification change, run:

```sh
just doctor
git diff --check
```

If you changed markdown docs, also run markdown lint on the touched files:

```sh
./scripts/js_toolchain.sh markdownlint path/to/file.md
```

If doctor still reports findings, confirm whether they are expected follow-up
work or a sign that the change used the wrong ownership path.
