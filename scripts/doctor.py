#!/usr/bin/env python3
"""Read-only Development Ecosystem doctor for this Orchestrator Repo."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - older system Python fallback
    tomllib = None  # type: ignore[assignment]

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional local dependency
    yaml = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

BREWFILE = ROOT / "system/packages/Brewfile"
PERSONAL_BREWFILE = ROOT / "system/packages/personal.Brewfile"
VSCODE_EXTENSIONS = ROOT / "system/packages/vscode-extensions.txt"
PNPM_GLOBAL = ROOT / "system/packages/pnpm-global.txt"
DOTNET_TOOLS = ROOT / "system/packages/dotnet-tools.txt"
MANUAL_APPS = ROOT / "system/packages/manual-apps.md"
APM_MANIFEST = ROOT / "system/ai/apm/apm.yml"
APM_LOCKFILE = ROOT / "system/ai/apm/apm.lock.yaml"
APM_USER_MANIFEST = HOME / ".apm/apm.yml"
APM_USER_LOCKFILE = HOME / ".apm/apm.lock.yaml"
CODEX_SKILLS_DIR = HOME / ".codex/skills"
CLAUDE_SKILLS_DIR = HOME / ".claude/skills"
OPENCODE_SKILLS_DIR = HOME / ".config/opencode/skills"
CLAUDE_COMMAND = HOME / ".local/bin/claude"
CLAUDE_VERSIONS_DIR = HOME / ".local/share/claude/versions"
CLAUDE_DESKTOP_APP = Path("/Applications/Claude.app")
DEV_ENV = ROOT / "scripts/dev_env.sh"
MISE_CONFIG = ROOT / "system/mise/config.toml"
MISE_USER_CONFIG = HOME / ".config/mise/config.toml"
MISE_SHIMS = HOME / ".local/share/mise/shims"
MISE_DOTNET_ROOT = HOME / ".local/share/mise/dotnet-root"
ZSH_ENV = ROOT / "system/zsh/.zshenv"
ZSH_PROFILE = ROOT / "system/zsh/.zprofile"
ZSH_RC = ROOT / "system/zsh/.zshrc"
DOTNET_POLICY_SDK_LINES = ["10", "8"]
DOTNET_READ_ONLY_ENV = {
    **os.environ,
    "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
    "DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE": "1",
    "DOTNET_NOLOGO": "1",
    "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
    "MISE_AUTO_INSTALL": "0",
    "MISE_PREFER_OFFLINE": "1",
}

AREA_ORDER = [
    "brew",
    "js_toolchain",
    "vscode",
    "pnpm",
    "npm",
    "fnm",
    "runtime_managers",
    "shell_parity",
    "dotnet",
    "ai_tools",
    "manual_apps",
    "other",
]

ACTIONABLE_CLASSIFICATIONS = {
    "approval_gated_removal",
    "declared_absent",
    "drift",
    "duplicate",
    "legacy",
    "manual",
    "migration_pending",
    "missing",
    "present_undeclared",
}
ACTIONABLE_SEVERITIES = {"medium", "high"}

SHELL_NAMES = {"bash", "fish", "sh", "zsh"}
JS_COMMANDS = ["node", "npm", "npx", "pnpm", "corepack"]
NPM_RUNTIME_GLOBALS = {"corepack", "npm"}

DEV_RE = re.compile(
    r"(ai|apm|ast-grep|aws|azure|bash|biome|bun|cargo|cdk|clang|claude|"
    r"bruno|cmake|codex|colima|composer|ctags|cursor|deno|docker|dotenv|dotnet|"
    r"editorconfig|eslint|fd|ffmpeg|fnm|gcloud|gh|git|gitleaks|go|gradle|"
    r"graphviz|helm|httpie|jenv|jq|just|kotlin|kubectl|kubernetes|lambda|llm|lua|"
    r"mise|mysql|node|npm|nu|nushell|nvm|ollama|opencode|pnpm|podman|"
    r"poppler|postman|pycharm|pyenv|python|rbenv|redis|ripgrep|ripsecrets|"
    r"ruby|rust|rustup|sdkman|semgrep|serverless|shell|terraform|tmux|"
    r"typescript|unbound|uv|vim|volta|vscode|watchman|xcode|yarn|zsh)"
)

DEV_APP_RE = re.compile(
    r"(android studio|bruno|chatgpt atlas|codex|cursor|datagrip|docker|ghostty|"
    r"intellij|iterm|leapp|postman|pycharm|rider|session manager plugin|"
    r"sublime|tableplus|visual studio code|warp|webstorm|xcode)",
    re.IGNORECASE,
)

AI_COMMANDS = ["codex", "claude", "opencode", "open-code", "pi", "apm"]
CODEX_BASELINE_SKILLS = ["grill-with-docs", "grilling", "domain-modeling"]
CODEX_SPLIT_BASELINE_FILES = [
    "grill-with-docs/SKILL.md",
    "grilling/SKILL.md",
    "domain-modeling/SKILL.md",
    "domain-modeling/ADR-FORMAT.md",
    "domain-modeling/CONTEXT-FORMAT.md",
]
CODEX_STALE_BASELINE_FILES = [
    "grill-with-docs/ADR-FORMAT.md",
    "grill-with-docs/CONTEXT-FORMAT.md",
]
CODEX_ALLOWED_VENDOR_RUNTIME_SKILLS = [".system", "codex-primary-runtime"]
EXCLUDED_AI_ASSETS = {"using-superpowers"}
APM_BASELINE_TARGETS = ["codex", "claude", "opencode"]
PI_PNPM_PACKAGES = [
    "@earendil-works/pi-coding-agent",
    "@plannotator/pi-extension",
    "pi-lens",
    "pi-mcp-adapter",
    "pi-subagents",
    "pi-web-access",
]
PI_EXPECTED_COMMANDS = ["pi", "pi-lens-mcp", "pi-mcp-adapter", "pi-subagents"]
GRILL_WITH_DOCS_REF = "mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1"
GRILL_WITH_DOCS_APM_REFS = [
    "mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1",
    "mattpocock/skills/skills/productivity/grilling#v1.0.1",
    "mattpocock/skills/skills/engineering/domain-modeling#v1.0.1",
]
GRILL_WITH_DOCS_VIRTUAL_PATHS = [
    "skills/engineering/grill-with-docs",
    "skills/productivity/grilling",
    "skills/engineering/domain-modeling",
]
GRILL_WITH_DOCS_COMMIT = "2454c95dc305c158b21a0cdafeb728879dd0359a"
GRILL_WITH_DOCS_RESOLVED_REF = "v1.0.1"
GRILL_WITH_DOCS_REPO_URL = "mattpocock/skills"
GRILL_WITH_DOCS_HOST = "github.com"
SHELL_PARITY_COMMANDS = [
    "node",
    "npm",
    "pnpm",
    "corepack",
    "fnm",
    "mise",
    "dotnet",
    "codex",
    "claude",
    "opencode",
    "open-code",
    "pi",
    "apm",
    "just",
    "zsh",
    "dotnet-lambda-test-tool-8.0",
    "dotnet-ef",
]
DEV_ENV_EXPECTED_COMMANDS = [
    "node",
    "npm",
    "pnpm",
    "corepack",
    "dotnet",
    "dotnet-lambda-test-tool-8.0",
    "codex",
    "claude",
    "opencode",
    "pi",
    "apm",
    "just",
]
SHELL_PARITY_ENV_KEYS = [
    "SHELL",
    "PATH",
    "PNPM_HOME",
    "FNM_DIR",
    "FNM_MULTISHELL_PATH",
    "FNM_VERSION_FILE_STRATEGY",
    "FNM_LOGLEVEL",
    "FNM_COREPACK_ENABLED",
    "FNM_ARCH",
    "DOTNET_ROOT",
    "MISE_SHELL",
    "MISE_DATA_DIR",
    "MISE_CONFIG_DIR",
]
SHELL_PROBE_ENV_KEY = "DOTFILES_DOCTOR_SHELL_PROBE"
SHELL_PROBE_ALLOW_STARTUP_KEY = "DOTFILES_DOCTOR_ALLOW_STARTUP_PROBES"
SHELL_PROBE_START = "__DOTFILES_DOCTOR_SHELL_PROBE_START__"
SHELL_PROBE_END = "__DOTFILES_DOCTOR_SHELL_PROBE_END__"
RUNTIME_MANAGERS = {
    "nvm": {
        "commands": ["nvm"],
        "paths": [HOME / ".nvm"],
        "classification": "legacy",
    },
    "volta": {
        "commands": ["volta"],
        "paths": [HOME / ".volta"],
        "classification": "legacy",
    },
    "asdf": {
        "commands": ["asdf"],
        "paths": [HOME / ".asdf"],
        "classification": "legacy",
    },
    "mise": {
        "commands": ["mise"],
        "paths": [HOME / ".local/share/mise", HOME / ".config/mise"],
        "classification": "canonical",
    },
    "pyenv": {
        "commands": ["pyenv"],
        "paths": [HOME / ".pyenv"],
        "classification": "unknown",
    },
    "rbenv": {
        "commands": ["rbenv"],
        "paths": [HOME / ".rbenv"],
        "classification": "unknown",
    },
    "jenv": {
        "commands": ["jenv"],
        "paths": [HOME / ".jenv"],
        "classification": "unknown",
    },
    "sdkman": {
        "commands": ["sdk"],
        "paths": [HOME / ".sdkman"],
        "classification": "unknown",
    },
    "rustup": {
        "commands": ["rustup"],
        "paths": [HOME / ".rustup", HOME / ".cargo"],
        "classification": "unknown",
    },
    "goenv": {
        "commands": ["goenv"],
        "paths": [HOME / ".goenv"],
        "classification": "unknown",
    },
    "nodenv": {
        "commands": ["nodenv"],
        "paths": [HOME / ".nodenv"],
        "classification": "legacy",
    },
}


def command_result(
    args: list[str],
    timeout: int = 12,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            args,
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return {
            "ok": False,
            "returncode": 127,
            "stdout": "",
            "stderr": f"{args[0]} not found",
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"Timed out after {timeout}s",
            "timed_out": True,
        }

    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "timed_out": False,
    }


def lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def short_brew_name(name: str) -> str:
    return name.rsplit("/", 1)[-1]


def clean_manifest_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    result: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            line = line.split("#", 1)[0].strip()
        if line:
            result.append(line)
    return result


def yaml_parser_mode() -> str:
    return "pyyaml" if yaml is not None else "conservative_text"


def yaml_parser_notes() -> list[str]:
    if yaml is not None:
        return ["Parsed with PyYAML safe_load."]
    return [
        "PyYAML is unavailable; parsed only simple top-level YAML blocks.",
        "Full-line comments and blank lines are ignored; APM #version suffixes are treated as scalar text.",
        "Canonical status requires exact parsed targets, dependencies.apm refs, lockfile virtual paths, refs, and commits.",
    ]


def load_yaml_with_optional_pyyaml(path: Path) -> tuple[Any | None, list[str]]:
    if yaml is None:
        return None, []
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}, []
    except OSError as exc:
        return None, [f"{type(exc).__name__}: {exc}"]
    except Exception as exc:
        return None, [f"{type(exc).__name__}: {exc}"]


def simple_yaml_content_lines(text: str) -> list[str]:
    return [
        raw.rstrip()
        for raw in text.splitlines()
        if raw.strip() and not raw.lstrip().startswith("#")
    ]


def normalize_simple_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def extract_top_level_yaml_block(
    lines_: list[str],
    key: str,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    start: int | None = None
    key_pattern = re.compile(rf"^{re.escape(key)}:\s*$")
    inline_pattern = re.compile(rf"^{re.escape(key)}:\s+.+$")
    for index, line in enumerate(lines_):
        if key_pattern.match(line):
            start = index + 1
            break
        if inline_pattern.match(line):
            errors.append(f"unsupported inline top-level {key} value")
            return [], errors

    if start is None:
        errors.append(f"missing top-level {key} block")
        return [], errors

    block: list[str] = []
    top_level_key = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)$")
    for line in lines_[start:]:
        if top_level_key.match(line):
            break
        block.append(line)
    return block, errors


def duplicate_values(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def missing_expected_values(values: list[str], expected: list[str]) -> list[str]:
    present = Counter(values)
    return sorted(value for value in expected if present[value] == 0)


def unexpected_values(values: list[str], expected: list[str]) -> list[str]:
    expected_set = set(expected)
    return sorted(value for value in set(values) if value not in expected_set)


def values_match_exactly(values: list[str], expected: list[str]) -> bool:
    return Counter(values) == Counter(expected)


def normalize_yaml_string_list(value: Any, field: str) -> tuple[list[str], list[str]]:
    if value is None:
        return [], [f"missing {field}"]
    if not isinstance(value, list):
        return [], [f"{field} is not a list"]

    result: list[str] = []
    errors: list[str] = []
    for item in value:
        if isinstance(item, str):
            result.append(item)
        else:
            errors.append(f"{field} contains non-string item")
    return result, errors


def parse_manifest_with_text_fallback(
    text: str,
) -> tuple[list[str], list[str], list[str], list[str]]:
    parser_errors: list[str] = []
    content_lines = simple_yaml_content_lines(text)

    target_block, errors = extract_top_level_yaml_block(content_lines, "targets")
    parser_errors.extend(errors)
    targets: list[str] = []
    for line in target_block:
        stripped = line.strip()
        match = re.match(r"^-\s+(.+?)\s*$", stripped)
        if match:
            targets.append(normalize_simple_yaml_scalar(match.group(1)))
        else:
            parser_errors.append(f"unsupported targets line: {stripped}")

    dependencies_block, errors = extract_top_level_yaml_block(content_lines, "dependencies")
    parser_errors.extend(errors)
    dependency_sections: list[str] = []
    apm_refs: list[str] = []
    current_section: str | None = None
    current_section_indent: int | None = None

    for line in dependencies_block:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        section_match = re.match(r"^([A-Za-z0-9_-]+):\s*$", stripped)
        if section_match and indent > 0 and (
            current_section_indent is None or indent <= current_section_indent
        ):
            current_section = section_match.group(1)
            current_section_indent = indent
            dependency_sections.append(current_section)
            continue

        if current_section == "apm" and current_section_indent is not None:
            item_match = re.match(r"^-\s+(.+?)\s*$", stripped)
            if indent > current_section_indent and item_match:
                apm_refs.append(normalize_simple_yaml_scalar(item_match.group(1)))
                continue

        parser_errors.append(f"unsupported dependencies line: {stripped}")

    if dependencies_block and "apm" not in dependency_sections:
        parser_errors.append("missing dependencies.apm block")

    return targets, dependency_sections, apm_refs, parser_errors


def parse_manifest_values(path: Path, text: str) -> dict[str, Any]:
    parser_errors: list[str] = []
    if yaml is not None:
        data, errors = load_yaml_with_optional_pyyaml(path)
        parser_errors.extend(errors)
        targets: list[str] = []
        dependency_sections: list[str] = []
        apm_refs: list[str] = []
        if not parser_errors:
            if not isinstance(data, dict):
                parser_errors.append("manifest root is not a mapping")
            else:
                targets, errors = normalize_yaml_string_list(data.get("targets"), "targets")
                parser_errors.extend(errors)
                dependencies = data.get("dependencies")
                if not isinstance(dependencies, dict):
                    parser_errors.append("dependencies is not a mapping")
                else:
                    dependency_sections = sorted(str(key) for key in dependencies.keys())
                    refs, errors = normalize_yaml_string_list(
                        dependencies.get("apm"), "dependencies.apm"
                    )
                    apm_refs = refs
                    parser_errors.extend(errors)
        return {
            "targets": targets,
            "dependency_sections": dependency_sections,
            "apm_refs": apm_refs,
            "parser_errors": parser_errors,
        }

    targets, dependency_sections, apm_refs, parser_errors = parse_manifest_with_text_fallback(text)
    return {
        "targets": targets,
        "dependency_sections": sorted(dependency_sections),
        "apm_refs": apm_refs,
        "parser_errors": parser_errors,
    }


def parse_lockfile_dependencies_with_text_fallback(
    text: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    parser_errors: list[str] = []
    content_lines = simple_yaml_content_lines(text)
    dependencies_block, errors = extract_top_level_yaml_block(content_lines, "dependencies")
    parser_errors.extend(errors)
    dependencies: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for line in dependencies_block:
        stripped = line.strip()
        item_match = re.match(r"^-\s*([^:\s][^:]*):\s*(.*?)\s*$", stripped)
        if item_match:
            current = {
                item_match.group(1).strip(): normalize_simple_yaml_scalar(
                    item_match.group(2)
                )
            }
            dependencies.append(current)
            continue

        field_match = re.match(r"^\s+([^:\s][^:]*):\s*(.*?)\s*$", line)
        if current is not None and field_match:
            current[field_match.group(1).strip()] = normalize_simple_yaml_scalar(
                field_match.group(2)
            )
            continue

        parser_errors.append(f"unsupported dependencies line: {stripped}")

    return dependencies, parser_errors


def parse_lockfile_dependencies(path: Path, text: str) -> tuple[list[dict[str, Any]], list[str]]:
    parser_errors: list[str] = []
    if yaml is not None:
        data, errors = load_yaml_with_optional_pyyaml(path)
        parser_errors.extend(errors)
        if parser_errors:
            return [], parser_errors
        if not isinstance(data, dict):
            return [], ["lockfile root is not a mapping"]
        dependencies = data.get("dependencies")
        if not isinstance(dependencies, list):
            return [], ["dependencies is not a list"]
        result: list[dict[str, Any]] = []
        for item in dependencies:
            if isinstance(item, dict):
                result.append({str(key): value for key, value in item.items()})
            else:
                parser_errors.append("dependencies contains non-mapping item")
        return result, parser_errors

    return parse_lockfile_dependencies_with_text_fallback(text)


def yamlish_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def load_toml(path: Path) -> dict[str, Any]:
    if not path.exists() or tomllib is None:
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def normalize_mise_tool_versions(value: Any) -> list[str]:
    versions: list[str] = []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                versions.append(item)
            elif isinstance(item, dict) and isinstance(item.get("version"), str):
                versions.append(item["version"])
    elif isinstance(value, dict) and isinstance(value.get("version"), str):
        versions.append(value["version"])
    return versions


def parse_mise_dotnet_versions_from_text(text: str) -> list[str]:
    match = re.search(r"(?ms)^\[tools\]\s*(.*?)(?:^\[|\Z)", text)
    if not match:
        return []
    dotnet_match = re.search(r"(?m)^\s*dotnet\s*=\s*(.+?)\s*$", match.group(1))
    if not dotnet_match:
        return []
    raw_value = dotnet_match.group(1)
    return [
        left or right
        for left, right in re.findall(r'"([^"]+)"|\'([^\']+)\'', raw_value)
        if left or right
    ]


def mise_config_state() -> dict[str, Any]:
    text = MISE_CONFIG.read_text(encoding="utf-8") if MISE_CONFIG.exists() else ""
    data = load_toml(MISE_CONFIG)
    tools = data.get("tools") if isinstance(data.get("tools"), dict) else {}
    settings = data.get("settings") if isinstance(data.get("settings"), dict) else {}
    dotnet_settings = (
        settings.get("dotnet")
        if isinstance(settings.get("dotnet"), dict)
        else {}
    )
    versions = normalize_mise_tool_versions(tools.get("dotnet")) if tools else []
    if not versions and text:
        versions = parse_mise_dotnet_versions_from_text(text)

    user_config: dict[str, Any] = {
        "path": str(MISE_USER_CONFIG),
        "exists": MISE_USER_CONFIG.exists(),
        "is_symlink": MISE_USER_CONFIG.is_symlink(),
    }
    if MISE_USER_CONFIG.is_symlink():
        try:
            user_config["link_target"] = os.readlink(MISE_USER_CONFIG)
            user_config["resolved_path"] = str(MISE_USER_CONFIG.resolve())
            user_config["points_to_repo_config"] = (
                MISE_USER_CONFIG.resolve() == MISE_CONFIG.resolve()
            )
        except OSError:
            user_config["points_to_repo_config"] = False

    expected_present = all(line in versions for line in DOTNET_POLICY_SDK_LINES)
    return {
        "path": str(MISE_CONFIG),
        "source": str(MISE_CONFIG.relative_to(ROOT)),
        "exists": MISE_CONFIG.exists(),
        "dotnet_versions": versions,
        "expected_dotnet_versions": DOTNET_POLICY_SDK_LINES,
        "expected_versions_declared": expected_present,
        "declares_node": "node" in tools if tools else bool(re.search(r"(?m)^\s*node\s*=", text)),
        "settings": {
            "idiomatic_version_file_enable_tools": (
                settings.get("idiomatic_version_file_enable_tools")
                if isinstance(settings, dict)
                else None
            ),
            "dotnet": dotnet_settings,
        },
        "user_config": user_config,
        "expected_paths": {
            "user_config": str(MISE_USER_CONFIG),
            "shims": str(MISE_SHIMS),
            "dotnet_root": str(MISE_DOTNET_ROOT),
        },
    }


def mise_config_declares_dotnet_policy() -> bool:
    state = mise_config_state()
    return bool(state["exists"] and state["expected_versions_declared"] and not state["declares_node"])


def parse_brewfile(path: Path) -> dict[str, set[str]]:
    parsed: dict[str, set[str]] = {"brew": set(), "cask": set(), "vscode": set()}
    if not path.exists():
        return parsed

    pattern = re.compile(r'^\s*(brew|cask|vscode)\s+"([^"]+)"')
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(raw)
        if match:
            parsed[match.group(1)].add(match.group(2).strip())
    return parsed


def parse_manual_apps(path: Path) -> set[str]:
    apps: set[str] = set()
    if not path.exists():
        return apps
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("- "):
            continue
        value = line[2:].strip()
        if not value or value.startswith("_"):
            continue
        candidates = [value]
        candidates.extend(re.findall(r"`([^`]+)`", value))
        for candidate in list(candidates):
            candidate_path_name = Path(candidate).name
            if candidate_path_name and candidate_path_name != candidate:
                candidates.append(candidate_path_name)
        for candidate in candidates:
            normalized = normalize_app_name(candidate)
            if normalized:
                apps.add(normalized)
    return apps


def normalize_app_name(value: str) -> str:
    value = value.lower().removesuffix(".app")
    return re.sub(r"[^a-z0-9]+", "", value)


def normalize_extension(value: str) -> str:
    return value.strip().lower()


def add_finding(
    findings: list[dict[str, Any]],
    *,
    area: str,
    classification: str,
    name: str,
    summary: str,
    severity: str = "info",
    source: str | None = None,
    details: dict[str, Any] | None = None,
    recommendation: str | None = None,
) -> None:
    finding: dict[str, Any] = {
        "area": area,
        "classification": classification,
        "name": name,
        "severity": severity,
        "summary": summary,
    }
    if source:
        finding["source"] = source
    if details:
        finding["details"] = details
    if recommendation:
        finding["recommendation"] = recommendation
    findings.append(finding)


def add_manifest_presence(
    findings: list[dict[str, Any]], area: str, path: Path, label: str
) -> bool:
    if path.exists():
        add_finding(
            findings,
            area=area,
            classification="canonical",
            name=f"{label}.manifest",
            source=str(path.relative_to(ROOT)),
            summary=f"{label} manifest is present.",
            details={"path": str(path)},
        )
        return True

    add_finding(
        findings,
        area=area,
        classification="declared_absent",
        name=f"{label}.manifest",
        severity="medium",
        source=str(path.relative_to(ROOT)),
        summary=f"{label} manifest is missing.",
        recommendation="Restore the manifest before making install provenance decisions.",
    )
    return False


def which_all(command: str) -> list[str]:
    seen: set[str] = set()
    matches: list[str] = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        candidate = Path(entry).expanduser() / command
        try:
            if (
                candidate.exists()
                and (candidate.is_file() or candidate.is_symlink())
                and os.access(candidate, os.X_OK)
            ):
                resolved = str(candidate.resolve())
                key = f"{candidate}:{resolved}"
                if key not in seen:
                    seen.add(key)
                    matches.append(str(candidate))
        except OSError:
            continue
    return matches


@lru_cache(maxsize=256)
def pkgutil_file_info(path: str) -> dict[str, str]:
    if not shutil.which("pkgutil"):
        return {}
    result = command_result(["pkgutil", "--file-info", path], timeout=5)
    if not result["ok"]:
        return {}

    info: dict[str, str] = {}
    for raw in result["stdout"].splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        if key and value:
            info[key] = value
    return info


def path_provenance(path: str | None) -> dict[str, Any]:
    if not path:
        return {"source": "absent"}

    original = str(Path(path).expanduser())
    try:
        resolved = str(Path(original).resolve())
    except OSError:
        resolved = original

    home = str(HOME)
    mise_data_dir = f"{home}/.local/share/mise"
    details: dict[str, Any] = {
        "path": original,
        "resolved_path": resolved,
    }
    codex_runtime_provided = is_codex_runtime_path(original) or is_codex_runtime_path(resolved)
    details["codex_runtime_provided"] = codex_runtime_provided

    def with_source(source: str) -> dict[str, Any]:
        if source in {"microsoft_dotnet_pkg", "manual/pkg"}:
            pkg_info = pkgutil_file_info(resolved) or pkgutil_file_info(original)
            if pkg_info:
                details["pkgutil"] = pkg_info
        return {"source": source, **details}

    if ".cache/codex-runtimes/" in resolved or "/codex-runtimes/" in resolved:
        return with_source("codex_runtime")
    if "/var/run/com.apple.security.cryptexd/codex." in resolved:
        return with_source("codex_runtime")
    if resolved.startswith("/pkg/env/"):
        return with_source("codex_runtime")
    if original == mise_data_dir or original.startswith(f"{mise_data_dir}/"):
        return with_source("mise")
    if resolved.startswith("/opt/homebrew/") or "/opt/homebrew/Cellar/" in resolved:
        return with_source("homebrew")
    if resolved.startswith("/usr/local/Homebrew/") or "/usr/local/Cellar/" in resolved:
        return with_source("homebrew")
    if resolved.startswith(f"{mise_data_dir}/") or resolved == mise_data_dir:
        return with_source("mise")
    if resolved.startswith(f"{home}/.local/share/fnm") or original.startswith(
        f"{home}/.local/share/fnm"
    ):
        return with_source("fnm")
    if resolved.startswith(f"{home}/.local/state/fnm_multishells") or original.startswith(
        f"{home}/.local/state/fnm_multishells"
    ):
        return with_source("fnm")
    if resolved.startswith(f"{home}/Library/pnpm") or original.startswith(f"{home}/Library/pnpm"):
        return with_source("pnpm")
    if resolved.startswith("/usr/local/share/dotnet"):
        return with_source("microsoft_dotnet_pkg")
    if "/Applications/" in resolved and ".app/Contents/" in resolved:
        return with_source("app/manual")
    if resolved.startswith(f"{home}/.npm") or "/node_modules/" in resolved:
        return with_source("npm")
    if resolved.startswith(f"{home}/.local/bin") or original.startswith(f"{home}/.local/bin"):
        return with_source("manual/local")
    if resolved.startswith("/usr/local/bin") or original.startswith("/usr/local/bin"):
        pkg_info = pkgutil_file_info(resolved) or pkgutil_file_info(original)
        if pkg_info:
            details["pkgutil"] = pkg_info
            return {"source": "manual/pkg", **details}
        return with_source("manual/local")
    if resolved.startswith("/usr/bin") or resolved.startswith("/bin"):
        return with_source("system")

    pkg_info = pkgutil_file_info(resolved) or pkgutil_file_info(original)
    if pkg_info:
        details["pkgutil"] = pkg_info
        return {"source": "manual/pkg", **details}
    return with_source("unknown")


def path_source(path: str | None) -> str:
    return str(path_provenance(path).get("source", "unknown"))


def is_codex_runtime_path(path: str | None) -> bool:
    if not path:
        return False
    value = str(path)
    return any(
        marker in value
        for marker in (
            ".cache/codex-runtimes/",
            "/codex-runtimes/",
            "/pkg/env/",
            "/var/run/com.apple.security.cryptexd/codex.",
            "/.codex/tmp/",
            "/Applications/Codex.app/",
        )
    )


def process_info(pid: int) -> dict[str, Any]:
    result = command_result(["ps", "-p", str(pid), "-o", "pid=", "-o", "ppid=", "-o", "comm="], timeout=5)
    if not result["ok"] or not result["stdout"]:
        return {"pid": pid}

    fields = result["stdout"].strip().split(None, 2)
    info: dict[str, Any] = {"pid": pid}
    if len(fields) >= 2:
        info["ppid"] = int(fields[1])
    if len(fields) >= 3:
        info["command"] = fields[2]
        info["basename"] = Path(fields[2]).name
    return info


def parent_process_chain(limit: int = 8) -> list[dict[str, Any]]:
    chain: list[dict[str, Any]] = []
    seen: set[int] = set()
    pid = os.getpid()
    for _ in range(limit):
        if pid <= 0 or pid in seen:
            break
        seen.add(pid)
        info = process_info(pid)
        chain.append(info)
        ppid = info.get("ppid")
        if not isinstance(ppid, int) or ppid <= 0 or ppid == pid:
            break
        pid = ppid
    return chain


def collect_execution_context() -> dict[str, Any]:
    path_raw = os.environ.get("PATH", "")
    path_entries = [entry for entry in path_raw.split(os.pathsep) if entry]
    chain = parent_process_chain()
    parent_shells = [
        item.get("basename")
        for item in chain
        if isinstance(item.get("basename"), str)
        and str(item["basename"]).lower() in SHELL_NAMES
    ]
    shell_env = os.environ.get("SHELL")
    shell_env_name = Path(shell_env).name if shell_env else None
    return {
        "pid": os.getpid(),
        "python_executable": sys.executable,
        "argv": sys.argv,
        "path": path_raw,
        "path_entries": path_entries,
        "shell_env": shell_env,
        "shell_env_name": shell_env_name,
        "parent_process_chain": chain,
        "detected_parent_shells": parent_shells,
    }


def expanded_path_entries() -> list[str]:
    result: list[str] = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        expanded = str(Path(entry).expanduser())
        if expanded not in result:
            result.append(expanded)
    return result


def modeled_laptop_js_env() -> dict[str, str]:
    env = os.environ.copy()
    pnpm_home = str(HOME / "Library/pnpm")
    path_entries = [
        str(HOME / ".local/share/fnm/aliases/default/bin"),
        pnpm_home,
        str(HOME / ".local/bin"),
    ]
    for entry in expanded_path_entries():
        if entry not in path_entries:
            path_entries.append(entry)
    env["PNPM_HOME"] = pnpm_home
    env["PATH"] = os.pathsep.join(path_entries)
    return env


def homebrew_candidate(command: str) -> str | None:
    for directory in (Path("/opt/homebrew/bin"), Path("/usr/local/bin")):
        candidate = directory / command
        try:
            if (
                candidate.exists()
                and (candidate.is_file() or candidate.is_symlink())
                and os.access(candidate, os.X_OK)
                and path_source(str(candidate)) == "homebrew"
            ):
                return str(candidate)
        except OSError:
            continue
    return None


def command_visibility(command: str) -> dict[str, Any]:
    current = shutil.which(command)
    path_matches = which_all(command)
    modeled: dict[str, Any] = {"available": False}
    fnm_default = fnm_default_version()
    if fnm_default:
        env = modeled_laptop_js_env()
        result = command_result(
            ["fnm", "exec", "--using", "default", command, "--version"],
            timeout=12,
            env=env,
        )
        modeled = {
            "available": result["ok"],
            "default": fnm_default,
            "version": result["stdout"].splitlines()[0] if result["stdout"] else None,
            "returncode": result["returncode"],
            "stderr": result["stderr"][:300],
            "source": "fnm_default",
            "env_overrides": {
                "PNPM_HOME": env.get("PNPM_HOME"),
                "PATH_prefix": env.get("PATH", "").split(os.pathsep)[:3],
            },
        }

    return {
        "current_process": path_provenance(current) if current else None,
        "path_matches": [path_provenance(path) for path in path_matches],
        "homebrew_candidate": (
            path_provenance(homebrew_candidate(command))
            if homebrew_candidate(command)
            else None
        ),
        "modeled_fnm_default": modeled,
        "has_codex_runtime_candidate": any(
            is_codex_runtime_path(path) for path in ([current] if current else []) + path_matches
        ),
        "current_process_is_codex_runtime": is_codex_runtime_path(current),
    }


def shell_probe_source() -> str:
    return f'''
from __future__ import annotations
import json
import os
import shutil
from pathlib import Path

commands = {json.dumps(SHELL_PARITY_COMMANDS)}
env_keys = {json.dumps(SHELL_PARITY_ENV_KEYS)}
home = str(Path.home())
path_raw = os.environ.get("PATH", "")
path_entries = [entry for entry in path_raw.split(os.pathsep) if entry]


def which_all(command):
    seen = set()
    matches = []
    for entry in path_entries:
        candidate = Path(entry).expanduser() / command
        try:
            if (
                candidate.exists()
                and (candidate.is_file() or candidate.is_symlink())
                and os.access(candidate, os.X_OK)
            ):
                resolved = str(candidate.resolve())
                key = (str(candidate), resolved)
                if key not in seen:
                    seen.add(key)
                    matches.append({{"path": str(candidate), "resolved_path": resolved}})
        except OSError:
            continue
    return matches


payload = {{
    "env": {{key: os.environ.get(key) for key in env_keys}},
    "fnm_env": {{
        key: value
        for key, value in sorted(os.environ.items())
        if key.startswith("FNM_")
    }},
    "mise_env": {{
        key: value
        for key, value in sorted(os.environ.items())
        if key.startswith("MISE_")
    }},
    "path_contains": {{
        "codex_runtime": any(
            "codex" in entry.lower() or "/pkg/env/" in entry
            for entry in path_entries
        ),
        "dotnet_tools_expanded": f"{{home}}/.dotnet/tools" in path_entries,
        "dotnet_tools_literal_tilde": "~/.dotnet/tools" in path_entries,
        "fnm_multishell_bin": any(
            ".local/state/fnm_multishells" in entry for entry in path_entries
        ),
        "fnm_default_alias_bin": f"{{home}}/.local/share/fnm/aliases/default/bin" in path_entries,
        "homebrew_bin": "/opt/homebrew/bin" in path_entries,
        "homebrew_sbin": "/opt/homebrew/sbin" in path_entries,
        "mise_shims": f"{{home}}/.local/share/mise/shims" in path_entries,
        "pnpm_home_expanded": f"{{home}}/Library/pnpm" in path_entries,
        "usr_local_bin": "/usr/local/bin" in path_entries,
    }},
    "path_entries": path_entries,
    "commands": {{
        command: {{"which": shutil.which(command), "all": which_all(command)}}
        for command in commands
    }},
}}
print("{SHELL_PROBE_START}")
print(json.dumps(payload, sort_keys=True))
print("{SHELL_PROBE_END}")
'''.strip()


def parse_shell_probe_stdout(stdout: str) -> dict[str, Any] | None:
    if SHELL_PROBE_START not in stdout or SHELL_PROBE_END not in stdout:
        return None
    body = stdout.split(SHELL_PROBE_START, 1)[1].split(SHELL_PROBE_END, 1)[0].strip()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def shell_probe_contexts() -> list[dict[str, Any]]:
    python_command = f'/usr/bin/python3 -c "${SHELL_PROBE_ENV_KEY}"'
    return [
        {
            "name": "codex_process",
            "requires": ["/bin/sh", "/usr/bin/python3"],
            "args": ["/bin/sh", "-c", python_command],
        },
        {
            "name": "zsh_non_login",
            "requires": ["/bin/zsh", "/usr/bin/python3"],
            "args": ["/bin/zsh", "-c", python_command],
        },
        {
            "name": "zsh_login",
            "startup_probe": True,
            "requires": ["/bin/zsh", "/usr/bin/python3"],
            "args": ["/bin/zsh", "-lic", python_command],
        },
        {
            "name": "just_default_recipe_shell",
            "requires": ["just", "/bin/zsh", "/usr/bin/python3"],
            "args": [
                "/bin/zsh",
                "-c",
                (
                    "just --justfile <(printf 'probe:\\n\\t@/usr/bin/python3 "
                    f"-c \"${SHELL_PROBE_ENV_KEY}\"\\n') probe"
                ),
            ],
        },
    ]


def requirement_available(requirement: str) -> bool:
    if requirement.startswith("/"):
        return Path(requirement).exists()
    return shutil.which(requirement) is not None


def run_shell_probe(context: dict[str, Any], probe: str) -> dict[str, Any]:
    if context.get("startup_probe") and os.environ.get(
        SHELL_PROBE_ALLOW_STARTUP_KEY
    ) not in {"1", "true", "yes"}:
        return {
            "name": context["name"],
            "ok": False,
            "skipped": True,
            "startup_probe": True,
            "reason": (
                f"Set {SHELL_PROBE_ALLOW_STARTUP_KEY}=1 to execute login "
                "startup probes. They can run user startup hooks."
            ),
        }

    missing = [
        requirement
        for requirement in context.get("requires", [])
        if not requirement_available(requirement)
    ]
    if missing:
        return {
            "name": context["name"],
            "ok": False,
            "skipped": True,
            "missing": missing,
        }

    env = os.environ.copy()
    env[SHELL_PROBE_ENV_KEY] = probe
    result = command_result(context["args"], timeout=35, env=env)
    payload = parse_shell_probe_stdout(result["stdout"])
    return {
        "name": context["name"],
        "ok": result["ok"] and payload is not None,
        "returncode": result["returncode"],
        "timed_out": result["timed_out"],
        "payload": payload,
        "stderr": result["stderr"][:1000],
        "startup_stdout": result["stdout"].split(SHELL_PROBE_START, 1)[0].strip()[:1000],
    }


def check_dev_env_wrapper(findings: list[dict[str, Any]], probe: str) -> None:
    if not DEV_ENV.exists():
        add_finding(
            findings,
            area="shell_parity",
            classification="declared_absent",
            name="shell_parity.dev_env_wrapper",
            severity="medium",
            summary="The non-interactive development environment wrapper is missing.",
            source=str(DEV_ENV.relative_to(ROOT)),
            recommendation="Restore scripts/dev_env.sh or update the execution-context contract.",
        )
        return

    result = command_result([str(DEV_ENV), "/usr/bin/python3", "-c", probe], timeout=35)
    payload = parse_shell_probe_stdout(result["stdout"])
    command_info = (payload or {}).get("commands", {})
    missing = [
        command
        for command in DEV_ENV_EXPECTED_COMMANDS
        if not command_info.get(command, {}).get("which")
    ]
    sources = {
        command: path_provenance(command_info.get(command, {}).get("which"))
        for command in DEV_ENV_EXPECTED_COMMANDS
    }

    add_finding(
        findings,
        area="shell_parity",
        classification="canonical" if result["ok"] and payload and not missing else "unknown",
        name="shell_parity.dev_env_wrapper",
        severity="info" if result["ok"] and payload and not missing else "medium",
        source=str(DEV_ENV.relative_to(ROOT)),
        summary=(
            "dev_env wrapper exposes the expected non-interactive command surface."
            if result["ok"] and payload and not missing
            else "dev_env wrapper does not expose the full expected command surface."
        ),
        details={
            "commands": sources,
            "missing": missing,
            "path_flags": (payload or {}).get("path_contains", {}),
            "path_prefix": (payload or {}).get("path_entries", [])[:8],
            "returncode": result["returncode"],
            "stderr": result["stderr"][:500],
        },
        recommendation=(
            "Use scripts/dev_env.sh for AI/tool-launched commands that need the repo PATH contract."
            if result["ok"] and payload and not missing
            else "Fix scripts/dev_env.sh before relying on it from AI/tool-launched commands."
        ),
    )


def compact_command_matrix(
    probes: list[dict[str, Any]], commands: list[str]
) -> dict[str, dict[str, str | None]]:
    matrix: dict[str, dict[str, str | None]] = {}
    for command in commands:
        matrix[command] = {}
        for probe in probes:
            payload = probe.get("payload") or {}
            command_info = payload.get("commands", {}).get(command, {})
            matrix[command][probe["name"]] = command_info.get("which")
    return matrix


def compact_env_matrix(
    probes: list[dict[str, Any]], keys: list[str]
) -> dict[str, dict[str, str | None]]:
    matrix: dict[str, dict[str, str | None]] = {}
    for key in keys:
        matrix[key] = {}
        for probe in probes:
            payload = probe.get("payload") or {}
            matrix[key][probe["name"]] = payload.get("env", {}).get(key)
    return matrix


def path_flag_matrix(probes: list[dict[str, Any]]) -> dict[str, dict[str, bool | None]]:
    flags = [
        "codex_runtime",
        "dotnet_tools_expanded",
        "dotnet_tools_literal_tilde",
        "fnm_default_alias_bin",
        "fnm_multishell_bin",
        "mise_shims",
        "pnpm_home_expanded",
    ]
    matrix: dict[str, dict[str, bool | None]] = {}
    for flag in flags:
        matrix[flag] = {}
        for probe in probes:
            payload = probe.get("payload") or {}
            matrix[flag][probe["name"]] = payload.get("path_contains", {}).get(flag)
    return matrix


def differing_values(values: dict[str, Any]) -> set[Any]:
    return {value for value in values.values() if value not in (None, "", [])}


def command_path_source(path: str | None) -> str:
    return str(path_provenance(path).get("source", "absent"))


def shell_parity_gaps(
    command_matrix: dict[str, dict[str, str | None]],
    env_matrix: dict[str, dict[str, str | None]],
    paths: dict[str, dict[str, bool | None]],
    editor_policy: dict[str, Any],
    alias_policy: dict[str, Any],
) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []

    pnpm_sources = {
        name: command_path_source(path) for name, path in command_matrix["pnpm"].items()
    }
    if len(differing_values(pnpm_sources)) > 1:
        gaps.append(
            {
                "area": "pnpm",
                "finding": "pnpm resolves through different sources across shell contexts.",
                "impact": f"Observed sources: {pnpm_sources}.",
                "recommendation": "Use the ADR-0007 explicit fnm/default wrapper until PATH parity is enforced.",
            }
        )

    corepack_visibility = command_matrix["corepack"]
    if any(value is None for value in corepack_visibility.values()) and any(
        corepack_visibility.values()
    ):
        gaps.append(
            {
                "area": "pnpm",
                "finding": "Corepack is visible only in fnm-activated contexts.",
                "impact": f"corepack by context: {corepack_visibility}.",
                "recommendation": "Run Corepack commands through the ADR-0007 fnm/default wrapper until shell parity is fixed.",
            }
        )

    node_sources = {
        name: command_path_source(path) for name, path in command_matrix["node"].items()
    }
    if len(differing_values(node_sources)) > 1:
        gaps.append(
            {
                "area": "fnm",
                "finding": "Node resolves through fnm only in fnm-activated contexts.",
                "impact": f"Observed sources: {node_sources}.",
                "recommendation": "Keep Node automation on `fnm exec --using default` rather than plain node/npm/pnpm.",
            }
        )

    fnm_values = env_matrix.get("FNM_DIR", {})
    npm_sources = {
        name: command_path_source(path) for name, path in command_matrix["npm"].items()
    }
    corepack_sources = {
        name: command_path_source(path) for name, path in command_matrix["corepack"].items()
    }
    runtime_source_values = {
        source
        for sources in (node_sources, npm_sources, pnpm_sources, corepack_sources)
        for source in sources.values()
        if source != "absent"
    }
    runtime_commands_are_fnm = bool(runtime_source_values) and runtime_source_values <= {"fnm"}
    if any(value is None for value in fnm_values.values()) and any(fnm_values.values()):
        if not runtime_commands_are_fnm:
            gaps.append(
                {
                    "area": "fnm",
                    "finding": "FNM_* variables are not exported consistently.",
                    "impact": f"FNM_DIR by context: {fnm_values}.",
                    "recommendation": "Generate or share shell environment ownership before relying on plain runtime commands.",
                }
            )

    pnpm_home_values = env_matrix.get("PNPM_HOME", {})
    if len(differing_values(pnpm_home_values)) > 1:
        gaps.append(
            {
                "area": "PATH",
                "finding": "PNPM_HOME alternates between literal tilde and expanded absolute paths.",
                "impact": f"PNPM_HOME by context: {pnpm_home_values}.",
                "recommendation": "Use an expanded shared PATH source for both Nu and zsh.",
            }
        )

    dotnet_tools = paths.get("dotnet_tools_expanded", {})
    dotnet_tools_literal = paths.get("dotnet_tools_literal_tilde", {})
    if any(value is False for value in dotnet_tools.values()):
        gaps.append(
            {
                "area": "dotnet",
                "finding": ".NET global tool path visibility differs by shell.",
                "impact": (
                    f"Expanded path: {dotnet_tools}; literal tilde path: "
                    f"{dotnet_tools_literal}."
                ),
                "recommendation": "Put the expanded ~/.dotnet/tools path in the shared shell environment.",
            }
        )

    dotnet_sources = {
        name: command_path_source(path) for name, path in command_matrix["dotnet"].items()
    }
    dotnet_migration_pending = mise_config_declares_dotnet_policy()
    if len(differing_values(dotnet_sources)) > 1 or any(
        value is None for value in env_matrix.get("DOTNET_ROOT", {}).values()
    ):
        gaps.append(
            {
                "area": "dotnet",
                "finding": "dotnet source and DOTNET_ROOT are not aligned.",
                "impact": (
                    f"dotnet sources: {dotnet_sources}; DOTNET_ROOT: "
                    f"{env_matrix.get('DOTNET_ROOT', {})}."
                ),
                "recommendation": (
                    "ADR-0006 mise policy is declared; keep current SDK sources as managed exceptions until mise parity is proven."
                    if dotnet_migration_pending
                    else "Do not remove current SDK sources until ADR-0006 mise parity is proven."
                ),
            }
        )

    if not any(paths.get("mise_shims", {}).values()):
        if not dotnet_migration_pending:
            gaps.append(
                {
                    "area": "mise",
                    "finding": "mise shims are not visible in probed shell contexts.",
                    "impact": "The ADR-0006 .NET target is not active in shell PATH yet.",
                    "recommendation": "Install and activate mise in a later approved implementation step.",
                }
            )

    ai_commands = ["claude", "opencode", "pi", "apm"]
    ai_visibility = {
        command: command_matrix[command]
        for command in ai_commands
        if any(value is None for value in command_matrix[command].values())
        and any(command_matrix[command].values())
    }
    if ai_visibility:
        gaps.append(
            {
                "area": "ai_tools",
                "finding": "AI CLI visibility differs by shell context.",
                "impact": f"Visibility drift: {ai_visibility}.",
                "recommendation": "Declare intended AI Tool Surface CLI paths before enforcing shell parity.",
            }
        )

    zsh_aliases = alias_policy.get("zsh", {}).get("aliases", [])
    if not zsh_aliases:
        gaps.append(
            {
                "area": "aliases",
                "finding": "Repo-managed zsh aliases were not detected.",
                "impact": "Interactive convenience aliases may be missing from the primary shell.",
                "recommendation": "Do not use aliases in bootstrap, just recipes, or AI-generated commands.",
            }
        )

    if not justfile_declares_shell():
        gaps.append(
            {
                "area": "just",
                "finding": "The repo justfile does not declare a recipe shell.",
                "impact": "`just` recipes use the task runner default shell and inherit the caller environment.",
                "recommendation": "Treat just bootstrap as POSIX/zsh-compatible automation unless a later ADR changes it.",
            }
        )

    editor_shells = {
        name: policy.get("default_shell")
        for name, policy in editor_policy.items()
        if isinstance(policy, dict)
    }
    if "nu" in editor_shells.values():
        gaps.append(
            {
                "area": "editor_terminal",
                "finding": "Repo-managed editor terminals are configured for deprecated Nu.",
                "impact": f"Editor policy: {editor_shells}.",
                "recommendation": "Use zsh as the primary editor terminal shell.",
            }
        )

    return gaps


def extract_jsonc_string(text: str, key: str) -> str | None:
    pattern = re.compile(rf'"{re.escape(key)}"\s*:\s*"([^"]+)"')
    match = pattern.search(text)
    return match.group(1) if match else None


def editor_shell_policy() -> dict[str, Any]:
    policies: dict[str, Any] = {}
    for name, path in {
        "vscode": ROOT / "system/vscode/settings.jsonc",
    }.items():
        if not path.exists():
            policies[name] = {"configured": False}
            continue
        text = path.read_text(encoding="utf-8")
        default_profile = extract_jsonc_string(text, "terminal.integrated.defaultProfile.osx")
        policies[name] = {
            "configured": bool(default_profile),
            "default_profile_osx": default_profile,
            "default_shell": default_profile,
            "source": str(path.relative_to(ROOT)),
        }

    ghostty = ROOT / "system/ghostty/config"
    if ghostty.exists():
        text = ghostty.read_text(encoding="utf-8")
        command_match = re.search(r"(?m)^\s*command\s*=\s*(.+?)\s*$", text)
        command = command_match.group(1) if command_match else None
        command_path = command.split()[0] if command else None
        policies["ghostty"] = {
            "configured": bool(command),
            "command": command,
            "default_shell": Path(command_path).name if command_path else None,
            "source": str(ghostty.relative_to(ROOT)),
        }
    else:
        policies["ghostty"] = {"configured": False}
    return policies


def shell_alias_policy() -> dict[str, Any]:
    result: dict[str, Any] = {
        "zsh": {"aliases": [], "sources": []},
    }
    repo_zsh_sources = [ZSH_ENV, ZSH_PROFILE, ZSH_RC]
    zsh_sources = (
        repo_zsh_sources
        if any(source.exists() for source in repo_zsh_sources)
        else [HOME / ".zshenv", HOME / ".zprofile", HOME / ".zshrc"]
    )
    zsh_aliases = []
    for source in zsh_sources:
        if not source.exists():
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        zsh_aliases.extend(
            match.group(1)
            for match in re.finditer(
                r"(?m)^\s*alias\s+([A-Za-z0-9_.-]+)=",
                text,
            )
        )
        try:
            display_source = str(source.relative_to(ROOT))
        except ValueError:
            display_source = str(source)
        result["zsh"]["sources"].append(display_source)
    result["zsh"]["aliases"] = sorted(set(zsh_aliases))
    return result


def justfile_declares_shell() -> bool:
    justfile = ROOT / "justfile"
    if not justfile.exists():
        return False
    return re.search(
        r"(?m)^\s*set\s+(windows-)?shell\s*:=",
        justfile.read_text(encoding="utf-8"),
    ) is not None


def check_shell_parity(findings: list[dict[str, Any]]) -> None:
    probe = shell_probe_source()
    probes = [run_shell_probe(context, probe) for context in shell_probe_contexts()]
    successful = [item for item in probes if item.get("payload")]
    command_matrix = compact_command_matrix(successful, SHELL_PARITY_COMMANDS)
    env_matrix = compact_env_matrix(successful, SHELL_PARITY_ENV_KEYS)
    paths = path_flag_matrix(successful)
    editor_policy = editor_shell_policy()
    alias_policy = shell_alias_policy()
    gaps = shell_parity_gaps(
        command_matrix,
        env_matrix,
        paths,
        editor_policy,
        alias_policy,
    )
    skipped = [item for item in probes if item.get("skipped")]
    failed = [
        item
        for item in probes
        if not item.get("ok") and not item.get("skipped")
    ]

    add_finding(
        findings,
        area="shell_parity",
        classification="unknown" if gaps or failed or skipped else "canonical",
        name="shell_parity.contexts",
        severity="medium" if gaps or failed else "info",
        summary=(
            f"Shell parity probes found {len(gaps)} drift areas across "
            f"{len(successful)} executable contexts."
        ),
        details={
            "probes": probes,
            "startup_probe_policy": {
                "enabled": os.environ.get(SHELL_PROBE_ALLOW_STARTUP_KEY)
                in {"1", "true", "yes"},
                "env": SHELL_PROBE_ALLOW_STARTUP_KEY,
                "reason": (
                    "Login shell probes are opt-in because they execute user "
                    "startup files and may write caches or run hooks."
                ),
            },
            "command_matrix": command_matrix,
            "env_matrix": env_matrix,
            "path_flags": paths,
            "editor_policy": editor_policy,
            "alias_policy": alias_policy,
            "gaps": gaps,
        },
        recommendation=(
            "Keep automation on explicit POSIX-compatible commands and wrappers "
            "until shared shell PATH ownership is implemented."
            if gaps or failed
            else None
        ),
    )
    check_dev_env_wrapper(findings, probe)


def check_js_toolchain(findings: list[dict[str, Any]]) -> dict[str, Any]:
    commands = {command: command_visibility(command) for command in JS_COMMANDS}
    codex_commands = sorted(
        command for command, info in commands.items() if info["has_codex_runtime_candidate"]
    )

    add_finding(
        findings,
        area="js_toolchain",
        classification="unknown" if codex_commands else "canonical",
        name="js_toolchain.resolution",
        severity="low" if codex_commands else "info",
        summary=(
            "JavaScript toolchain candidates include Codex/runtime-provided binaries."
            if codex_commands
            else "JavaScript toolchain candidates do not include Codex/runtime-provided binaries."
        ),
        details={
            "commands": commands,
            "codex_runtime_commands": codex_commands,
            "primary_selection_policy": (
                "Prefer fnm exec --using default; fall back to Homebrew; do not "
                "use Codex runtime pnpm/npm for canonical laptop drift claims."
            ),
        },
        recommendation=(
            "Interpret current-process npm/pnpm as context only when Codex runtime candidates are present."
            if codex_commands
            else None
        ),
    )

    for command in ("npx", "corepack"):
        info = commands[command]
        available = bool(info["current_process"]) or bool(info["modeled_fnm_default"].get("available"))
        add_finding(
            findings,
            area="js_toolchain",
            classification="canonical" if available else "declared_absent",
            name=f"js_toolchain.{command}_visibility",
            severity="info" if available else "low",
            summary=(
                f"{command} is visible through the current process or modeled fnm/default toolchain."
                if available
                else f"{command} was not visible through the current process or modeled fnm/default toolchain."
            ),
            details=info,
        )

    stale_packages: list[dict[str, Any]] = []
    for root in (Path("/opt/homebrew/lib/node_modules"), Path("/usr/local/lib/node_modules")):
        if not root.is_dir():
            continue
        try:
            for child in sorted(root.iterdir(), key=lambda value: value.name):
                stale_packages.append(
                    {
                        "root": str(root),
                        "name": child.name,
                        "path": str(child),
                        "kind": "directory" if child.is_dir() else "file",
                    }
                )
        except OSError as exc:
            stale_packages.append({"root": str(root), "error": str(exc)})

    stale_symlinks: list[dict[str, str]] = []
    for directory in (Path("/opt/homebrew/bin"), Path("/usr/local/bin")):
        if not directory.is_dir():
            continue
        try:
            for child in sorted(directory.iterdir(), key=lambda value: value.name):
                if not child.is_symlink():
                    continue
                try:
                    target = os.readlink(child)
                except OSError:
                    continue
                if "node_modules" in target or "node_modules" in str(child.resolve()):
                    stale_symlinks.append(
                        {
                            "path": str(child),
                            "target": target,
                            "resolved_path": str(child.resolve()),
                        }
                    )
        except OSError:
            continue

    if stale_packages or stale_symlinks:
        add_finding(
            findings,
            area="js_toolchain",
            classification="drift",
            name="js_toolchain.homebrew_prefix_node_globals",
            severity="medium",
            summary="Homebrew-prefix Node global leftovers are present outside the canonical fnm/pnpm ownership model.",
            details={
                "packages": stale_packages,
                "bin_symlinks": stale_symlinks,
            },
            recommendation=(
                "Remove stale Homebrew-prefix Node globals after confirming their "
                "commands are provided by the declared pnpm global manifest."
            ),
        )
    else:
        add_finding(
            findings,
            area="js_toolchain",
            classification="canonical",
            name="js_toolchain.homebrew_prefix_node_globals",
            summary="No Homebrew-prefix Node global packages or bin symlinks were detected.",
            details={
                "checked_package_roots": [
                    "/opt/homebrew/lib/node_modules",
                    "/usr/local/lib/node_modules",
                ],
                "checked_bin_dirs": ["/opt/homebrew/bin", "/usr/local/bin"],
            },
        )

    return commands


def fnm_default_version() -> str | None:
    if not shutil.which("fnm"):
        return None
    result = command_result(["fnm", "default"], timeout=10)
    if result["ok"] and result["stdout"]:
        return result["stdout"].splitlines()[0].strip()
    return None


def equivalent_member(name: str, values: set[str]) -> bool:
    short_values = {short_brew_name(value) for value in values}
    return name in values or short_brew_name(name) in short_values


def is_dev_related(name: str) -> bool:
    return bool(DEV_RE.search(name.lower()))


def check_brew(findings: list[dict[str, Any]]) -> dict[str, set[str]]:
    add_manifest_presence(findings, "brew", BREWFILE, "Homebrew")
    declared = parse_brewfile(BREWFILE)
    personal_declared = parse_brewfile(PERSONAL_BREWFILE)

    brew_path = shutil.which("brew")
    if not brew_path:
        add_finding(
            findings,
            area="brew",
            classification="unknown",
            name="homebrew.command",
            severity="medium",
            summary="brew is not on PATH, so installed Homebrew packages cannot be audited.",
            recommendation="Use the declared Brewfile as desired state until Homebrew is available.",
        )
        return declared

    add_finding(
        findings,
        area="brew",
        classification="canonical",
        name="homebrew.command",
        source=brew_path,
        summary="brew is available for read-only package inventory.",
        details=path_provenance(brew_path),
    )

    formulae_result = command_result(["brew", "list", "--formula", "--full-name"])
    casks_result = command_result(["brew", "list", "--cask"])
    leaves_result = command_result(["brew", "leaves"])

    installed_formulae = set(lines(formulae_result["stdout"])) if formulae_result["ok"] else set()
    installed_casks = set(lines(casks_result["stdout"])) if casks_result["ok"] else set()
    installed_leaves = set(lines(leaves_result["stdout"])) if leaves_result["ok"] else installed_formulae

    missing_formulae = sorted(
        name for name in declared["brew"] if not equivalent_member(name, installed_formulae)
    )
    missing_casks = sorted(
        name for name in declared["cask"] if not equivalent_member(name, installed_casks)
    )
    present_formulae = sorted(
        name for name in declared["brew"] if equivalent_member(name, installed_formulae)
    )
    present_casks = sorted(
        name for name in declared["cask"] if equivalent_member(name, installed_casks)
    )

    add_finding(
        findings,
        area="brew",
        classification="canonical" if not missing_formulae else "declared_absent",
        name="homebrew.formulae.declared",
        severity="info" if not missing_formulae else "medium",
        source=str(BREWFILE.relative_to(ROOT)),
        summary=(
            f"{len(present_formulae)}/{len(declared['brew'])} declared Homebrew "
            "formulae appear installed."
        ),
        details={"present": present_formulae, "missing": missing_formulae},
        recommendation=(
            "A later install task can decide whether to install missing declared formulae."
            if missing_formulae
            else None
        ),
    )
    add_finding(
        findings,
        area="brew",
        classification="canonical" if not missing_casks else "declared_absent",
        name="homebrew.casks.declared",
        severity="info" if not missing_casks else "medium",
        source=str(BREWFILE.relative_to(ROOT)),
        summary=(
            f"{len(present_casks)}/{len(declared['cask'])} declared Homebrew "
            "casks appear installed."
        ),
        details={"present": present_casks, "missing": missing_casks},
        recommendation=(
            "A later install task can decide whether to install missing declared casks."
            if missing_casks
            else None
        ),
    )

    declared_or_personal_formulae = declared["brew"] | personal_declared["brew"]
    declared_or_personal_casks = declared["cask"] | personal_declared["cask"]
    undeclared_formulae = sorted(
        name
        for name in installed_leaves
        if not equivalent_member(name, declared_or_personal_formulae)
        and is_dev_related(name)
    )
    undeclared_casks = sorted(
        name
        for name in installed_casks
        if not equivalent_member(name, declared_or_personal_casks)
        and is_dev_related(name)
    )
    if undeclared_formulae or undeclared_casks:
        add_finding(
            findings,
            area="brew",
            classification="present_undeclared",
            name="homebrew.dev_tools.present_undeclared",
            severity="low",
            summary="Installed Homebrew dev-related tools were not declared in the Brewfile.",
            details={
                "formulae": undeclared_formulae,
                "casks": undeclared_casks,
                "formula_source": "brew leaves",
            },
            recommendation=(
                "Decide whether each tool belongs in the Brewfile, a manual manifest, "
                "or should be removed behind a Reset Approval Gate."
            ),
        )
    else:
        add_finding(
            findings,
            area="brew",
            classification="canonical",
            name="homebrew.dev_tools.present_undeclared",
            summary="No undeclared Homebrew dev-related leaves or casks were detected.",
        )

    if PERSONAL_BREWFILE.exists():
        personal_present_formulae = sorted(
            name
            for name in personal_declared["brew"]
            if equivalent_member(name, installed_formulae)
        )
        personal_missing_formulae = sorted(
            name
            for name in personal_declared["brew"]
            if not equivalent_member(name, installed_formulae)
        )
        personal_present_casks = sorted(
            name
            for name in personal_declared["cask"]
            if equivalent_member(name, installed_casks)
        )
        personal_missing_casks = sorted(
            name
            for name in personal_declared["cask"]
            if not equivalent_member(name, installed_casks)
        )
        personal_missing = personal_missing_formulae or personal_missing_casks
        add_finding(
            findings,
            area="brew",
            classification="canonical" if not personal_missing else "declared_absent",
            name="homebrew.personal_packages",
            severity="info" if not personal_missing else "low",
            source=str(PERSONAL_BREWFILE.relative_to(ROOT)),
            summary=(
                "Gitignored personal Homebrew packages are installed."
                if not personal_missing
                else "Some gitignored personal Homebrew packages are missing."
            ),
            details={
                "manifest_gitignored": True,
                "present": {
                    "formulae": personal_present_formulae,
                    "casks": personal_present_casks,
                },
                "missing": {
                    "formulae": personal_missing_formulae,
                    "casks": personal_missing_casks,
                },
            },
            recommendation=(
                "Run just install-personal-brew if these personal packages should stay on this laptop."
                if personal_missing
                else None
            ),
        )
    else:
        add_finding(
            findings,
            area="brew",
            classification="not_required",
            name="homebrew.personal_packages",
            source=str(PERSONAL_BREWFILE.relative_to(ROOT)),
            summary="No gitignored personal Homebrew package manifest is present.",
            details={"manifest_gitignored": True},
        )

    return declared


def compare_extensions(
    findings: list[dict[str, Any]],
    *,
    area: str,
    command: str,
    manifest: Path,
    label: str,
) -> None:
    add_manifest_presence(findings, area, manifest, label)
    declared = {normalize_extension(value) for value in clean_manifest_lines(manifest)}
    cli_path = shutil.which(command)
    if not cli_path:
        add_finding(
            findings,
            area=area,
            classification="unknown",
            name=f"{label}.cli",
            severity="info",
            summary=f"{command} is not on PATH; installed {label} extensions were not audited.",
            recommendation=f"Run this doctor from an environment where {command} is available.",
        )
        return

    result = command_result([command, "--list-extensions"], timeout=20)
    if not result["ok"]:
        add_finding(
            findings,
            area=area,
            classification="unknown",
            name=f"{label}.extensions.installed",
            severity="low",
            source=cli_path,
            summary=f"{command} exists, but extension discovery did not complete.",
            details={
                "returncode": result["returncode"],
                "stderr": result["stderr"][:400],
            },
            recommendation="Keep this as audit data unless extension discovery remains broken.",
        )
        return

    installed = {normalize_extension(value) for value in lines(result["stdout"])}
    missing = sorted(declared - installed)
    undeclared = sorted(installed - declared)
    add_finding(
        findings,
        area=area,
        classification="canonical" if not missing else "declared_absent",
        name=f"{label}.extensions.declared",
        severity="info" if not missing else "medium",
        source=str(manifest.relative_to(ROOT)),
        summary=f"{len(declared) - len(missing)}/{len(declared)} declared {label} extensions appear installed.",
        details={"present_count": len(declared) - len(missing), "missing": missing},
        recommendation=(
            "A later install task can install missing declared extensions."
            if missing
            else None
        ),
    )
    if undeclared:
        add_finding(
            findings,
            area=area,
            classification="present_undeclared",
            name=f"{label}.extensions.present_undeclared",
            severity="low",
            source=cli_path,
            summary=f"{len(undeclared)} installed {label} extensions are not declared.",
            details={"extensions": undeclared},
            recommendation="Declare intentional extensions or remove them behind a Reset Approval Gate.",
        )
    else:
        add_finding(
            findings,
            area=area,
            classification="canonical",
            name=f"{label}.extensions.present_undeclared",
            source=cli_path,
            summary=f"No undeclared {label} extensions were detected.",
        )


def parse_pnpm_globals(stdout: str) -> set[str]:
    if not stdout.strip():
        return set()

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return parse_package_names_from_text(stdout)

    entries = data if isinstance(data, list) else [data]
    packages: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for key in ("dependencies", "devDependencies", "optionalDependencies"):
            dependencies = entry.get(key)
            if isinstance(dependencies, dict):
                packages.update(str(name) for name in dependencies)
    return packages


def parse_package_names_from_text(stdout: str) -> set[str]:
    packages: set[str] = set()
    for line in lines(stdout):
        if "/node_modules/" in line:
            package = line.rsplit("/node_modules/", 1)[1]
            parts = package.split("/")
            if parts[0].startswith("@") and len(parts) > 1:
                packages.add(f"{parts[0]}/{parts[1]}")
            else:
                packages.add(parts[0])
            continue
        match = re.search(r"((?:@[A-Za-z0-9_.-]+/)?[A-Za-z0-9_.-]+)@", line)
        if match:
            packages.add(match.group(1))
    return packages


def run_pnpm_list(args: list[str], env: dict[str, str] | None = None) -> dict[str, Any]:
    result = command_result(args, timeout=25, env=env)
    installed = parse_pnpm_globals(result["stdout"]) if result["stdout"] else set()
    return {**result, "installed": installed, "args": args}


def select_primary_pnpm_scope() -> dict[str, Any] | None:
    fnm_default = fnm_default_version()
    if fnm_default and shutil.which("fnm"):
        return {
            "scope": "primary_fnm_default",
            "trusted_for_canonical_drift": True,
            "args": ["fnm", "exec", "--using", "default", "pnpm", "list", "-g", "--depth", "0", "--json"],
            "env": modeled_laptop_js_env(),
            "toolchain": {
                "source": "fnm_default",
                "default": fnm_default,
                "fnm": path_provenance(shutil.which("fnm")),
                "modeled_env": {
                    "PNPM_HOME": str(HOME / "Library/pnpm"),
                    "PATH_prefix": modeled_laptop_js_env()["PATH"].split(os.pathsep)[:3],
                },
            },
        }

    homebrew_pnpm = homebrew_candidate("pnpm")
    if homebrew_pnpm:
        return {
            "scope": "primary_homebrew",
            "trusted_for_canonical_drift": True,
            "args": [homebrew_pnpm, "list", "-g", "--depth", "0", "--json"],
            "env": None,
            "toolchain": {
                "source": "homebrew",
                "pnpm": path_provenance(homebrew_pnpm),
            },
        }

    return None


def check_pnpm(findings: list[dict[str, Any]], js_commands: dict[str, Any]) -> set[str]:
    add_manifest_presence(findings, "pnpm", PNPM_GLOBAL, "pnpm global")
    declared = set(clean_manifest_lines(PNPM_GLOBAL))

    current_pnpm = shutil.which("pnpm")
    if current_pnpm:
        current_result = run_pnpm_list(
            [current_pnpm, "list", "-g", "--depth", "0", "--json"],
        )
        current_installed = sorted(current_result["installed"])
        current_is_codex = is_codex_runtime_path(current_pnpm)
        add_finding(
            findings,
            area="pnpm",
            classification="unknown",
            name="pnpm.globals.current_process",
            severity="low",
            source=current_pnpm,
            summary=(
                "Current-process pnpm is Codex/runtime-provided and is reported as context only."
                if current_is_codex
                else "Current-process pnpm is reported as context only, not canonical laptop drift."
            ),
            details={
                "scope": "current_process",
                "trusted_for_canonical_drift": False,
                "installed": current_installed,
                "provenance": path_provenance(current_pnpm),
                "returncode": current_result["returncode"],
                "stderr": current_result["stderr"][:400],
                "args": current_result["args"],
                "js_toolchain_resolution": js_commands.get("pnpm"),
            },
            recommendation=(
                "Ignore this pnpm for canonical drift; use the primary modeled laptop JS toolchain finding."
                if current_is_codex
                else None
            ),
        )
    else:
        add_finding(
            findings,
            area="pnpm",
            classification="unknown",
            name="pnpm.globals.current_process",
            severity="medium",
            summary="pnpm is not on the current process PATH.",
            details={"scope": "current_process", "trusted_for_canonical_drift": False},
        )

    primary = select_primary_pnpm_scope()
    if not primary:
        only_codex = bool(current_pnpm and is_codex_runtime_path(current_pnpm))
        add_finding(
            findings,
            area="pnpm",
            classification="unknown",
            name="pnpm.globals.primary_unavailable",
            severity="medium",
            summary=(
                "Only Codex/runtime pnpm is available; canonical pnpm drift cannot be trusted from this context."
                if only_codex
                else "No trusted primary pnpm toolchain was available for canonical drift."
            ),
            details={
                "current_process": path_provenance(current_pnpm) if current_pnpm else None,
                "selection_policy": "fnm default first, Homebrew fallback, Codex runtime excluded",
            },
            recommendation="Rerun from a laptop environment with fnm/default or Homebrew pnpm visible.",
        )
        return set()

    result = run_pnpm_list(primary["args"], env=primary["env"])
    installed = result["installed"]
    if not result["ok"] and not installed:
        add_finding(
            findings,
            area="pnpm",
            classification="unknown",
            name="pnpm.globals.primary_audit_failed",
            severity="medium",
            summary=f"Primary pnpm audit via {primary['scope']} did not produce package data.",
            details={
                "scope": primary["scope"],
                "trusted_for_canonical_drift": primary["trusted_for_canonical_drift"],
                "toolchain": primary["toolchain"],
                "returncode": result["returncode"],
                "stderr": result["stderr"][:500],
                "args": primary["args"],
            },
            recommendation="Treat pnpm drift as unknown until the primary laptop JS toolchain can be audited.",
        )
        return set()

    missing = sorted(declared - installed)
    undeclared = sorted(installed - declared)
    add_finding(
        findings,
        area="pnpm",
        classification="canonical" if not missing else "declared_absent",
        name="pnpm.globals.primary_declared",
        severity="info" if not missing else "medium",
        source=str(PNPM_GLOBAL.relative_to(ROOT)),
        summary=(
            f"{len(declared) - len(missing)}/{len(declared)} declared pnpm globals "
            f"appear installed via {primary['scope']}."
        ),
        details={
            "scope": primary["scope"],
            "trusted_for_canonical_drift": primary["trusted_for_canonical_drift"],
            "toolchain": primary["toolchain"],
            "installed": sorted(installed),
            "missing": missing,
            "returncode": result["returncode"],
            "stderr": result["stderr"][:400],
            "args": primary["args"],
        },
        recommendation=(
            "A later install task can install missing declared pnpm globals."
            if missing
            else None
        ),
    )
    if undeclared:
        add_finding(
            findings,
            area="pnpm",
            classification="present_undeclared",
            name="pnpm.globals.primary_present_undeclared",
            severity="low",
            source=primary["scope"],
            summary=f"{len(undeclared)} pnpm globals are installed but undeclared via {primary['scope']}.",
            details={
                "scope": primary["scope"],
                "trusted_for_canonical_drift": primary["trusted_for_canonical_drift"],
                "packages": undeclared,
                "toolchain": primary["toolchain"],
            },
            recommendation="Declare intentional pnpm globals or remove them behind a Reset Approval Gate.",
        )
    else:
        add_finding(
            findings,
            area="pnpm",
            classification="canonical",
            name="pnpm.globals.primary_present_undeclared",
            source=primary["scope"],
            summary=f"No undeclared pnpm globals were detected via {primary['scope']}.",
            details={
                "scope": primary["scope"],
                "trusted_for_canonical_drift": primary["trusted_for_canonical_drift"],
                "toolchain": primary["toolchain"],
            },
        )
    return installed


def parse_npm_globals(stdout: str) -> set[str]:
    if not stdout:
        return set()
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return parse_package_names_from_text(stdout)

    dependencies = data.get("dependencies", {}) if isinstance(data, dict) else {}
    if not isinstance(dependencies, dict):
        return set()
    return {str(name) for name in dependencies}


def run_npm_list(args: list[str], env: dict[str, str] | None = None) -> dict[str, Any]:
    result = command_result(args, timeout=25, env=env)
    installed = parse_npm_globals(result["stdout"]) if result["stdout"] else set()
    return {**result, "installed": installed, "args": args}


def npm_scopes() -> list[dict[str, Any]]:
    scopes: list[dict[str, Any]] = []
    fnm_default = fnm_default_version()
    if fnm_default and shutil.which("fnm"):
        env = modeled_laptop_js_env()
        scopes.append(
            {
                "scope": "primary_fnm_default",
                "trusted_for_canonical_drift": True,
                "args": ["fnm", "exec", "--using", "default", "npm", "ls", "-g", "--depth=0", "--json"],
                "env": env,
                "toolchain": {
                    "source": "fnm_default",
                    "default": fnm_default,
                    "fnm": path_provenance(shutil.which("fnm")),
                    "modeled_env": {
                        "PNPM_HOME": env.get("PNPM_HOME"),
                        "PATH_prefix": env.get("PATH", "").split(os.pathsep)[:3],
                    },
                },
            }
        )

    homebrew_npm = homebrew_candidate("npm")
    if homebrew_npm:
        scopes.append(
            {
                "scope": "homebrew",
                "trusted_for_canonical_drift": True,
                "args": [homebrew_npm, "ls", "-g", "--depth=0", "--json"],
                "env": None,
                "toolchain": {
                    "source": "homebrew",
                    "npm": path_provenance(homebrew_npm),
                },
            }
        )

    current_npm = shutil.which("npm")
    if current_npm:
        scopes.append(
            {
                "scope": "current_process",
                "trusted_for_canonical_drift": False,
                "args": [current_npm, "ls", "-g", "--depth=0", "--json"],
                "env": None,
                "toolchain": {
                    "source": "current_process",
                    "npm": path_provenance(current_npm),
                },
            }
        )
    return scopes


def check_npm(
    findings: list[dict[str, Any]],
    pnpm_declared: set[str],
    pnpm_installed: set[str],
    js_commands: dict[str, Any],
) -> None:
    scopes = npm_scopes()
    if not scopes:
        add_finding(
            findings,
            area="npm",
            classification="unknown",
            name="npm.globals",
            summary="No npm scope was available; npm globals were not audited.",
            details={"js_toolchain_resolution": js_commands.get("npm")},
        )
        return

    duplicate_basis = pnpm_declared | pnpm_installed
    for scope in scopes:
        result = run_npm_list(scope["args"], env=scope["env"])
        installed = result["installed"]
        duplicate_with_pnpm = sorted(installed & duplicate_basis)
        runtime_owned = (
            installed & NPM_RUNTIME_GLOBALS
            if scope["scope"] == "primary_fnm_default"
            else set()
        )
        legacy_globals = sorted(installed - set(duplicate_with_pnpm) - runtime_owned)
        current_process_codex = scope["scope"] == "current_process" and any(
            is_codex_runtime_path(value.get("path"))
            for value in [scope["toolchain"].get("npm", {})]
            if isinstance(value, dict)
        )
        trusted = bool(scope["trusted_for_canonical_drift"]) and not current_process_codex

        if not result["ok"] and not installed:
            add_finding(
                findings,
                area="npm",
                classification="unknown",
                name=f"npm.globals.{scope['scope']}",
                severity="low" if scope["scope"] == "current_process" else "medium",
                summary=f"npm global audit for {scope['scope']} did not produce package data.",
                details={
                    "scope": scope["scope"],
                    "trusted_for_canonical_drift": trusted,
                    "toolchain": scope["toolchain"],
                    "returncode": result["returncode"],
                    "stderr": result["stderr"][:500],
                    "args": scope["args"],
                    "js_toolchain_resolution": js_commands.get("npm"),
                },
            )
            continue

        if duplicate_with_pnpm:
            classification = "duplicate" if trusted else "unknown"
        elif legacy_globals:
            classification = "legacy" if trusted else "unknown"
        else:
            classification = "canonical" if trusted else "unknown"
        has_actionable_drift = bool(duplicate_with_pnpm or legacy_globals)

        add_finding(
            findings,
            area="npm",
            classification=classification,
            name=f"npm.globals.{scope['scope']}",
            severity="medium" if trusted and has_actionable_drift else "low",
            source=scope["scope"],
            summary=(
                f"{scope['scope']} npm reports {len(installed)} globals; "
                f"{len(duplicate_with_pnpm)} duplicate pnpm globals and "
                f"{len(legacy_globals)} other npm globals."
            ),
            details={
                "scope": scope["scope"],
                "trusted_for_canonical_drift": trusted,
                "installed": sorted(installed),
                "duplicate_with_pnpm": duplicate_with_pnpm,
                "legacy_packages": legacy_globals,
                "runtime_owned_packages": sorted(runtime_owned),
                "toolchain": scope["toolchain"],
                "returncode": result["returncode"],
                "stderr": result["stderr"][:400],
                "args": scope["args"],
                "js_toolchain_resolution": js_commands.get("npm") if scope["scope"] == "current_process" else None,
            },
            recommendation=(
                "Prefer the canonical pnpm global path; remove npm duplicates only after a Reset Approval Gate."
                if trusted and duplicate_with_pnpm
                else (
                    "Treat current-process npm as context only; do not use Codex/runtime npm for canonical drift."
                    if not trusted and current_process_codex
                    else None
                )
            ),
        )


def parse_fnm_inventory(fnm_list: str) -> dict[str, Any]:
    installed_versions: list[str] = []
    aliases: dict[str, list[str]] = {}
    system_node_present = False

    for raw in lines(fnm_list):
        line = raw.lstrip("* ").strip()
        if not line:
            continue

        version, _, alias_text = line.partition(" ")
        if version == "system":
            system_node_present = True
        else:
            installed_versions.append(version)
        if alias_text:
            names = [value.strip() for value in alias_text.split(",") if value.strip()]
            if names:
                aliases[version] = names

    return {
        "installed_versions": installed_versions,
        "aliases": aliases,
        "system_node_present": system_node_present,
    }


def check_fnm(findings: list[dict[str, Any]], brew_declared: dict[str, set[str]]) -> None:
    fnm_path = shutil.which("fnm")
    if not fnm_path:
        add_finding(
            findings,
            area="fnm",
            classification="declared_absent" if "fnm" in brew_declared["brew"] else "unknown",
            name="fnm.command",
            severity="medium",
            summary="fnm is not on PATH.",
            recommendation="Install through the canonical Homebrew path if Node runtime management is required.",
        )
        return

    provenance = path_provenance(fnm_path)
    source = provenance["source"]
    classification = "canonical" if source == "homebrew" and "fnm" in brew_declared["brew"] else "unknown"
    add_finding(
        findings,
        area="fnm",
        classification=classification,
        name="fnm.install_source",
        source=fnm_path,
        summary=f"fnm is present via {source}.",
        details=provenance,
        recommendation=(
            "Decide whether this fnm source should become canonical."
            if classification != "canonical"
            else None
        ),
    )

    list_result = command_result(["fnm", "list"])
    default_result = command_result(["fnm", "default"])
    current_result = command_result(["fnm", "current"])
    env_result = command_result(["fnm", "env", "--json"])
    env_json: dict[str, Any] = {}
    if env_result["stdout"]:
        try:
            env_json = json.loads(env_result["stdout"])
        except json.JSONDecodeError:
            env_json = {}

    inventory = parse_fnm_inventory(list_result["stdout"])
    fnm_dir = env_json.get("FNM_DIR")

    add_finding(
        findings,
        area="fnm",
        classification="canonical" if inventory["installed_versions"] else "unknown",
        name="fnm.inventory",
        source=fnm_path,
        summary=f"fnm reports {len(inventory['installed_versions'])} installed Node versions.",
        details={
            "installed_versions": inventory["installed_versions"],
            "aliases": inventory["aliases"],
            "default": default_result["stdout"] if default_result["ok"] else None,
            "current": current_result["stdout"] if current_result["ok"] else None,
            "system_node_present": inventory["system_node_present"],
            "fnm_dir": fnm_dir,
            "fnm_env": env_json,
        },
    )

    add_finding(
        findings,
        area="fnm",
        classification="canonical",
        name="fnm.current_process_visible",
        source=fnm_path,
        summary="fnm is visible from the doctor process PATH.",
        details={
            "path": fnm_path,
            "provenance": provenance,
            "scope": "current process PATH only; not a login-shell assertion",
        },
    )


def check_runtime_managers(findings: list[dict[str, Any]]) -> None:
    present: dict[str, dict[str, Any]] = {}
    absent: list[str] = []
    for name, spec in RUNTIME_MANAGERS.items():
        command_matches = []
        for command in spec["commands"]:
            command_matches.extend(which_all(command))
        path_matches = [str(path) for path in spec["paths"] if path.exists()]
        if command_matches or path_matches:
            present[name] = {
                "commands": sorted(set(command_matches)),
                "paths": path_matches,
                "classification": spec["classification"],
            }
        else:
            absent.append(name)

    declared_brew = parse_brewfile(BREWFILE)
    if "mise" in absent and equivalent_member("mise", declared_brew["brew"]):
        absent.remove("mise")
        add_finding(
            findings,
            area="runtime_managers",
            classification="migration_pending",
            name="runtime_managers.mise",
            severity="info",
            source=str(BREWFILE.relative_to(ROOT)),
            summary=(
                "mise is declared as the ADR-0006 .NET SDK owner, but no local "
                "mise command or data directory is visible yet."
            ),
            details={
                "brewfile_declares_mise": True,
                "repo_mise_config": mise_config_state(),
            },
            recommendation=(
                "Install the declared Homebrew mise formula and .NET SDKs only "
                "in a later approved mutation step."
            ),
        )

    if present:
        by_classification: dict[str, list[str]] = {}
        for name, info in present.items():
            by_classification.setdefault(info["classification"], []).append(name)
        for classification, names in sorted(by_classification.items()):
            is_canonical = classification == "canonical"
            add_finding(
                findings,
                area="runtime_managers",
                classification=classification,
                name=f"runtime_managers.{classification}",
                severity=(
                    "info"
                    if is_canonical
                    else "medium"
                    if classification == "legacy"
                    else "low"
                ),
                summary=(
                    "Canonical runtime manager signals detected: "
                    if is_canonical
                    else "Competing runtime manager signals detected: "
                )
                + f"{', '.join(sorted(names))}.",
                details={
                    manager: present[manager]
                    for manager in sorted(names)
                },
                recommendation=(
                    None
                    if is_canonical
                    else "Decide whether each manager is a Managed Exception or drift before cleanup."
                ),
            )
    else:
        add_finding(
            findings,
            area="runtime_managers",
            classification="canonical",
            name="runtime_managers.present",
            summary="No competing runtime manager signals were detected.",
        )

    add_finding(
        findings,
        area="runtime_managers",
        classification="canonical",
        name="runtime_managers.absent",
        summary=f"Runtime managers not detected: {', '.join(sorted(absent))}.",
        details={"absent": sorted(absent)},
    )


def parse_dotnet_tools(stdout: str) -> set[str]:
    return {row["package_id"] for row in parse_dotnet_tool_rows(stdout)}


def parse_dotnet_tool_rows(stdout: str) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for raw in stdout.splitlines():
        line = raw.strip()
        if not line or line.lower().startswith("package id") or set(line) <= {"-", " "}:
            continue
        parts = line.split()
        if len(parts) < 3:
            tools.append({"package_id": parts[0], "version": "", "commands": []})
            continue
        command_text = " ".join(parts[2:])
        tools.append(
            {
                "package_id": parts[0],
                "version": parts[1],
                "commands": [
                    command.strip().strip(",")
                    for command in command_text.split(",")
                    if command.strip()
                ],
            }
        )
    return tools


def dotnet_global_tool_path_state(commands: list[str]) -> dict[str, Any]:
    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    tool_dir = str(HOME / ".dotnet/tools")
    literal_tool_dir = "~/.dotnet/tools"
    command_paths = {command: shutil.which(command) for command in sorted(commands)}
    return {
        "command_paths": command_paths,
        "commands_available": {
            command: bool(path) for command, path in command_paths.items()
        },
        "exact_path_on_path": tool_dir in path_entries,
        "literal_tilde_path_on_path": literal_tool_dir in path_entries,
        "path": tool_dir,
        "path_exists": Path(tool_dir).exists(),
    }


def parse_dotnet_workloads(stdout: str) -> list[dict[str, str]]:
    workloads: list[dict[str, str]] = []
    for raw in stdout.splitlines():
        line = raw.strip()
        if (
            not line
            or line.startswith("Installed Workload Id")
            or line.startswith("Use `dotnet workload search`")
            or set(line) <= {"-", " "}
        ):
            continue
        parts = line.split()
        if len(parts) >= 3:
            workloads.append(
                {
                    "id": parts[0],
                    "manifest_version": parts[1],
                    "installation_source": " ".join(parts[2:]),
                }
            )
        else:
            workloads.append({"raw": line})
    return workloads


def summarize_command(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": result["ok"],
        "returncode": result["returncode"],
        "stderr": result["stderr"],
        "timed_out": result["timed_out"],
    }


def dotnet_inventory(dotnet_path: str) -> dict[str, Any]:
    sdk_result = command_result(
        [dotnet_path, "--list-sdks"],
        timeout=20,
        env=DOTNET_READ_ONLY_ENV,
    )
    runtime_result = command_result(
        [dotnet_path, "--list-runtimes"],
        timeout=20,
        env=DOTNET_READ_ONLY_ENV,
    )
    workload_result = command_result(
        [dotnet_path, "workload", "list"],
        timeout=30,
        env=DOTNET_READ_ONLY_ENV,
    )
    return {
        "path": dotnet_path,
        "provenance": path_provenance(dotnet_path),
        "sdks": lines(sdk_result["stdout"]),
        "runtimes": lines(runtime_result["stdout"]),
        "workloads": parse_dotnet_workloads(workload_result["stdout"]),
        "commands": {
            "list_sdks": summarize_command(sdk_result),
            "list_runtimes": summarize_command(runtime_result),
            "workload_list": summarize_command(workload_result),
        },
    }


def dotnet_candidate_paths(active_path: str) -> list[str]:
    candidates = [
        *which_all("dotnet"),
        str(HOME / ".local/share/mise/shims/dotnet"),
        str(HOME / ".local/share/mise/dotnet-root/dotnet"),
        "/opt/homebrew/opt/dotnet@8/bin/dotnet",
        "/opt/homebrew/opt/dotnet/bin/dotnet",
        "/usr/local/opt/dotnet@8/bin/dotnet",
        "/usr/local/opt/dotnet/bin/dotnet",
        "/usr/local/share/dotnet/dotnet",
        active_path,
    ]
    seen: set[str] = set()
    existing: list[str] = []
    for candidate in candidates:
        path = Path(candidate).expanduser()
        try:
            if not path.exists() or not os.access(path, os.X_OK):
                continue
            resolved = str(path.resolve())
        except OSError:
            continue
        key = f"{path}:{resolved}"
        if key in seen:
            continue
        seen.add(key)
        existing.append(str(path))
    return existing


def check_mise_dotnet_config(findings: list[dict[str, Any]]) -> None:
    state = mise_config_state()
    if not state["exists"]:
        add_finding(
            findings,
            area="dotnet",
            classification="declared_absent",
            name="dotnet.mise_config",
            severity="medium",
            source=str(MISE_CONFIG.relative_to(ROOT)),
            summary="Repo-managed mise .NET config is missing.",
            details=state,
            recommendation=(
                "Restore system/mise/config.toml with dotnet 10 default and "
                "dotnet 8 compatibility lines."
            ),
        )
        return

    has_policy = state["expected_versions_declared"] and not state["declares_node"]
    add_finding(
        findings,
        area="dotnet",
        classification="canonical" if has_policy else "unknown",
        name="dotnet.mise_config",
        severity="info" if has_policy else "medium",
        source=state["source"],
        summary=(
            "Repo-managed mise config declares .NET 10 and .NET 8 without taking Node ownership."
            if has_policy
            else "Repo-managed mise config does not match the ADR-0006 .NET policy."
        ),
        details=state,
        recommendation=(
            None
            if has_policy
            else "Keep Node under fnm and declare only the ADR-0006 .NET SDK lines in mise."
        ),
    )


def check_dotnet(findings: list[dict[str, Any]]) -> None:
    add_manifest_presence(findings, "dotnet", DOTNET_TOOLS, ".NET global tool")
    check_mise_dotnet_config(findings)
    declared = set(clean_manifest_lines(DOTNET_TOOLS))
    dotnet_path = shutil.which("dotnet")
    if not dotnet_path:
        config_declared = mise_config_declares_dotnet_policy()
        add_finding(
            findings,
            area="dotnet",
            classification="migration_pending" if config_declared else "unknown",
            name="dotnet.command",
            severity="info" if config_declared else "medium",
            summary=(
                "dotnet is not on PATH yet, but ADR-0006 mise .NET policy is declared."
                if config_declared
                else "dotnet is not on PATH; SDKs and global tools were not audited."
            ),
            details={"repo_mise_config": mise_config_state()},
            recommendation=(
                "Use the ADR-0006 mise .NET SDK source and dotnet tool manifest "
                "as desired state; install SDKs only in a later approved mutation step."
            ),
        )
        return

    provenance = path_provenance(dotnet_path)
    source = provenance["source"]
    active_inventory = dotnet_inventory(dotnet_path)
    sdk_lines = active_inventory["sdks"]
    active_source = "mise_dotnet" if source == "mise" else source
    if "dotnet@8" in str(Path(dotnet_path).resolve()):
        active_source = "homebrew-dotnet@8"
    config_declared = mise_config_declares_dotnet_policy()
    sdk_major_lines = sorted(
        {
            sdk.split()[0].split(".", 1)[0]
            for sdk in sdk_lines
            if sdk and sdk[0].isdigit()
        }
    )
    missing_sdk_major_lines = [
        line for line in DOTNET_POLICY_SDK_LINES if line not in sdk_major_lines
    ]
    expected_sdk_major_lines_visible = not missing_sdk_major_lines
    source_classification = (
        "canonical"
        if active_source == "mise_dotnet" and expected_sdk_major_lines_visible
        else "migration_pending"
        if config_declared
        else "unknown"
    )
    candidates = [
        dotnet_inventory(candidate)
        for candidate in dotnet_candidate_paths(dotnet_path)
    ]
    add_finding(
        findings,
        area="dotnet",
        classification=source_classification,
        name="dotnet.sdk_source",
        source=dotnet_path,
        severity="info" if source_classification == "canonical" else "low",
        summary=(
            "dotnet resolves through the ADR-0006 mise SDK owner with the expected SDK major lines."
            if active_source == "mise_dotnet" and expected_sdk_major_lines_visible
            else "dotnet resolves through the ADR-0006 mise SDK owner, but expected SDK major lines are not all visible."
            if active_source == "mise_dotnet"
            else f"dotnet is still present from {active_source}; ADR-0006 mise migration is declared but not active."
            if config_declared
            else f"dotnet is present from {active_source}."
        ),
        details={
            "active": active_inventory,
            "candidates": candidates,
            "expected_sdk_major_lines": DOTNET_POLICY_SDK_LINES,
            "installed_sdk_major_lines": sdk_major_lines,
            "missing_expected_sdk_major_lines": missing_sdk_major_lines,
            "repo_mise_config": mise_config_state(),
            "path_matches": [path_provenance(path) for path in which_all("dotnet")],
            "provenance": provenance,
            "runtimes": active_inventory["runtimes"],
            "sdks": sdk_lines,
            "workloads": active_inventory["workloads"],
        },
        recommendation=(
            "Keep existing SDK sources as managed exceptions until the ADR-0006 mise SDK lines are installed and active."
            if active_source != "mise_dotnet"
            else "Repair missing ADR-0006 mise SDK lines in a later approved mutation step."
            if not expected_sdk_major_lines_visible
            else None
        ),
    )

    legacy_sdk_candidates = [
        candidate
        for candidate in candidates
        if candidate["provenance"].get("source") in {"homebrew", "microsoft_dotnet_pkg"}
    ]
    if legacy_sdk_candidates:
        add_finding(
            findings,
            area="dotnet",
            classification="approval_gated_removal",
            name="dotnet.sdk_sources.legacy_present",
            severity="low",
            summary="Legacy .NET SDK source candidates are still present outside mise.",
            details={"candidates": legacy_sdk_candidates},
            recommendation=(
                "Remove legacy SDK roots only through an explicit cleanup task; "
                "root-owned Microsoft pkg files require interactive sudo."
            ),
        )
    else:
        add_finding(
            findings,
            area="dotnet",
            classification="canonical",
            name="dotnet.sdk_sources.legacy_present",
            summary="No legacy Homebrew or Microsoft pkg .NET SDK source candidates were detected.",
        )

    tool_result = command_result(
        ["dotnet", "tool", "list", "--global"],
        timeout=20,
        env=DOTNET_READ_ONLY_ENV,
    )
    tool_rows = parse_dotnet_tool_rows(tool_result["stdout"]) if tool_result["stdout"] else []
    installed = {row["package_id"] for row in tool_rows}
    tool_commands = sorted(
        {
            command
            for row in tool_rows
            for command in row.get("commands", [])
        }
    )
    tool_path_state = dotnet_global_tool_path_state(tool_commands)
    declared_lc = {value.lower(): value for value in declared}
    installed_lc = {value.lower(): value for value in installed}
    missing = sorted(declared_lc[key] for key in declared_lc.keys() - installed_lc.keys())
    undeclared = sorted(installed_lc[key] for key in installed_lc.keys() - declared_lc.keys())
    add_finding(
        findings,
        area="dotnet",
        classification="canonical" if not missing else "declared_absent",
        name="dotnet.global_tools.declared",
        severity="info" if not missing else "medium",
        source=str(DOTNET_TOOLS.relative_to(ROOT)),
        summary=f"{len(declared) - len(missing)}/{len(declared)} declared .NET global tools appear installed.",
        details={
            "installed": sorted(installed),
            "missing": missing,
            "tool_path": tool_path_state,
            "tools": tool_rows,
        },
        recommendation=(
            "A later install task can install missing declared .NET tools."
            if missing
            else None
        ),
    )
    unavailable_commands = sorted(
        command
        for command, available in tool_path_state["commands_available"].items()
        if not available
    )
    if installed and unavailable_commands:
        add_finding(
            findings,
            area="dotnet",
            classification="unknown",
            name="dotnet.global_tools.path",
            severity="medium",
            source=tool_path_state["path"],
            summary=(
                f"{len(unavailable_commands)} installed .NET global tool commands "
                "are not directly visible on PATH."
            ),
            details={
                "tool_path": tool_path_state,
                "unavailable_commands": unavailable_commands,
            },
            recommendation=(
                "Put the expanded ~/.dotnet/tools directory on PATH for every "
                "supported shell, not a literal tilde entry."
            ),
        )
    elif installed:
        add_finding(
            findings,
            area="dotnet",
            classification="canonical",
            name="dotnet.global_tools.path",
            source=tool_path_state["path"],
            summary=".NET global tool commands are directly visible on PATH.",
            details={"tool_path": tool_path_state},
        )
    if undeclared:
        add_finding(
            findings,
            area="dotnet",
            classification="present_undeclared",
            name="dotnet.global_tools.present_undeclared",
            severity="low",
            source=dotnet_path,
            summary=f"{len(undeclared)} .NET global tools are installed but undeclared.",
            details={"tools": undeclared},
            recommendation="Declare intentional .NET global tools or remove them behind a Reset Approval Gate.",
        )
    else:
        add_finding(
            findings,
            area="dotnet",
            classification="canonical",
            name="dotnet.global_tools.present_undeclared",
            source=dotnet_path,
            summary="No undeclared .NET global tools were detected.",
        )


def apm_manifest_state() -> dict[str, Any]:
    state: dict[str, Any] = {
        "path": str(APM_MANIFEST),
        "exists": APM_MANIFEST.exists(),
        "parser": yaml_parser_mode(),
        "parser_notes": yaml_parser_notes(),
        "parser_errors": [],
        "expected_targets": APM_BASELINE_TARGETS,
        "targets": [],
        "targets_codex": False,
        "targets_shared_harnesses": False,
        "target_set_exact": False,
        "unexpected_targets": [],
        "duplicate_targets": [],
        "dependency_sections": [],
        "unexpected_dependency_sections": [],
        "dependencies_apm_refs": [],
        "declares_grill_with_docs": False,
        "declares_public_dependency_set": False,
        "expected_refs": GRILL_WITH_DOCS_APM_REFS,
        "declared_expected_refs": [],
        "missing_expected_refs": GRILL_WITH_DOCS_APM_REFS,
        "unexpected_refs": [],
        "duplicate_refs": [],
        "declares_using_superpowers": False,
        "canonical": False,
    }
    if not APM_MANIFEST.exists():
        return state

    text = APM_MANIFEST.read_text(encoding="utf-8")
    uncommented = "\n".join(simple_yaml_content_lines(text))
    parsed = parse_manifest_values(APM_MANIFEST, text)
    targets = parsed["targets"]
    apm_refs = parsed["apm_refs"]
    dependency_sections = parsed["dependency_sections"]

    state["parser_errors"] = parsed["parser_errors"]
    state["targets"] = targets
    state["targets_codex"] = "codex" in targets
    state["targets_shared_harnesses"] = values_match_exactly(
        targets, APM_BASELINE_TARGETS
    )
    state["target_set_exact"] = values_match_exactly(targets, APM_BASELINE_TARGETS)
    state["unexpected_targets"] = unexpected_values(targets, APM_BASELINE_TARGETS)
    state["duplicate_targets"] = duplicate_values(targets)
    state["dependency_sections"] = dependency_sections
    state["unexpected_dependency_sections"] = unexpected_values(
        dependency_sections, ["apm"]
    )
    state["dependencies_apm_refs"] = apm_refs
    state["declares_grill_with_docs"] = GRILL_WITH_DOCS_REF in apm_refs
    declared_refs = [ref for ref in GRILL_WITH_DOCS_APM_REFS if ref in apm_refs]
    state["declared_expected_refs"] = declared_refs
    state["missing_expected_refs"] = missing_expected_values(
        apm_refs, GRILL_WITH_DOCS_APM_REFS
    )
    state["unexpected_refs"] = unexpected_values(apm_refs, GRILL_WITH_DOCS_APM_REFS)
    state["duplicate_refs"] = duplicate_values(apm_refs)
    state["declares_public_dependency_set"] = values_match_exactly(
        apm_refs, GRILL_WITH_DOCS_APM_REFS
    )
    state["declares_using_superpowers"] = "using-superpowers" in uncommented
    state["canonical"] = bool(
        not state["parser_errors"]
        and state["target_set_exact"]
        and not state["unexpected_dependency_sections"]
        and state["declares_public_dependency_set"]
        and not state["declares_using_superpowers"]
    )
    return state


def apm_lockfile_state() -> dict[str, Any]:
    state: dict[str, Any] = {
        "path": str(APM_LOCKFILE),
        "exists": APM_LOCKFILE.exists(),
        "parser": yaml_parser_mode(),
        "parser_notes": yaml_parser_notes(),
        "parser_errors": [],
        "dependency_count": 0,
        "dependency_summaries": [],
        "pins_grill_with_docs": False,
        "pins_public_dependency_set": False,
        "expected_virtual_paths": GRILL_WITH_DOCS_VIRTUAL_PATHS,
        "pinned_virtual_paths": [],
        "missing_virtual_paths": GRILL_WITH_DOCS_VIRTUAL_PATHS,
        "unexpected_virtual_paths": [],
        "duplicate_virtual_paths": [],
        "virtual_paths_exact": False,
        "expected_repo_url": GRILL_WITH_DOCS_REPO_URL,
        "repo_urls": [],
        "unexpected_repo_urls": [],
        "expected_host": GRILL_WITH_DOCS_HOST,
        "hosts": [],
        "unexpected_hosts": [],
        "dependencies_from_expected_repo": False,
        "dependencies_are_virtual": False,
        "dependencies_resolved_to_expected_commit": False,
        "dependencies_resolved_to_expected_ref": False,
        "unexpected_dependencies": [],
        "resolved_commit": None,
        "resolved_commits": [],
        "expected_resolved_commit": GRILL_WITH_DOCS_COMMIT,
        "resolved_ref": None,
        "resolved_refs": [],
        "expected_resolved_ref": GRILL_WITH_DOCS_RESOLVED_REF,
        "package_type": None,
        "package_types": [],
        "mentions_using_superpowers": False,
        "canonical": False,
    }
    if not APM_LOCKFILE.exists():
        return state

    text = APM_LOCKFILE.read_text(encoding="utf-8")
    dependencies, parser_errors = parse_lockfile_dependencies(APM_LOCKFILE, text)
    state["parser_errors"] = parser_errors
    state["dependency_count"] = len(dependencies)
    dependency_summaries = [
        {
            "repo_url": yamlish_string(dependency.get("repo_url")),
            "host": yamlish_string(dependency.get("host")),
            "resolved_commit": yamlish_string(dependency.get("resolved_commit")),
            "resolved_ref": yamlish_string(dependency.get("resolved_ref")),
            "virtual_path": yamlish_string(dependency.get("virtual_path")),
            "is_virtual": yamlish_string(dependency.get("is_virtual")),
            "package_type": yamlish_string(dependency.get("package_type")),
        }
        for dependency in dependencies
    ]
    state["dependency_summaries"] = dependency_summaries

    pinned_virtual_paths = [
        summary["virtual_path"]
        for summary in dependency_summaries
        if summary["virtual_path"] is not None
    ]
    state["pins_grill_with_docs"] = "skills/engineering/grill-with-docs" in pinned_virtual_paths
    state["pinned_virtual_paths"] = pinned_virtual_paths
    state["missing_virtual_paths"] = missing_expected_values(
        pinned_virtual_paths, GRILL_WITH_DOCS_VIRTUAL_PATHS
    )
    state["unexpected_virtual_paths"] = unexpected_values(
        pinned_virtual_paths, GRILL_WITH_DOCS_VIRTUAL_PATHS
    )
    state["duplicate_virtual_paths"] = duplicate_values(pinned_virtual_paths)
    state["virtual_paths_exact"] = values_match_exactly(
        pinned_virtual_paths, GRILL_WITH_DOCS_VIRTUAL_PATHS
    )
    state["pins_public_dependency_set"] = state["virtual_paths_exact"]
    state["mentions_using_superpowers"] = "using-superpowers" in text

    commits = sorted(
        set(
            value
            for value in (
                summary["resolved_commit"] for summary in dependency_summaries
            )
            if value
        )
    )
    state["resolved_commits"] = commits
    if commits:
        state["resolved_commit"] = commits[0]

    refs = sorted(
        set(
            value
            for value in (summary["resolved_ref"] for summary in dependency_summaries)
            if value
        )
    )
    state["resolved_refs"] = refs
    if refs:
        state["resolved_ref"] = refs[0]

    package_types = sorted(
        set(
            value
            for value in (summary["package_type"] for summary in dependency_summaries)
            if value
        )
    )
    state["package_types"] = package_types
    if package_types:
        state["package_type"] = package_types[0]

    repo_urls = sorted(
        set(
            value
            for value in (summary["repo_url"] for summary in dependency_summaries)
            if value
        )
    )
    hosts = sorted(
        set(value for value in (summary["host"] for summary in dependency_summaries) if value)
    )
    state["repo_urls"] = repo_urls
    state["unexpected_repo_urls"] = unexpected_values(repo_urls, [GRILL_WITH_DOCS_REPO_URL])
    state["hosts"] = hosts
    state["unexpected_hosts"] = unexpected_values(hosts, [GRILL_WITH_DOCS_HOST])

    expected_dependency_count = len(GRILL_WITH_DOCS_VIRTUAL_PATHS)
    state["dependencies_from_expected_repo"] = bool(
        len(dependency_summaries) == expected_dependency_count
        and all(
            summary["repo_url"] == GRILL_WITH_DOCS_REPO_URL
            and summary["host"] == GRILL_WITH_DOCS_HOST
            for summary in dependency_summaries
        )
    )
    state["dependencies_are_virtual"] = bool(
        len(dependency_summaries) == expected_dependency_count
        and all(summary["is_virtual"] == "true" for summary in dependency_summaries)
    )
    state["dependencies_resolved_to_expected_commit"] = bool(
        len(dependency_summaries) == expected_dependency_count
        and all(
            summary["resolved_commit"] == GRILL_WITH_DOCS_COMMIT
            for summary in dependency_summaries
        )
    )
    state["dependencies_resolved_to_expected_ref"] = bool(
        len(dependency_summaries) == expected_dependency_count
        and all(
            summary["resolved_ref"] == GRILL_WITH_DOCS_RESOLVED_REF
            for summary in dependency_summaries
        )
    )
    state["unexpected_dependencies"] = [
        summary
        for summary in dependency_summaries
        if summary["virtual_path"] not in GRILL_WITH_DOCS_VIRTUAL_PATHS
        or summary["repo_url"] != GRILL_WITH_DOCS_REPO_URL
        or summary["host"] != GRILL_WITH_DOCS_HOST
    ]
    state["canonical"] = bool(
        not state["parser_errors"]
        and state["virtual_paths_exact"]
        and state["dependencies_from_expected_repo"]
        and state["dependencies_are_virtual"]
        and state["dependencies_resolved_to_expected_commit"]
        and state["dependencies_resolved_to_expected_ref"]
        and not state["mentions_using_superpowers"]
        and not state["unexpected_dependencies"]
    )

    return state


def path_exists_or_symlink(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def split_skill_baseline_state(
    skills_dir: Path,
    allowed_vendor_runtime_skills: list[str] | None = None,
) -> dict[str, Any]:
    if allowed_vendor_runtime_skills is None:
        allowed_vendor_runtime_skills = []
    baseline_skill_set = set(CODEX_BASELINE_SKILLS)
    allowed_vendor_runtime_set = set(allowed_vendor_runtime_skills)
    state: dict[str, Any] = {
        "path": str(skills_dir),
        "exists": skills_dir.is_dir(),
        "skill_names": [],
        "baseline_skill_roots": CODEX_BASELINE_SKILLS,
        "allowed_vendor_runtime_skills": allowed_vendor_runtime_skills,
        "present_allowed_vendor_runtime_skills": [],
        "expected_files": CODEX_SPLIT_BASELINE_FILES,
        "present_files": [],
        "missing_files": CODEX_SPLIT_BASELINE_FILES,
        "expected_stale_absent_files": CODEX_STALE_BASELINE_FILES,
        "stale_files": [],
        "observed_baseline_files": [],
        "unexpected_baseline_files": [],
        "extra_non_vendor_skills": [],
        "excluded_skills": sorted(EXCLUDED_AI_ASSETS),
        "excluded_present": [],
        "scan_errors": [],
        "canonical": False,
    }
    if not skills_dir.is_dir():
        return state

    names: list[str] = []
    try:
        for item in skills_dir.iterdir():
            if item.is_dir():
                names.append(item.name)
    except OSError as exc:
        state["scan_errors"].append(f"{type(exc).__name__}: {exc}")
        return state

    names = sorted(set(names))
    name_set = set(names)
    state["skill_names"] = names
    state["present_allowed_vendor_runtime_skills"] = [
        name for name in allowed_vendor_runtime_skills if name in name_set
    ]
    state["extra_non_vendor_skills"] = sorted(
        name
        for name in name_set
        if name not in baseline_skill_set
        and name not in allowed_vendor_runtime_set
        and name not in EXCLUDED_AI_ASSETS
    )
    state["excluded_present"] = sorted(EXCLUDED_AI_ASSETS.intersection(names))

    present_files: list[str] = []
    missing_files: list[str] = []
    for relative_path in CODEX_SPLIT_BASELINE_FILES:
        path = skills_dir / relative_path
        if path.is_file():
            present_files.append(relative_path)
        else:
            missing_files.append(relative_path)

    stale_files = [
        relative_path
        for relative_path in CODEX_STALE_BASELINE_FILES
        if path_exists_or_symlink(skills_dir / relative_path)
    ]

    observed_baseline_files: set[str] = set()
    for skill_name in CODEX_BASELINE_SKILLS:
        skill_dir = skills_dir / skill_name
        if not skill_dir.is_dir():
            continue
        try:
            for item in skill_dir.rglob("*"):
                if item.is_file() or item.is_symlink():
                    observed_baseline_files.add(str(item.relative_to(skills_dir)))
        except OSError as exc:
            state["scan_errors"].append(
                f"{skill_name}: {type(exc).__name__}: {exc}"
            )

    expected_or_stale = set(CODEX_SPLIT_BASELINE_FILES).union(
        CODEX_STALE_BASELINE_FILES
    )
    state["present_files"] = present_files
    state["missing_files"] = missing_files
    state["stale_files"] = stale_files
    state["observed_baseline_files"] = sorted(observed_baseline_files)
    state["unexpected_baseline_files"] = sorted(
        path for path in observed_baseline_files if path not in expected_or_stale
    )
    state["canonical"] = bool(
        not state["scan_errors"]
        and not missing_files
        and not stale_files
        and not state["excluded_present"]
        and not state["unexpected_baseline_files"]
    )
    return state


def codex_split_baseline_state() -> dict[str, Any]:
    return split_skill_baseline_state(
        CODEX_SKILLS_DIR,
        allowed_vendor_runtime_skills=CODEX_ALLOWED_VENDOR_RUNTIME_SKILLS,
    )


def claude_split_baseline_state() -> dict[str, Any]:
    return split_skill_baseline_state(CLAUDE_SKILLS_DIR)


def opencode_split_baseline_state() -> dict[str, Any]:
    return split_skill_baseline_state(OPENCODE_SKILLS_DIR)


def claude_code_state() -> dict[str, Any]:
    paths = which_all("claude")
    primary_path = paths[0] if paths else None
    primary_provenance = path_provenance(primary_path)
    declared = parse_brewfile(BREWFILE)
    declared_casks = declared["cask"]
    installed_casks: set[str] = set()
    cask_result = command_result(["brew", "list", "--cask"]) if shutil.which("brew") else None
    if cask_result and cask_result["ok"]:
        installed_casks = set(lines(cask_result["stdout"]))
    claude_code_declared = "claude-code" in declared_casks
    claude_code_latest_declared = "claude-code@latest" in declared_casks
    claude_desktop_declared = "claude" in declared_casks
    claude_code_cask_installed = equivalent_member("claude-code", installed_casks)
    claude_code_latest_cask_installed = equivalent_member(
        "claude-code@latest", installed_casks
    )
    claude_desktop_cask_installed = equivalent_member("claude", installed_casks)
    state: dict[str, Any] = {
        "expected_command": str(CLAUDE_COMMAND),
        "target_casks": {
            "cli_stable": "claude-code",
            "cli_latest": "claude-code@latest",
            "desktop": "claude",
        },
        "declared_casks": {
            "cli_stable": claude_code_declared,
            "cli_latest": claude_code_latest_declared,
            "desktop": claude_desktop_declared,
        },
        "installed_casks": {
            "cli_stable": claude_code_cask_installed,
            "cli_latest": claude_code_latest_cask_installed,
            "desktop": claude_desktop_cask_installed,
        },
        "paths": [path_provenance(path) for path in paths],
        "active_command_present": bool(primary_path),
        "active_command": primary_provenance,
        "homebrew_cli_active": primary_provenance.get("source") == "homebrew",
        "manual_local": primary_provenance.get("source") == "manual/local",
        "install_source": primary_provenance.get("source", "absent"),
        "installer_discoverable_from_metadata": bool(
            primary_provenance.get("source") == "homebrew"
        ),
        "command_symlink": {
            "path": str(CLAUDE_COMMAND),
            "path_present": path_exists_or_symlink(CLAUDE_COMMAND),
            "is_symlink": CLAUDE_COMMAND.is_symlink(),
            "link_target": None,
            "resolved_path": None,
        },
        "versions_path": str(CLAUDE_VERSIONS_DIR),
        "versions_path_present": CLAUDE_VERSIONS_DIR.is_dir(),
        "versioned_artifacts": [],
        "active_version": None,
        "old_versions": [],
        "desktop_app": {
            "path": str(CLAUDE_DESKTOP_APP),
            "present": CLAUDE_DESKTOP_APP.is_dir(),
            "homebrew_cask_installed": claude_desktop_cask_installed,
            "declared_cask": claude_desktop_declared,
            "bundle_identifier": None,
            "version": None,
        },
        "classification": "migration_pending",
        "scan_errors": [],
    }

    info_plist = CLAUDE_DESKTOP_APP / "Contents/Info.plist"
    if info_plist.is_file():
        try:
            with info_plist.open("rb") as handle:
                plist = plistlib.load(handle)
            state["desktop_app"]["bundle_identifier"] = plist.get("CFBundleIdentifier")
            state["desktop_app"]["version"] = (
                plist.get("CFBundleShortVersionString")
                or plist.get("CFBundleVersion")
            )
        except (OSError, plistlib.InvalidFileException) as exc:
            state["scan_errors"].append(
                f"claude desktop plist: {type(exc).__name__}: {exc}"
            )

    if CLAUDE_COMMAND.is_symlink():
        try:
            state["command_symlink"]["link_target"] = os.readlink(CLAUDE_COMMAND)
        except OSError as exc:
            state["scan_errors"].append(
                f"claude command symlink: {type(exc).__name__}: {exc}"
            )

    if path_exists_or_symlink(CLAUDE_COMMAND):
        try:
            active_resolved_path = CLAUDE_COMMAND.resolve(strict=False)
            state["command_symlink"]["resolved_path"] = str(active_resolved_path)
            if active_resolved_path.parent == CLAUDE_VERSIONS_DIR:
                state["active_version"] = active_resolved_path.name
        except OSError as exc:
            state["scan_errors"].append(
                f"claude command resolve: {type(exc).__name__}: {exc}"
            )

    versioned_artifacts: list[dict[str, Any]] = []
    if CLAUDE_VERSIONS_DIR.is_dir():
        try:
            for item in CLAUDE_VERSIONS_DIR.iterdir():
                if item.name.startswith("."):
                    continue
                if item.is_symlink():
                    kind = "symlink"
                elif item.is_dir():
                    kind = "directory"
                elif item.is_file():
                    kind = "file"
                else:
                    continue
                versioned_artifacts.append(
                    {
                        "name": item.name,
                        "path": str(item),
                        "kind": kind,
                        "executable": os.access(item, os.X_OK),
                    }
                )
        except OSError as exc:
            state["scan_errors"].append(
                f"claude versions: {type(exc).__name__}: {exc}"
            )

    versioned_artifacts = sorted(
        versioned_artifacts, key=lambda artifact: str(artifact["name"])
    )
    state["versioned_artifacts"] = versioned_artifacts
    if state["active_version"]:
        state["old_versions"] = [
            str(artifact["name"])
            for artifact in versioned_artifacts
            if artifact["name"] != state["active_version"]
        ]
    return state


def apm_user_project_state() -> dict[str, Any]:
    files = {
        "apm.yml": symlink_file_state(APM_USER_MANIFEST, APM_MANIFEST),
        "apm.lock.yaml": symlink_file_state(APM_USER_LOCKFILE, APM_LOCKFILE),
    }
    missing = sorted(
        name for name, info in files.items() if not info["path_present"]
    )
    noncanonical = sorted(
        name
        for name, info in files.items()
        if info["path_present"] and not info["canonical"]
    )
    return {
        "path": str(HOME / ".apm"),
        "files": files,
        "missing": missing,
        "noncanonical": noncanonical,
        "canonical": not missing and not noncanonical,
    }


def symlink_file_state(path: Path, expected_target: Path) -> dict[str, Any]:
    state: dict[str, Any] = {
        "path": str(path),
        "path_present": path_exists_or_symlink(path),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_symlink": path.is_symlink(),
        "link_target": None,
        "resolved_path": None,
        "expected_target": str(expected_target),
        "points_to_expected_target": False,
        "canonical": False,
    }
    if path.is_symlink():
        try:
            state["link_target"] = os.readlink(path)
        except OSError:
            pass
        try:
            resolved_path = path.resolve(strict=False)
            state["resolved_path"] = str(resolved_path)
            state["points_to_expected_target"] = (
                resolved_path == expected_target.resolve(strict=False)
            )
        except OSError:
            pass

    state["canonical"] = bool(
        state["is_symlink"] and state["points_to_expected_target"]
    )
    return state


def scan_ai_baseline(findings: list[dict[str, Any]]) -> None:
    manifest = apm_manifest_state()
    lockfile = apm_lockfile_state()
    apm_user_project = apm_user_project_state()
    codex_baseline = codex_split_baseline_state()

    if not manifest["exists"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="missing",
            name="ai_tools.apm_manifest",
            severity="high",
            summary="APM is selected, but the repo APM manifest is missing.",
            details=manifest,
            recommendation="Restore system/ai/apm/apm.yml with the approved Global AI Baseline.",
        )
    elif manifest["canonical"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="ai_tools.apm_manifest",
            summary="Repo APM manifest declares the intended public grill-with-docs dependency set.",
            details=manifest,
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="drift",
            name="ai_tools.apm_manifest",
            severity="high",
            summary="APM manifest does not match the approved shared harness grill-with-docs dependency set.",
            details=manifest,
            recommendation="Keep targets pinned to codex, claude, and opencode, and declare the approved public grill-with-docs dependency set only.",
        )

    if manifest["declares_using_superpowers"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="drift",
            name="ai_tools.apm_manifest.excluded_assets",
            severity="medium",
            summary="APM manifest declares using-superpowers, which is intentionally excluded from the baseline.",
            details=manifest,
            recommendation="Remove using-superpowers from the APM baseline unless ADR-0003 is changed.",
        )

    if not lockfile["exists"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="missing",
            name="ai_tools.apm_lockfile",
            severity="medium",
            summary="APM manifest exists, but apm.lock.yaml is missing.",
            details=lockfile,
            recommendation="Create the lockfile only through an approved APM lock gate.",
        )
    elif lockfile["canonical"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="ai_tools.apm_lockfile",
            summary="APM lockfile pins the approved public grill-with-docs dependency evidence.",
            details=lockfile,
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="drift",
            name="ai_tools.apm_lockfile",
            severity="high",
            summary="APM lockfile does not match the approved grill-with-docs dependency set.",
            details=lockfile,
            recommendation="Review apm.lock.yaml before any install or deploy command.",
        )

    if apm_user_project["canonical"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="ai_tools.apm_user_project",
            summary="Live APM project files are symlinked to the repo manifest and lockfile.",
            details=apm_user_project,
        )
    elif apm_user_project["noncanonical"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="drift",
            name="ai_tools.apm_user_project",
            severity="medium",
            summary="Live APM project files exist but are not symlinked to the repo source files.",
            details=apm_user_project,
            recommendation=(
                "Run the normal dotfiles symlink setup after approval; it will back up "
                "existing ~/.apm/apm.yml or ~/.apm/apm.lock.yaml before replacing them."
            ),
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="migration_pending",
            name="ai_tools.apm_user_project",
            severity="low",
            summary="Live APM project files are not linked to the repo manifest and lockfile yet.",
            details=apm_user_project,
            recommendation=(
                "Run the normal dotfiles symlink setup when live ~/.apm project files "
                "should consume the repo source of truth."
            ),
        )

    if not codex_baseline["exists"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="missing",
            name="ai_tools.codex_baseline",
            severity="medium",
            summary="Codex global skills directory is missing.",
            details=codex_baseline,
            recommendation=(
                "Restore the approved APM-managed Codex split baseline through a "
                "separate target-write gate."
            ),
        )
    elif codex_baseline["canonical"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="ai_tools.codex_baseline",
            summary="Codex has the approved APM-managed split skill baseline.",
            details=codex_baseline,
        )
    else:
        classification = "missing" if codex_baseline["missing_files"] else "drift"
        add_finding(
            findings,
            area="ai_tools",
            classification=classification,
            name="ai_tools.codex_baseline",
            severity="medium",
            summary="Codex live skills do not match the approved split baseline.",
            details=codex_baseline,
            recommendation=(
                "Review the live Codex target output against the APM manifest and "
                "use a separate approved deployment or cleanup gate for changes."
            ),
        )

    if codex_baseline["extra_non_vendor_skills"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="drift",
            name="ai_tools.codex_extra_skills",
            severity="medium",
            summary="Codex has non-vendor skills outside the approved APM baseline.",
            details={
                "path": codex_baseline["path"],
                "baseline_skill_roots": codex_baseline["baseline_skill_roots"],
                "allowed_vendor_runtime_skills": codex_baseline[
                    "allowed_vendor_runtime_skills"
                ],
                "extra_non_vendor_skills": codex_baseline[
                    "extra_non_vendor_skills"
                ],
            },
            recommendation=(
                "Declare intentional shared skills through APM or remove undeclared "
                "local skills through a separate cleanup gate."
            ),
        )

    if codex_baseline["excluded_present"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="drift",
            name="ai_tools.codex_excluded_assets",
            severity="medium",
            summary="Codex has skills that are explicitly excluded from the Global AI Baseline.",
            details={
                "path": codex_baseline["path"],
                "excluded_present": codex_baseline["excluded_present"],
            },
            recommendation=(
                "Remove excluded local skills only through a separate approved cleanup task."
            ),
        )


def scan_claude_code(findings: list[dict[str, Any]]) -> None:
    state = claude_code_state()
    claude_baseline = claude_split_baseline_state()
    command_details = {
        "expected_command": state["expected_command"],
        "target_casks": state["target_casks"],
        "declared_casks": state["declared_casks"],
        "installed_casks": state["installed_casks"],
        "paths": state["paths"],
        "active_command": state["active_command"],
        "command_symlink": state["command_symlink"],
        "active_version": state["active_version"],
        "install_source": state["install_source"],
        "homebrew_cli_active": state["homebrew_cli_active"],
        "manual_local": state["manual_local"],
        "installer_discoverable_from_metadata": state[
            "installer_discoverable_from_metadata"
        ],
        "scan_errors": state["scan_errors"],
    }
    if state["active_command_present"] and state["homebrew_cli_active"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="claude.command",
            summary="Claude Code active CLI resolves through the declared Homebrew cask.",
            details=command_details,
        )
    elif state["active_command_present"] and state["declared_casks"]["cli_stable"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="migration_pending",
            name="claude.command",
            severity="low",
            summary="Claude Code is declared in the Brewfile, but the active CLI is still manual-local.",
            details=command_details,
            recommendation=(
                "Migrate Claude Code to the stable Homebrew cask in a separate "
                "approved reinstall task; do not mutate live Claude state from doctor."
            ),
        )
    elif state["active_command_present"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="managed_exception",
            name="claude.command",
            severity="low",
            summary="Claude Code active CLI is present, but no repo-owned installer is declared.",
            details=command_details,
            recommendation="Declare a Claude Code installer before cleanup or migration.",
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification=(
                "declared_absent" if state["declared_casks"]["cli_stable"] else "missing"
            ),
            name="claude.command",
            severity="low",
            summary="Claude Code active CLI is not present on PATH.",
            details=command_details,
            recommendation="Install Claude Code only through a separate approved Homebrew task.",
        )

    if state["desktop_app"]["homebrew_cask_installed"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="claude.desktop",
            summary="Claude Desktop is installed through the declared Homebrew cask.",
            details=state["desktop_app"],
        )
    elif state["desktop_app"]["present"] and state["desktop_app"]["declared_cask"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="migration_pending",
            name="claude.desktop",
            severity="low",
            summary="Claude Desktop is declared in the Brewfile, but the live app is not Homebrew-owned yet.",
            details=state["desktop_app"],
            recommendation=(
                "Migrate Claude Desktop to the Homebrew cask in a separate approved "
                "reinstall task; do not remove sensitive ~/.claude state."
            ),
        )
    elif state["desktop_app"]["present"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="managed_exception",
            name="claude.desktop",
            severity="low",
            summary="Claude Desktop is present outside a repo-owned installer.",
            details=state["desktop_app"],
            recommendation="Declare or remove Claude Desktop only through a separate approved task.",
        )
    elif state["desktop_app"]["declared_cask"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="declared_absent",
            name="claude.desktop",
            severity="low",
            summary="Claude Desktop is declared in the Brewfile but is not installed.",
            details=state["desktop_app"],
            recommendation="Install Claude Desktop only through a separate approved Homebrew task.",
        )

    old_version_artifacts = [
        artifact
        for artifact in state["versioned_artifacts"]
        if artifact["name"] in state["old_versions"]
    ]
    if state["old_versions"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="approval_gated_removal",
            name="claude.versions.cleanup_candidates",
            severity="low",
            summary="Older Claude Code versioned executable artifacts are present.",
            details={
                "versions_path": state["versions_path"],
                "active_version": state["active_version"],
                "old_versions": state["old_versions"],
                "old_version_artifacts": old_version_artifacts,
                "scan_errors": state["scan_errors"],
            },
            recommendation=(
                "Remove older Claude Code artifacts only in a separate cleanup task "
                "with explicit approval."
            ),
        )

    claude_baseline_details = {
        "target": "claude",
        "baseline_required": True,
        "target_declared": "claude" in APM_BASELINE_TARGETS,
        "expected_skills": CODEX_BASELINE_SKILLS,
        "excluded_assets": sorted(EXCLUDED_AI_ASSETS),
        "baseline": claude_baseline,
    }
    if not claude_baseline["exists"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="migration_pending",
            name="claude.apm_baseline",
            severity="low",
            summary="Claude is part of the shared APM baseline target set, but live Claude target output is not deployed yet.",
            details=claude_baseline_details,
            recommendation=(
                "Preview and deploy Claude target output only through a separate "
                "approved APM target-write gate."
            ),
        )
    elif claude_baseline["canonical"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="claude.apm_baseline",
            summary="Claude has the approved APM-managed split skill baseline.",
            details=claude_baseline_details,
        )
    else:
        classification = "missing" if claude_baseline["missing_files"] else "drift"
        add_finding(
            findings,
            area="ai_tools",
            classification=classification,
            name="claude.apm_baseline",
            severity="medium",
            summary="Claude live skills do not match the approved split baseline.",
            details=claude_baseline_details,
            recommendation=(
                "Review the live Claude target output against the APM manifest and "
                "use a separate approved deployment or cleanup gate for changes."
            ),
        )


def scan_opencode_baseline(findings: list[dict[str, Any]]) -> None:
    opencode_baseline = opencode_split_baseline_state()
    details = {
        "target": "opencode",
        "baseline_required": True,
        "target_declared": "opencode" in APM_BASELINE_TARGETS,
        "expected_skills": CODEX_BASELINE_SKILLS,
        "excluded_assets": sorted(EXCLUDED_AI_ASSETS),
        "skills_path": str(OPENCODE_SKILLS_DIR),
        "sensitive_local_state_excluded": [
            str(HOME / ".config/opencode/opencode.json"),
            str(HOME / ".config/opencode/ai-gateway-sigv4-wrapper"),
            str(HOME / ".local/share/opencode"),
        ],
        "baseline": opencode_baseline,
    }
    if not opencode_baseline["exists"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="migration_pending",
            name="opencode.apm_baseline",
            severity="low",
            summary="opencode is part of the shared APM baseline target set, but live opencode target output is not deployed yet.",
            details=details,
            recommendation=(
                "Preview and deploy opencode target output only through a separate "
                "approved APM target-write gate."
            ),
        )
    elif opencode_baseline["canonical"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="opencode.apm_baseline",
            summary="opencode has the approved APM-managed split skill baseline.",
            details=details,
        )
    else:
        classification = "missing" if opencode_baseline["missing_files"] else "drift"
        add_finding(
            findings,
            area="ai_tools",
            classification=classification,
            name="opencode.apm_baseline",
            severity="medium",
            summary="opencode live skills do not match the approved split baseline.",
            details=details,
            recommendation=(
                "Review the live opencode target output against the APM manifest "
                "and use a separate approved deployment or cleanup gate for changes."
            ),
        )


def scan_opencode_command(
    findings: list[dict[str, Any]], brew_declared: dict[str, set[str]]
) -> None:
    active = shutil.which("opencode")
    homebrew = homebrew_candidate("opencode")
    paths = which_all("opencode")
    declared = equivalent_member("anomalyco/tap/opencode", brew_declared["brew"])
    npm_or_fnm_paths = [
        path
        for path in paths
        if path_source(path) in {"fnm", "npm"}
    ]
    version_path = active or homebrew
    version_result = (
        command_result([version_path, "--version"], timeout=10)
        if version_path
        else {"ok": False, "stdout": "", "stderr": "", "returncode": None}
    )
    details = {
        "expected_formula": "anomalyco/tap/opencode",
        "declared_formula": declared,
        "active_command": path_provenance(active),
        "homebrew_candidate": path_provenance(homebrew),
        "path_matches": [path_provenance(path) for path in paths],
        "npm_or_fnm_paths": [path_provenance(path) for path in npm_or_fnm_paths],
        "version": version_result["stdout"].splitlines()[0]
        if version_result["stdout"]
        else None,
        "version_returncode": version_result["returncode"],
        "version_stderr": version_result["stderr"][:300],
    }

    if active and path_source(active) == "homebrew" and declared and not npm_or_fnm_paths:
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="opencode.command",
            summary="opencode active CLI resolves through the declared upstream Homebrew tap.",
            details=details,
        )
    elif homebrew and declared:
        add_finding(
            findings,
            area="ai_tools",
            classification="migration_pending",
            name="opencode.command",
            severity="low",
            summary="opencode is declared and installed through Homebrew, but PATH still exposes a different command first.",
            details=details,
            recommendation="Remove or demote shadowing opencode commands before treating the CLI as canonical.",
        )
    elif active:
        add_finding(
            findings,
            area="ai_tools",
            classification="managed_exception",
            name="opencode.command",
            severity="low",
            summary="opencode active CLI is present, but no canonical Homebrew tap declaration is active.",
            details=details,
            recommendation="Declare the selected opencode installer or migrate the CLI behind an approved cleanup task.",
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="declared_absent" if declared else "missing",
            name="opencode.command",
            severity="low",
            summary="opencode CLI is not present on PATH.",
            details=details,
            recommendation="Install opencode through the declared upstream Homebrew tap if it remains part of the AI Tool Surface baseline.",
        )


def scan_pi_command(findings: list[dict[str, Any]], pnpm_installed: set[str]) -> None:
    declared_packages = set(clean_manifest_lines(PNPM_GLOBAL))
    expected_packages = set(PI_PNPM_PACKAGES)
    missing_declared = sorted(expected_packages - declared_packages)
    missing_installed = sorted(expected_packages - pnpm_installed)
    command_paths = {
        command: [path_provenance(path) for path in which_all(command)]
        for command in PI_EXPECTED_COMMANDS
    }
    missing_commands = [
        command for command, paths in command_paths.items() if not paths
    ]
    active = shutil.which("pi")
    version_result = (
        command_result([active, "--version"], timeout=10)
        if active
        else {"ok": False, "stdout": "", "stderr": "", "returncode": None}
    )
    details = {
        "package_manifest": str(PNPM_GLOBAL.relative_to(ROOT)),
        "expected_packages": PI_PNPM_PACKAGES,
        "declared_packages": sorted(declared_packages & expected_packages),
        "installed_packages": sorted(pnpm_installed & expected_packages),
        "missing_declared": missing_declared,
        "missing_installed": missing_installed,
        "expected_commands": PI_EXPECTED_COMMANDS,
        "missing_commands": missing_commands,
        "command_paths": command_paths,
        "active_command": path_provenance(active),
        "version": version_result["stdout"].splitlines()[0]
        if version_result["stdout"]
        else None,
        "version_returncode": version_result["returncode"],
        "version_stderr": version_result["stderr"][:300],
        "local_state": {
            "root": str(HOME / ".pi"),
            "agent_root_exists": (HOME / ".pi/agent").exists(),
            "subagent_extension_exists": (
                HOME / ".pi/agent/extensions/subagent"
            ).exists(),
            "sensitive_local_state_excluded": [
                str(HOME / ".pi/agent/auth.json"),
                str(HOME / ".pi/agent/npm"),
                str(HOME / ".pi/agent/extensions"),
            ],
        },
    }

    if (
        active
        and path_source(active) == "pnpm"
        and not missing_declared
        and not missing_installed
        and not missing_commands
    ):
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="pi.command",
            summary="Pi CLI and declared Pi extension packages resolve through the canonical pnpm global path.",
            details=details,
        )
    elif not missing_declared and not missing_installed:
        add_finding(
            findings,
            area="ai_tools",
            classification="migration_pending",
            name="pi.command",
            severity="low",
            summary="Pi packages are declared and installed, but command visibility is incomplete.",
            details=details,
            recommendation="Repair pnpm global PATH visibility before treating Pi as fully canonical.",
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="declared_absent" if not missing_declared else "drift",
            name="pi.command",
            severity="medium",
            summary="Pi CLI or declared Pi extension packages do not match the pnpm global manifest.",
            details=details,
            recommendation="Run the approved node-tool install path or update system/packages/pnpm-global.txt to match the intended Pi package set.",
        )


def scan_ai_tools(
    findings: list[dict[str, Any]],
    brew_declared: dict[str, set[str]],
    pnpm_installed: set[str],
) -> None:
    detected: dict[str, list[str]] = {}
    for command in AI_COMMANDS:
        matches = which_all(command)
        if matches:
            detected[command] = matches

    variant_re = re.compile(r"^(codex|claude|opencode|open-code)([-_.].*)?$|^pi($|[-_.])")
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        directory = Path(entry).expanduser()
        if not directory.is_dir():
            continue
        try:
            for item in directory.iterdir():
                if not item.name or item.name.startswith("."):
                    continue
                if not variant_re.search(item.name):
                    continue
                if item.is_file() or item.is_symlink():
                    if os.access(item, os.X_OK):
                        detected.setdefault(item.name, []).append(str(item))
        except OSError:
            continue

    if detected:
        detected_details = {
            name: [path_provenance(path) for path in sorted(set(paths))]
            for name, paths in sorted(detected.items())
        }
        add_finding(
            findings,
            area="ai_tools",
            classification="managed_exception",
            name="ai_tools.path",
            severity="low",
            summary="AI Tool Surface commands were found on PATH.",
            details={"commands": detected_details},
            recommendation=(
                "Keep binaries separate from APM-managed assets; declare or "
                "clean up each manual CLI through its own tool-surface policy."
            ),
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="unknown",
            name="ai_tools.path",
            summary="No codex, claude, opencode, pi, apm, or obvious variants were found on PATH.",
        )

    scan_claude_code(findings)
    scan_opencode_command(findings, brew_declared)
    scan_opencode_baseline(findings)
    scan_pi_command(findings, pnpm_installed)

    apm_paths = which_all("apm")
    if apm_paths:
        apm_path_details = [path_provenance(path) for path in apm_paths]
        primary_apm = apm_path_details[0]
        manual_apm_paths = [
            path
            for path in apm_path_details
            if str(path.get("source")) in {"manual/pkg", "manual/local"}
        ]
        if primary_apm.get("source") == "homebrew":
            add_finding(
                findings,
                area="ai_tools",
                classification="canonical",
                name="apm.command",
                summary="apm resolves through the declared Homebrew formula.",
                details={
                    "primary": primary_apm,
                    "paths": apm_path_details,
                    "legacy_manual_paths": manual_apm_paths,
                },
            )
            if manual_apm_paths:
                add_finding(
                    findings,
                    area="ai_tools",
                    classification="approval_gated_removal",
                    name="apm.command.legacy_manual_duplicate",
                    severity="low",
                    summary="A legacy manual APM binary is still present after Homebrew migration.",
                    details={"paths": manual_apm_paths},
                    recommendation=(
                        "Remove the legacy /usr/local APM install only in a separate "
                        "cleanup task after confirming Homebrew PATH precedence remains stable."
                    ),
                )
        else:
            add_finding(
                findings,
                area="ai_tools",
                classification="managed_exception",
                name="apm.command",
                severity="low",
                summary="apm is present and selected as the AI Asset Manager, but does not resolve through Homebrew.",
                details={"paths": apm_path_details},
                recommendation="Install and verify the declared Homebrew APM formula before removing the manual binary.",
            )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="unknown",
            name="apm.command",
            summary="apm is not on PATH.",
        )

    scan_ai_baseline(findings)


def scan_applications(paths: list[Path]) -> list[dict[str, str]]:
    apps: list[dict[str, str]] = []
    for directory in paths:
        if not directory.is_dir():
            continue
        try:
            for item in directory.iterdir():
                if item.name.endswith(".app"):
                    apps.append({"name": item.name.removesuffix(".app"), "path": str(item)})
        except OSError:
            continue
    return sorted(apps, key=lambda item: item["name"].lower())


def scan_bin_dir(path: Path) -> list[dict[str, str]]:
    tools: list[dict[str, str]] = []
    if not path.is_dir():
        return tools
    try:
        for item in path.iterdir():
            if item.name.startswith("."):
                continue
            if not (item.is_file() or item.is_symlink()):
                continue
            if not os.access(item, os.X_OK):
                continue
            if not is_dev_related(item.name):
                continue
            source = path_source(str(item))
            if source == "homebrew":
                continue
            tools.append(
                {
                    "name": item.name,
                    "path": str(item),
                    "resolved_source": source,
                }
            )
    except OSError:
        return tools
    return sorted(tools, key=lambda item: item["name"].lower())


def check_manual_apps(
    findings: list[dict[str, Any]],
    brew_declared: dict[str, set[str]],
) -> None:
    add_manifest_presence(findings, "manual_apps", MANUAL_APPS, "manual apps")
    manual_declared = parse_manual_apps(MANUAL_APPS)

    installed_cask_norms = set()
    cask_result = command_result(["brew", "list", "--cask"]) if shutil.which("brew") else None
    if cask_result and cask_result["ok"]:
        installed_cask_norms = {normalize_app_name(value) for value in lines(cask_result["stdout"])}
    declared_cask_norms = {normalize_app_name(value) for value in brew_declared["cask"]}

    apps = scan_applications([Path("/Applications"), HOME / "Applications"])
    manual_dev_apps = []
    canonical_apps = []
    declared_manual_apps = []
    for app in apps:
        normalized = normalize_app_name(app["name"])
        if normalized in installed_cask_norms or normalized in declared_cask_norms:
            canonical_apps.append(app)
            continue
        if normalized in manual_declared:
            declared_manual_apps.append(app)
            continue
        if DEV_APP_RE.search(app["name"]):
            manual_dev_apps.append(app)

    if manual_dev_apps:
        add_finding(
            findings,
            area="manual_apps",
            classification="manual",
            name="manual_apps.applications",
            severity="low",
            source="/Applications, ~/Applications",
            summary="Manual or approval-gated dev applications were detected outside declared Homebrew casks.",
            details={"apps": manual_dev_apps},
            recommendation="Declare intentional manual apps in system/packages/manual-apps.md or move them to a canonical installer.",
        )
    else:
        add_finding(
            findings,
            area="manual_apps",
            classification="canonical",
            name="manual_apps.applications",
            source="/Applications, ~/Applications",
            summary="No obvious manual dev applications were detected outside declared Homebrew casks.",
            details={
                "canonical_app_count": len(canonical_apps),
                "declared_manual_app_count": len(declared_manual_apps),
            },
        )

    bin_tools = scan_bin_dir(Path("/usr/local/bin")) + scan_bin_dir(HOME / ".local/bin")
    unknown_bin_tools = [
        tool
        for tool in bin_tools
        if normalize_app_name(tool["name"]) not in manual_declared
        and normalize_app_name(Path(tool["path"]).name) not in manual_declared
    ]
    declared_manual_bin_tools = [
        tool for tool in bin_tools if tool not in unknown_bin_tools
    ]
    if unknown_bin_tools:
        add_finding(
            findings,
            area="manual_apps",
            classification="manual",
            name="manual_apps.bin_tools",
            severity="low",
            source="/usr/local/bin, ~/.local/bin",
            summary="Manual dev-related executables were detected in local bin directories.",
            details={
                "tools": unknown_bin_tools[:80],
                "truncated": len(unknown_bin_tools) > 80,
            },
            recommendation="Declare intentional local tools or migrate them to a canonical installer.",
        )
    else:
        add_finding(
            findings,
            area="manual_apps",
            classification="canonical",
            name="manual_apps.bin_tools",
            source="/usr/local/bin, ~/.local/bin",
            summary="No obvious manual dev-related executables were detected in local bin directories.",
            details={"declared_manual_tool_count": len(declared_manual_bin_tools)},
        )


def build_payload() -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    execution_context = collect_execution_context()
    brew_declared = check_brew(findings)
    js_commands = check_js_toolchain(findings)
    compare_extensions(
        findings,
        area="vscode",
        command="code",
        manifest=VSCODE_EXTENSIONS,
        label="VS Code",
    )
    pnpm_installed = check_pnpm(findings, js_commands)
    check_npm(findings, set(clean_manifest_lines(PNPM_GLOBAL)), pnpm_installed, js_commands)
    check_fnm(findings, brew_declared)
    check_runtime_managers(findings)
    check_shell_parity(findings)
    check_dotnet(findings)
    scan_ai_tools(findings, brew_declared, pnpm_installed)
    check_manual_apps(findings, brew_declared)

    by_classification = Counter(finding["classification"] for finding in findings)
    by_area = Counter(finding["area"] for finding in findings)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(ROOT),
        "read_only": True,
        "execution_context": execution_context,
        "summary": {
            "total_findings": len(findings),
            "by_classification": dict(sorted(by_classification.items())),
            "by_area": dict(sorted(by_area.items())),
        },
        "findings": findings,
    }


def format_items(value: Any, max_items: int = 10) -> str:
    if isinstance(value, dict):
        parts = []
        for key, nested in value.items():
            if isinstance(nested, list):
                parts.append(f"{key}: {format_items(nested, max_items)}")
            else:
                parts.append(f"{key}: {nested}")
        return "; ".join(parts)
    if isinstance(value, list):
        if value and all(isinstance(item, dict) for item in value):
            rendered_items = []
            for item in value[:max_items]:
                name = item.get("name") or item.get("path") or item
                path = item.get("path")
                rendered_items.append(f"{name} ({path})" if path else str(name))
            rendered = ", ".join(rendered_items)
            if len(value) > max_items:
                rendered += f", ... (+{len(value) - max_items} more)"
            return rendered
        rendered = ", ".join(str(item) for item in value[:max_items])
        if len(value) > max_items:
            rendered += f", ... (+{len(value) - max_items} more)"
        return rendered
    return str(value)


def is_actionable_finding(finding: dict[str, Any]) -> bool:
    classification = finding.get("classification")
    severity = finding.get("severity")
    return bool(
        classification in ACTIONABLE_CLASSIFICATIONS
        or (
            severity in ACTIONABLE_SEVERITIES
            and classification not in {"canonical", "managed_exception", "not_required"}
        )
    )


def emit_full_markdown(payload: dict[str, Any]) -> None:
    print("# Development Ecosystem Doctor")
    print()
    print(f"- Repo: `{payload['repo_root']}`")
    print("- Mode: read-only audit; no installs, uninstalls, migrations, backups, or rewrites")
    print(f"- Findings: {payload['summary']['total_findings']}")
    counts = payload["summary"]["by_classification"]
    print(
        "- Classifications: "
        + ", ".join(f"{key}={value}" for key, value in counts.items())
    )

    context = payload["execution_context"]
    print()
    print("## execution-context")
    print(f"- `SHELL`: `{context.get('shell_env')}`")
    parent_shells = context.get("detected_parent_shells") or []
    print(f"- Detected parent/current shells: `{', '.join(parent_shells) if parent_shells else 'none'}`")
    print(f"- Python executable: `{context.get('python_executable')}`")
    print("- Parent process chain:")
    for item in context.get("parent_process_chain", []):
        pid = item.get("pid")
        ppid = item.get("ppid")
        command = item.get("command") or item.get("basename") or "unknown"
        print(f"  - pid={pid} ppid={ppid} command=`{command}`")
    print("- Current process PATH:")
    for entry in context.get("path_entries", []):
        print(f"  - `{entry}`")

    findings = payload["findings"]
    for area in AREA_ORDER:
        area_findings = [finding for finding in findings if finding["area"] == area]
        if not area_findings:
            continue
        print()
        print(f"## {area}")
        for finding in area_findings:
            print(f"- `{finding['classification']}` `{finding['name']}`: {finding['summary']}")
            details = finding.get("details", {})
            interesting: list[str] = []
            for key in (
                "missing",
                "packages",
                "tools",
                "formulae",
                "casks",
                "extensions",
                "apps",
                "commands",
                "installed_versions",
            ):
                if key in details and details[key]:
                    interesting.append(f"{key}: {format_items(details[key])}")
            if interesting:
                print(f"  - details: {'; '.join(interesting)}")
            if finding.get("recommendation"):
                print(f"  - later: {finding['recommendation']}")


def emit_concise_markdown(payload: dict[str, Any]) -> None:
    findings = [finding for finding in payload["findings"] if is_actionable_finding(finding)]
    if not findings:
        print("Your development ecosystem is ready.")
        return

    print(f"Doctor found {len(findings)} issue{'s' if len(findings) != 1 else ''}:")
    for area in AREA_ORDER:
        area_findings = [finding for finding in findings if finding["area"] == area]
        if not area_findings:
            continue
        print()
        print(f"## {area}")
        for finding in area_findings:
            print(f"- `{finding['name']}`: {finding['summary']}")
            details = finding.get("details", {})
            interesting: list[str] = []
            for key in (
                "missing",
                "packages",
                "tools",
                "formulae",
                "casks",
                "extensions",
                "apps",
                "commands",
                "installed_versions",
            ):
                if key in details and details[key]:
                    interesting.append(f"{key}: {format_items(details[key])}")
            if interesting:
                print(f"  - details: {'; '.join(interesting)}")
            if finding.get("recommendation"):
                print(f"  - fix: {finding['recommendation']}")

    print()
    print("Run `doctor --all` for the full read-only audit or `doctor --json` for machine-readable output.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only audit of this dotfiles Development Ecosystem."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of markdown.",
    )
    parser.add_argument(
        "--all",
        "--verbose",
        action="store_true",
        dest="show_all",
        help="Emit the full markdown audit instead of only actionable findings.",
    )
    args = parser.parse_args()

    payload = build_payload()
    if args.json:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        print()
    elif args.show_all:
        emit_full_markdown(payload)
    else:
        emit_concise_markdown(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
