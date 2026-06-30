# Optimize Shell Choice for AI-Native Low-Friction Development

The shell strategy should be evaluated around AI-native development with low shell friction rather than preserving the current shell by default. Nushell may remain the Primary Shell if its structured-data workflow justifies the complexity, but automation and AI-executed commands should be POSIX-compatible unless a later Tool-Choice ADR deliberately chooses otherwise.

## Considered Options

- zsh as Primary Shell
- Nushell as Primary Shell with zsh/POSIX as Automation Shell
- both shells supported through generated shared environment configuration
- Nushell retained only as an optional structured-data tool
