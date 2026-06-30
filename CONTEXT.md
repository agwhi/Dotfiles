# Development Ecosystem

This context describes the personal development environment that should be reproducible on a new laptop and continuously kept current.

## Language

**Development Ecosystem**:
The complete set of tools, configurations, runtimes, editor integrations, AI tooling, and workflows that make up the user's laptop development environment.
_Avoid_: Dotfiles only, shell setup

**Living Source of Truth**:
The authoritative desired state for the Development Ecosystem; anything development-related is either managed here, intentionally referenced elsewhere, or intentionally excluded.
_Avoid_: Backup, notes, snapshot

**Orchestrator Repo**:
The repository that defines, installs, links, and verifies the complete Development Ecosystem, including any external repositories it depends on.
_Avoid_: Dotfiles repo, bootstrap script

**Companion Repo**:
A separately versioned repository for a specialized part of the Development Ecosystem that has its own lifecycle but is still installed and verified by the Orchestrator Repo.
_Avoid_: Manual dependency, external notes

**AI Package Source**:
A package source consumed by the AI Asset Manager, including public packages, marketplaces, Git repositories, local bundles, or the user's own AI Asset repositories.
_Avoid_: Special integration path, manual clone

**Canonical Installer**:
The chosen installation and update path for a tool or tool category within the Development Ecosystem.
_Avoid_: Whatever installed it first, manual install

**Managed Exception**:
A tool or workflow that is intentionally kept outside the normal Canonical Installer path but is still documented and verified by the Orchestrator Repo.
_Avoid_: Drift, manual one-off

**Replacement Candidate**:
A tool that may replace an existing part of the Development Ecosystem if it materially improves developer experience, reproducibility, or AI-native workflows.
_Avoid_: Shiny tool, random experiment

**Stabilization**:
The work of making the current Development Ecosystem reproducible, verified, and internally consistent without unnecessary tool churn.
_Avoid_: Rewrite, rebuild from scratch

**Stabilizing Replacement**:
A Replacement Candidate adopted during Stabilization because it reduces complexity now and is the likely long-term direction.
_Avoid_: Opportunistic migration, cleanup distraction

**Tool Fit**:
The degree to which a tool matches the user's actual Development Ecosystem needs, including depth of support, reliability, ergonomics, and integration quality.
_Avoid_: Popularity, breadth alone

**Specialized Tool**:
A tool focused on one category of work that may be preferable to a broader tool when its Tool Fit is stronger.
_Avoid_: Legacy tool, narrow tool

**Consolidating Tool**:
A broader tool that can replace multiple specialized tools when it improves Tool Fit and reduces operational complexity.
_Avoid_: Better by default, generic tool

**Tool-Choice ADR**:
An architectural decision record for a long-lived tool boundary or Canonical Installer decision that carries meaningful trade-offs.
_Avoid_: Package changelog, extension list

**AI Asset**:
A reusable skill, prompt, agent, template, rule, or workflow artifact used by AI-native development tools.
_Avoid_: Chat history, token, local cache

**AI Asset Manager**:
The Canonical Installer for AI Assets; it installs, updates, links, and verifies the AI Assets required by the Development Ecosystem.
_Avoid_: Manual copy, ad hoc clone

**AI Tool Surface**:
A specific AI-native tool environment that consumes AI Assets, such as Codex, Claude Code, Cursor, opencode, or Pi.
_Avoid_: Editor, CLI

**Shared AI Asset**:
An AI Asset authored once and adapted for multiple AI Tool Surfaces when their formats differ.
_Avoid_: Tool-specific copy, duplicated prompt

**Custom AI Asset**:
An AI Asset authored or maintained by the user.
_Avoid_: Third-party skill, marketplace package

**Third-Party AI Asset**:
An AI Asset sourced from an external author, marketplace, or package registry and installed through the Orchestrator Repo.
_Avoid_: Custom skill, vendored prompt

**Global AI Baseline**:
The small set of AI Assets intentionally installed across the Development Ecosystem for cross-project workflows.
_Avoid_: Everything useful, project-specific toolkit

**Baseline AI Asset**:
An AI Asset currently included in the Global AI Baseline.
_Avoid_: Installed skill, available package

**AI Workflow Rebuild**:
An intentional reset of user-managed AI tooling configuration and assets so the Global AI Baseline can be recreated cleanly from the Orchestrator Repo.
_Avoid_: Incremental cleanup, unmanaged pruning

**User-Managed AI State**:
AI tool configuration, assets, plugins, packages, and generated adapters that the user intentionally owns or installs outside the tool vendor's built-in system assets.
_Avoid_: Built-in assets, sensitive local state

**Reset Approval Gate**:
A required user confirmation before removing, moving, or replacing an existing tool, config tree, credential-adjacent file, history, cache, or AI asset during a rebuild.
_Avoid_: Blind cleanup, automatic deletion

**Rebuild Snapshot**:
An out-of-repository backup captured before a Reset Approval Gate changes or removes existing Development Ecosystem state.
_Avoid_: Repo backup directory, symlink copy

**Doctor Check**:
A read-only verification command that reports whether the laptop matches the Living Source of Truth and fails on actionable drift.
_Avoid_: Fix command, bootstrap

**Managed AI Config**:
Sensitive-safe AI tool configuration stored under the Orchestrator Repo and linked into AI Tool Surfaces.
_Avoid_: AI local state, auth config

**Package Manifest**:
A file that declares installable software, global packages, editor extensions, manual applications, or tool dependencies for the Development Ecosystem.
_Avoid_: App config, backup output

**Primary Shell**:
The shell optimized for daily interactive development in the Development Ecosystem.
_Avoid_: Default shell, bootstrap shell

**Compatibility Shell**:
A shell kept working for login scripts, external tools, editor terminals, or fallback workflows even when it is not the Primary Shell.
_Avoid_: Unsupported shell, accidental shell

**Shell Parity**:
The degree to which multiple supported shells expose the same PATH, aliases, environment variables, and developer commands.
_Avoid_: Duplicate config, copy-paste shell setup

**AI Shell Friction**:
The cost of using a shell whose syntax, plugins, or terminal behavior differs from what AI tools, generated commands, documentation, and package installers assume.
_Avoid_: Shell preference, AI annoyance

**Automation Shell**:
The shell contract used for bootstrap scripts, task runners, AI-executed commands, and generated instructions.
_Avoid_: Primary Shell, interactive shell

**Sensitive Local State**:
Secrets, auth tokens, credentials, local histories, databases, trusted-project lists, logs, and machine-specific identity files that must not be committed to git.
_Avoid_: Config, source of truth
