# Treat Custom AI Assets as Normal AI Package Sources

Custom AI Assets such as skills, prompts, agents, templates, and reusable workflow artifacts may live in separately versioned repositories, but they should be consumed through the same AI Asset Manager flow as Third-Party AI Assets. The Orchestrator Repo declares only the Global AI Baseline for the laptop, regardless of whether those assets come from public packages, marketplaces, Git repositories, local bundles, or the user's own repositories. Sensitive Local State such as tokens, histories, local databases, and machine-specific trust data stays out of git.

## Consequences

The AI Asset Manager is a separate tool choice: APM or a better replacement may be selected later, but the Orchestrator Repo must expose the chosen install and verification flow for the Global AI Baseline. Project-specific AI Assets belong in the project repos that need them.
