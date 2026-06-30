# Use One .NET SDK Source

The Development Ecosystem should expose one canonical `.NET` SDK source across supported shells. Homebrew `dotnet@8` is the default stabilization candidate because it is already declared in the Orchestrator Repo and resolves correctly in Nushell, but the Microsoft pkg install must be evaluated for SDK/workload compatibility before removal.

## Consequences

Global `.NET` tools should be declared in a Package Manifest, and `doctor` should report the active `dotnet` path per supported shell before any SDK source is removed behind a Reset Approval Gate.
