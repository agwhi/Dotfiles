# Use One Node Runtime and One Global JS Tool Path

The Development Ecosystem should have one canonical Node runtime owner and one canonical global JavaScript tool path. npm globals are prohibited except as temporary migration exceptions; global JavaScript tools should be declared through the Orchestrator Repo and installed through the chosen package manager path, with Corepack-managed pnpm as the default unless a later runtime-manager decision changes it.

## Consequences

Existing drift such as npm-global `aws-cdk`, Homebrew `node` competing with `fnm`, and mixed `cdk`/`cdk-dia` resolution must be cleaned up behind Reset Approval Gates.
