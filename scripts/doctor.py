#!/usr/bin/env python3
"""Read-only Development Ecosystem doctor for this Orchestrator Repo.

Design rules:
- Read-only: no installs, uninstalls, migrations, backups, or rewrites.
- Manifest-driven: expected state comes from the repo manifests
  (Brewfile, pnpm-global.txt, dotnet-tools.txt, system/mise/config.toml,
  system/ai/apm/apm.yml + apm.lock.yaml), never from constants in this file.
- Stdlib only: runs on a fresh machine with any modern python3.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

# Repo manifests (the sources of truth this doctor audits against).
BREWFILE = ROOT / "system/packages/Brewfile"
PERSONAL_BREWFILE = ROOT / "system/packages/personal.Brewfile"
VSCODE_EXTENSIONS = ROOT / "system/packages/vscode-extensions.txt"
PNPM_GLOBAL = ROOT / "system/packages/pnpm-global.txt"
DOTNET_TOOLS = ROOT / "system/packages/dotnet-tools.txt"
MANUAL_APPS = ROOT / "system/packages/manual-apps.md"
APM_MANIFEST = ROOT / "system/ai/apm/apm.yml"
APM_LOCKFILE = ROOT / "system/ai/apm/apm.lock.yaml"
MISE_CONFIG = ROOT / "system/mise/config.toml"
PATH_CONTRACT = ROOT / "system/shell/path.sh"
DEV_ENV = ROOT / "scripts/dev_env.sh"
ZSH_FILES = [
    ROOT / "system/zsh/.zshenv",
    ROOT / "system/zsh/.zprofile",
    ROOT / "system/zsh/.zshrc",
]

# Live locations the manifests deploy to.
APM_USER_MANIFEST = HOME / ".apm/apm.yml"
APM_USER_LOCKFILE = HOME / ".apm/apm.lock.yaml"
MISE_USER_CONFIG = HOME / ".config/mise/config.toml"
CLAUDE_COMMAND = HOME / ".local/bin/claude"
CLAUDE_VERSIONS_DIR = HOME / ".local/share/claude/versions"
CLAUDE_DESKTOP_APP = Path("/Applications/Claude.app")
SKILL_DIRS_BY_TARGET = {
    "codex": HOME / ".codex/skills",
    "claude": HOME / ".claude/skills",
    "opencode": HOME / ".config/opencode/skills",
}

# Policy constants. Keep this section tiny: entries here must be policy or
# structural facts, not copies of manifest data.
# ADR-0003: intentionally excluded from the Global AI Baseline.
EXCLUDED_AI_ASSETS = {"using-superpowers"}
# Codex ships vendor runtime skills that are not baseline drift.
CODEX_VENDOR_RUNTIME_SKILLS = {".system", "codex-primary-runtime"}
# Toolchain entry points the dev_env.sh PATH contract must expose.
DEV_ENV_EXPECTED_COMMANDS = ["node", "npm", "pnpm", "corepack", "dotnet", "just"]
JS_COMMANDS = ["node", "npm", "npx", "pnpm", "corepack"]
NPM_RUNTIME_GLOBALS = {"corepack", "npm"}
AI_COMMANDS = ["codex", "claude", "opencode", "pi", "apm"]

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
    "shell",
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

# Heuristics for spotting stray dev tools (detection only, not desired state).
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

RUNTIME_MANAGERS = {
    "nvm": {"commands": ["nvm"], "paths": [HOME / ".nvm"], "classification": "legacy"},
    "volta": {"commands": ["volta"], "paths": [HOME / ".volta"], "classification": "legacy"},
    "asdf": {"commands": ["asdf"], "paths": [HOME / ".asdf"], "classification": "legacy"},
    "nodenv": {"commands": ["nodenv"], "paths": [HOME / ".nodenv"], "classification": "legacy"},
    "mise": {
        "commands": ["mise"],
        "paths": [HOME / ".local/share/mise", HOME / ".config/mise"],
        "classification": "canonical",
    },
    "pyenv": {"commands": ["pyenv"], "paths": [HOME / ".pyenv"], "classification": "unknown"},
    "rbenv": {"commands": ["rbenv"], "paths": [HOME / ".rbenv"], "classification": "unknown"},
    "jenv": {"commands": ["jenv"], "paths": [HOME / ".jenv"], "classification": "unknown"},
    "sdkman": {"commands": ["sdk"], "paths": [HOME / ".sdkman"], "classification": "unknown"},
    "rustup": {
        "commands": ["rustup"],
        "paths": [HOME / ".rustup", HOME / ".cargo"],
        "classification": "unknown",
    },
    "goenv": {"commands": ["goenv"], "paths": [HOME / ".goenv"], "classification": "unknown"},
}


# --- generic helpers ---------------------------------------------------------


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


def short_brew_name(name: str) -> str:
    return name.rsplit("/", 1)[-1]


def equivalent_member(name: str, values: set[str]) -> bool:
    short_values = {short_brew_name(value) for value in values}
    return name in values or short_brew_name(name) in short_values


def is_dev_related(name: str) -> bool:
    return bool(DEV_RE.search(name.lower()))


def normalize_app_name(value: str) -> str:
    value = value.lower().removesuffix(".app")
    return re.sub(r"[^a-z0-9]+", "", value)


def normalize_extension(value: str) -> str:
    return value.strip().lower()


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
    details: dict[str, Any] = {"path": original, "resolved_path": resolved}

    def with_source(source: str) -> dict[str, Any]:
        return {"source": source, **details}

    if original.startswith(f"{mise_data_dir}/") or resolved.startswith(f"{mise_data_dir}/"):
        return with_source("mise")
    if resolved.startswith("/opt/homebrew/") or "/usr/local/Cellar/" in resolved:
        return with_source("homebrew")
    if resolved.startswith("/usr/local/Homebrew/"):
        return with_source("homebrew")
    if f"{home}/.local/share/fnm" in resolved or f"{home}/.local/share/fnm" in original:
        return with_source("fnm")
    if f"{home}/.local/state/fnm_multishells" in resolved:
        return with_source("fnm")
    if resolved.startswith(f"{home}/Library/pnpm") or original.startswith(f"{home}/Library/pnpm"):
        return with_source("pnpm")
    if resolved.startswith("/usr/local/share/dotnet"):
        pkg_info = pkgutil_file_info(resolved) or pkgutil_file_info(original)
        if pkg_info:
            details["pkgutil"] = pkg_info
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
            return with_source("manual/pkg")
        return with_source("manual/local")
    if resolved.startswith("/usr/bin") or resolved.startswith("/bin"):
        return with_source("system")
    return with_source("unknown")


def path_source(path: str | None) -> str:
    return str(path_provenance(path).get("source", "unknown"))


def path_exists_or_symlink(path: Path) -> bool:
    return path.exists() or path.is_symlink()


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


def symlink_file_state(path: Path, expected_target: Path) -> dict[str, Any]:
    state: dict[str, Any] = {
        "path": str(path),
        "path_present": path_exists_or_symlink(path),
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
    state["canonical"] = bool(state["is_symlink"] and state["points_to_expected_target"])
    return state


# --- manifest parsing --------------------------------------------------------
# The two APM files are simple machine-generated YAML. Parse exactly that
# shape with strict errors rather than carrying a YAML library dependency.


def yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_apm_manifest() -> dict[str, Any]:
    """Parse targets and dependencies.apm from system/ai/apm/apm.yml."""
    state: dict[str, Any] = {
        "path": str(APM_MANIFEST),
        "exists": APM_MANIFEST.exists(),
        "targets": [],
        "apm_refs": [],
        "parser_errors": [],
    }
    if not APM_MANIFEST.exists():
        return state

    section: str | None = None
    in_dependencies_apm = False
    for raw in APM_MANIFEST.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0:
            match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
            if not match:
                state["parser_errors"].append(f"unsupported top-level line: {line}")
                continue
            section = match.group(1)
            in_dependencies_apm = False
            continue
        if section == "targets":
            match = re.match(r"^-\s+(.+)$", line)
            if match:
                state["targets"].append(yaml_scalar(match.group(1)))
            else:
                state["parser_errors"].append(f"unsupported targets line: {line}")
        elif section == "dependencies":
            if re.match(r"^apm:\s*$", line):
                in_dependencies_apm = True
                continue
            match = re.match(r"^-\s+(.+)$", line)
            if in_dependencies_apm and match:
                state["apm_refs"].append(yaml_scalar(match.group(1)))
            else:
                state["parser_errors"].append(f"unsupported dependencies line: {line}")
    if state["exists"] and not state["targets"]:
        state["parser_errors"].append("missing top-level targets block")
    if state["exists"] and not state["apm_refs"]:
        state["parser_errors"].append("missing dependencies.apm block")
    return state


def parse_apm_lockfile() -> dict[str, Any]:
    """Parse the flat dependency list from system/ai/apm/apm.lock.yaml."""
    state: dict[str, Any] = {
        "path": str(APM_LOCKFILE),
        "exists": APM_LOCKFILE.exists(),
        "dependencies": [],
        "parser_errors": [],
    }
    if not APM_LOCKFILE.exists():
        return state

    in_dependencies = False
    current: dict[str, str] | None = None
    for raw in APM_LOCKFILE.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if re.match(r"^dependencies:\s*$", raw):
            in_dependencies = True
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:", raw):
            in_dependencies = False
            continue
        if not in_dependencies:
            continue
        item_match = re.match(r"^-\s+([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if item_match:
            current = {item_match.group(1): yaml_scalar(item_match.group(2))}
            state["dependencies"].append(current)
            continue
        field_match = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if current is not None and field_match:
            current[field_match.group(1)] = yaml_scalar(field_match.group(2))
            continue
        state["parser_errors"].append(f"unsupported dependencies line: {raw.strip()}")
    return state


def apm_ref_parts(ref: str) -> dict[str, str]:
    """Split 'owner/repo/path/to/skill#ref' into repo_url, virtual_path, ref, name."""
    ref_part = ""
    path_part = ref
    if "#" in ref:
        path_part, ref_part = ref.split("#", 1)
    segments = path_part.split("/")
    repo_url = "/".join(segments[:2])
    virtual_path = "/".join(segments[2:])
    return {
        "ref": ref,
        "repo_url": repo_url,
        "virtual_path": virtual_path,
        "requested_ref": ref_part,
        "name": segments[-1] if segments else "",
    }


def mise_config_state() -> dict[str, Any]:
    state: dict[str, Any] = {
        "path": str(MISE_CONFIG),
        "source": str(MISE_CONFIG.relative_to(ROOT)),
        "exists": MISE_CONFIG.exists(),
        "dotnet_versions": [],
        "declares_node": False,
        "dotnet_root": None,
        "parse_error": None,
        "user_config": symlink_file_state(MISE_USER_CONFIG, MISE_CONFIG),
    }
    if not MISE_CONFIG.exists():
        return state
    try:
        data = tomllib.loads(MISE_CONFIG.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        state["parse_error"] = f"{type(exc).__name__}: {exc}"
        return state

    tools = data.get("tools") if isinstance(data.get("tools"), dict) else {}
    settings = data.get("settings") if isinstance(data.get("settings"), dict) else {}
    dotnet_settings = settings.get("dotnet") if isinstance(settings.get("dotnet"), dict) else {}

    value = tools.get("dotnet")
    if isinstance(value, str):
        state["dotnet_versions"] = [value]
    elif isinstance(value, list):
        state["dotnet_versions"] = [item for item in value if isinstance(item, str)]
    state["declares_node"] = "node" in tools
    state["dotnet_root"] = dotnet_settings.get("dotnet_root")
    return state


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


# --- brew --------------------------------------------------------------------


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

    formulae_result = command_result(["brew", "list", "--formula", "--full-name"])
    casks_result = command_result(["brew", "list", "--cask"])
    leaves_result = command_result(["brew", "leaves"])

    installed_formulae = set(lines(formulae_result["stdout"])) if formulae_result["ok"] else set()
    installed_casks = set(lines(casks_result["stdout"])) if casks_result["ok"] else set()
    installed_leaves = set(lines(leaves_result["stdout"])) if leaves_result["ok"] else installed_formulae

    for kind, installed in (("formulae", installed_formulae), ("casks", installed_casks)):
        manifest_key = "brew" if kind == "formulae" else "cask"
        missing = sorted(
            name for name in declared[manifest_key] if not equivalent_member(name, installed)
        )
        present_count = len(declared[manifest_key]) - len(missing)
        add_finding(
            findings,
            area="brew",
            classification="canonical" if not missing else "declared_absent",
            name=f"homebrew.{kind}.declared",
            severity="info" if not missing else "medium",
            source=str(BREWFILE.relative_to(ROOT)),
            summary=(
                f"{present_count}/{len(declared[manifest_key])} declared Homebrew "
                f"{kind} appear installed."
            ),
            details={"missing": missing},
            recommendation=(
                f"A later install task can install missing declared {kind}."
                if missing
                else None
            ),
        )

    declared_or_personal_formulae = declared["brew"] | personal_declared["brew"]
    declared_or_personal_casks = declared["cask"] | personal_declared["cask"]
    undeclared_formulae = sorted(
        name
        for name in installed_leaves
        if not equivalent_member(name, declared_or_personal_formulae) and is_dev_related(name)
    )
    undeclared_casks = sorted(
        name
        for name in installed_casks
        if not equivalent_member(name, declared_or_personal_casks) and is_dev_related(name)
    )
    if undeclared_formulae or undeclared_casks:
        add_finding(
            findings,
            area="brew",
            classification="present_undeclared",
            name="homebrew.dev_tools.present_undeclared",
            severity="low",
            summary="Installed Homebrew dev-related tools were not declared in the Brewfile.",
            details={"formulae": undeclared_formulae, "casks": undeclared_casks},
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
        personal_missing = sorted(
            name
            for name in personal_declared["brew"]
            if not equivalent_member(name, installed_formulae)
        ) + sorted(
            name
            for name in personal_declared["cask"]
            if not equivalent_member(name, installed_casks)
        )
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
            details={"missing": personal_missing},
            recommendation=(
                "Run just install-personal-brew if these personal packages should stay on this laptop."
                if personal_missing
                else None
            ),
        )

    return declared


# --- editors -----------------------------------------------------------------


def check_vscode_extensions(findings: list[dict[str, Any]]) -> None:
    add_manifest_presence(findings, "vscode", VSCODE_EXTENSIONS, "VS Code")
    declared = {normalize_extension(value) for value in clean_manifest_lines(VSCODE_EXTENSIONS)}
    cli_path = shutil.which("code")
    if not cli_path:
        add_finding(
            findings,
            area="vscode",
            classification="unknown",
            name="VS Code.cli",
            summary="code is not on PATH; installed VS Code extensions were not audited.",
            recommendation="Run this doctor from an environment where code is available.",
        )
        return

    result = command_result(["code", "--list-extensions"], timeout=20)
    if not result["ok"]:
        add_finding(
            findings,
            area="vscode",
            classification="unknown",
            name="VS Code.extensions.installed",
            severity="low",
            source=cli_path,
            summary="code exists, but extension discovery did not complete.",
            details={"returncode": result["returncode"], "stderr": result["stderr"][:400]},
        )
        return

    installed = {normalize_extension(value) for value in lines(result["stdout"])}
    missing = sorted(declared - installed)
    undeclared = sorted(installed - declared)
    add_finding(
        findings,
        area="vscode",
        classification="canonical" if not missing else "declared_absent",
        name="VS Code.extensions.declared",
        severity="info" if not missing else "medium",
        source=str(VSCODE_EXTENSIONS.relative_to(ROOT)),
        summary=(
            f"{len(declared) - len(missing)}/{len(declared)} declared VS Code "
            "extensions appear installed."
        ),
        details={"missing": missing},
        recommendation=(
            "A later install task can install missing declared extensions." if missing else None
        ),
    )
    if undeclared:
        add_finding(
            findings,
            area="vscode",
            classification="present_undeclared",
            name="VS Code.extensions.present_undeclared",
            severity="low",
            source=cli_path,
            summary=f"{len(undeclared)} installed VS Code extensions are not declared.",
            details={"extensions": undeclared},
            recommendation="Declare intentional extensions or remove them behind a Reset Approval Gate.",
        )
    else:
        add_finding(
            findings,
            area="vscode",
            classification="canonical",
            name="VS Code.extensions.present_undeclared",
            source=cli_path,
            summary="No undeclared VS Code extensions were detected.",
        )


# --- javascript toolchain ----------------------------------------------------


def fnm_default_version() -> str | None:
    if not shutil.which("fnm"):
        return None
    result = command_result(["fnm", "default"], timeout=10)
    if result["ok"] and result["stdout"]:
        return result["stdout"].splitlines()[0].strip()
    return None


def check_js_toolchain(findings: list[dict[str, Any]]) -> None:
    commands = {
        command: {
            "which": shutil.which(command),
            "provenance": path_provenance(shutil.which(command)),
        }
        for command in JS_COMMANDS
    }
    add_finding(
        findings,
        area="js_toolchain",
        classification="canonical",
        name="js_toolchain.resolution",
        summary="JavaScript toolchain command resolution captured for this process.",
        details={"commands": commands},
    )

    stale_packages: list[dict[str, Any]] = []
    for root in (Path("/opt/homebrew/lib/node_modules"), Path("/usr/local/lib/node_modules")):
        if not root.is_dir():
            continue
        try:
            for child in sorted(root.iterdir(), key=lambda value: value.name):
                stale_packages.append({"root": str(root), "name": child.name, "path": str(child)})
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
                    stale_symlinks.append({"path": str(child), "target": target})
        except OSError:
            continue

    if stale_packages or stale_symlinks:
        add_finding(
            findings,
            area="js_toolchain",
            classification="drift",
            name="js_toolchain.homebrew_prefix_node_globals",
            severity="medium",
            summary=(
                "Homebrew-prefix Node global leftovers are present outside the "
                "canonical fnm/pnpm ownership model."
            ),
            details={"packages": stale_packages, "bin_symlinks": stale_symlinks},
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
        )


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


def dev_env_command(args: list[str]) -> list[str]:
    """Run a command inside the repo PATH contract (scripts/dev_env.sh)."""
    return [str(DEV_ENV), *args]


def check_pnpm(findings: list[dict[str, Any]]) -> set[str]:
    add_manifest_presence(findings, "pnpm", PNPM_GLOBAL, "pnpm global")
    declared = set(clean_manifest_lines(PNPM_GLOBAL))

    if not DEV_ENV.exists() or not fnm_default_version():
        add_finding(
            findings,
            area="pnpm",
            classification="unknown",
            name="pnpm.globals",
            severity="medium",
            summary="No trusted pnpm toolchain (dev_env + fnm default) was available for audit.",
            recommendation="Install fnm and a default Node version through the declared bootstrap path.",
        )
        return set()

    args = dev_env_command(
        ["fnm", "exec", "--using", "default", "pnpm", "list", "-g", "--depth", "0", "--json"]
    )
    result = command_result(args, timeout=25)
    installed = parse_pnpm_globals(result["stdout"])
    if not result["ok"] and not installed:
        add_finding(
            findings,
            area="pnpm",
            classification="unknown",
            name="pnpm.globals",
            severity="medium",
            summary="pnpm global audit did not produce package data.",
            details={
                "returncode": result["returncode"],
                "stderr": result["stderr"][:500],
                "args": args,
            },
            recommendation="Treat pnpm drift as unknown until the laptop JS toolchain can be audited.",
        )
        return set()

    missing = sorted(declared - installed)
    undeclared = sorted(installed - declared)
    add_finding(
        findings,
        area="pnpm",
        classification="canonical" if not missing else "declared_absent",
        name="pnpm.globals.declared",
        severity="info" if not missing else "medium",
        source=str(PNPM_GLOBAL.relative_to(ROOT)),
        summary=(
            f"{len(declared) - len(missing)}/{len(declared)} declared pnpm globals appear installed."
        ),
        details={"missing": missing, "installed": sorted(installed)},
        recommendation=(
            "A later install task can install missing declared pnpm globals." if missing else None
        ),
    )
    if undeclared:
        add_finding(
            findings,
            area="pnpm",
            classification="present_undeclared",
            name="pnpm.globals.present_undeclared",
            severity="low",
            summary=f"{len(undeclared)} pnpm globals are installed but undeclared.",
            details={"packages": undeclared},
            recommendation="Declare intentional pnpm globals or remove them behind a Reset Approval Gate.",
        )
    else:
        add_finding(
            findings,
            area="pnpm",
            classification="canonical",
            name="pnpm.globals.present_undeclared",
            summary="No undeclared pnpm globals were detected.",
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


def check_npm(
    findings: list[dict[str, Any]],
    pnpm_declared: set[str],
    pnpm_installed: set[str],
) -> None:
    if not DEV_ENV.exists() or not fnm_default_version():
        add_finding(
            findings,
            area="npm",
            classification="unknown",
            name="npm.globals",
            summary="No trusted npm toolchain was available; npm globals were not audited.",
        )
        return

    args = dev_env_command(
        ["fnm", "exec", "--using", "default", "npm", "ls", "-g", "--depth=0", "--json"]
    )
    result = command_result(args, timeout=25)
    installed = parse_npm_globals(result["stdout"])
    if not result["ok"] and not installed:
        add_finding(
            findings,
            area="npm",
            classification="unknown",
            name="npm.globals",
            severity="medium",
            summary="npm global audit did not produce package data.",
            details={
                "returncode": result["returncode"],
                "stderr": result["stderr"][:500],
                "args": args,
            },
        )
        return

    duplicate_with_pnpm = sorted(installed & (pnpm_declared | pnpm_installed))
    runtime_owned = installed & NPM_RUNTIME_GLOBALS
    legacy_globals = sorted(installed - set(duplicate_with_pnpm) - runtime_owned)

    if duplicate_with_pnpm:
        classification = "duplicate"
    elif legacy_globals:
        classification = "legacy"
    else:
        classification = "canonical"
    add_finding(
        findings,
        area="npm",
        classification=classification,
        name="npm.globals",
        severity="medium" if duplicate_with_pnpm or legacy_globals else "info",
        summary=(
            f"npm reports {len(installed)} globals; {len(duplicate_with_pnpm)} duplicate "
            f"pnpm globals and {len(legacy_globals)} other npm globals."
        ),
        details={
            "installed": sorted(installed),
            "duplicate_with_pnpm": duplicate_with_pnpm,
            "legacy_packages": legacy_globals,
            "runtime_owned_packages": sorted(runtime_owned),
        },
        recommendation=(
            "Prefer the canonical pnpm global path; remove npm duplicates only after a Reset Approval Gate."
            if duplicate_with_pnpm
            else None
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
    classification = (
        "canonical" if source == "homebrew" and "fnm" in brew_declared["brew"] else "unknown"
    )
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
    inventory = parse_fnm_inventory(list_result["stdout"])
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
            "system_node_present": inventory["system_node_present"],
        },
    )


def check_runtime_managers(findings: list[dict[str, Any]]) -> None:
    present: dict[str, dict[str, Any]] = {}
    absent: list[str] = []
    for name, spec in RUNTIME_MANAGERS.items():
        command_matches: list[str] = []
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
                severity="info" if is_canonical else "medium" if classification == "legacy" else "low",
                summary=(
                    "Canonical runtime manager signals detected: "
                    if is_canonical
                    else "Competing runtime manager signals detected: "
                )
                + f"{', '.join(sorted(names))}.",
                details={manager: present[manager] for manager in sorted(names)},
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


# --- shell contract ----------------------------------------------------------


def check_shell_contract(findings: list[dict[str, Any]]) -> None:
    """The PATH contract lives in system/shell/path.sh; every consumer sources it."""
    consumers = [*ZSH_FILES, DEV_ENV]
    missing_reference = []
    for consumer in consumers:
        if not consumer.exists():
            missing_reference.append(f"{consumer.relative_to(ROOT)} (missing)")
            continue
        if "system/shell/path.sh" not in consumer.read_text(encoding="utf-8"):
            missing_reference.append(str(consumer.relative_to(ROOT)))

    if not PATH_CONTRACT.exists():
        add_finding(
            findings,
            area="shell",
            classification="missing",
            name="shell.path_contract",
            severity="high",
            source="system/shell/path.sh",
            summary="The shared PATH contract file is missing.",
            recommendation="Restore system/shell/path.sh; all shells and wrappers source it.",
        )
        return
    if missing_reference:
        add_finding(
            findings,
            area="shell",
            classification="drift",
            name="shell.path_contract",
            severity="medium",
            source="system/shell/path.sh",
            summary="Some shell entry points do not source the shared PATH contract.",
            details={"not_sourcing_contract": missing_reference},
            recommendation="Source system/shell/path.sh from every shell entry point instead of duplicating PATH logic.",
        )
    else:
        add_finding(
            findings,
            area="shell",
            classification="canonical",
            name="shell.path_contract",
            source="system/shell/path.sh",
            summary="All shell entry points source the shared PATH contract.",
        )

    if not DEV_ENV.exists():
        add_finding(
            findings,
            area="shell",
            classification="missing",
            name="shell.dev_env_wrapper",
            severity="medium",
            source="scripts/dev_env.sh",
            summary="The non-interactive development environment wrapper is missing.",
            recommendation="Restore scripts/dev_env.sh.",
        )
        return

    probe = "; ".join(f"command -v {command} || echo MISSING:{command}" for command in DEV_ENV_EXPECTED_COMMANDS)
    result = command_result(dev_env_command(["/bin/sh", "-c", probe]), timeout=20)
    missing = [
        line.removeprefix("MISSING:")
        for line in lines(result["stdout"])
        if line.startswith("MISSING:")
    ]
    resolved = {
        Path(line).name: line for line in lines(result["stdout"]) if not line.startswith("MISSING:")
    }
    add_finding(
        findings,
        area="shell",
        classification="canonical" if result["ok"] and not missing else "drift",
        name="shell.dev_env_wrapper",
        severity="info" if result["ok"] and not missing else "medium",
        source="scripts/dev_env.sh",
        summary=(
            "dev_env wrapper exposes the expected toolchain entry points."
            if result["ok"] and not missing
            else "dev_env wrapper does not expose the full expected command surface."
        ),
        details={
            "expected": DEV_ENV_EXPECTED_COMMANDS,
            "missing": missing,
            "resolved": resolved,
        },
        recommendation=(
            None
            if result["ok"] and not missing
            else "Fix system/shell/path.sh or install the missing toolchains before relying on the wrapper."
        ),
    )


# --- dotnet ------------------------------------------------------------------


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
        tools.append(
            {
                "package_id": parts[0],
                "version": parts[1],
                "commands": [
                    command.strip().strip(",")
                    for command in " ".join(parts[2:]).split(",")
                    if command.strip()
                ],
            }
        )
    return tools


def check_dotnet(findings: list[dict[str, Any]]) -> None:
    add_manifest_presence(findings, "dotnet", DOTNET_TOOLS, ".NET global tool")
    mise_state = mise_config_state()
    policy_versions = mise_state["dotnet_versions"]

    if not mise_state["exists"] or mise_state["parse_error"]:
        add_finding(
            findings,
            area="dotnet",
            classification="declared_absent",
            name="dotnet.mise_config",
            severity="medium",
            source=mise_state["source"],
            summary="Repo-managed mise .NET config is missing or unparseable.",
            details=mise_state,
            recommendation="Restore system/mise/config.toml with the intended dotnet SDK lines.",
        )
        return

    has_policy = bool(policy_versions) and not mise_state["declares_node"]
    add_finding(
        findings,
        area="dotnet",
        classification="canonical" if has_policy else "drift",
        name="dotnet.mise_config",
        severity="info" if has_policy else "medium",
        source=mise_state["source"],
        summary=(
            f"Repo-managed mise config declares .NET SDK lines {policy_versions} "
            "without taking Node ownership."
            if has_policy
            else "Repo-managed mise config does not declare the expected .NET-only policy."
        ),
        details=mise_state,
        recommendation=(
            None
            if has_policy
            else "Keep Node under fnm and declare only .NET SDK lines in system/mise/config.toml."
        ),
    )

    declared_tools = set(clean_manifest_lines(DOTNET_TOOLS))
    dotnet_path = shutil.which("dotnet")
    if not dotnet_path:
        add_finding(
            findings,
            area="dotnet",
            classification="migration_pending" if has_policy else "unknown",
            name="dotnet.command",
            severity="info" if has_policy else "medium",
            summary=(
                "dotnet is not on PATH yet, but the mise .NET policy is declared."
                if has_policy
                else "dotnet is not on PATH; SDKs and global tools were not audited."
            ),
            recommendation="Install SDKs through just install-dotnet-sdks in a later approved step.",
        )
        return

    provenance = path_provenance(dotnet_path)
    sdk_result = command_result([dotnet_path, "--list-sdks"], timeout=20, env=DOTNET_READ_ONLY_ENV)
    sdk_lines = lines(sdk_result["stdout"])
    sdk_major_lines = sorted(
        {sdk.split()[0].split(".", 1)[0] for sdk in sdk_lines if sdk and sdk[0].isdigit()}
    )
    missing_sdk_lines = [line for line in policy_versions if line not in sdk_major_lines]
    is_mise = provenance["source"] == "mise"
    add_finding(
        findings,
        area="dotnet",
        classification=(
            "canonical" if is_mise and not missing_sdk_lines else "migration_pending"
        ),
        name="dotnet.sdk_source",
        source=dotnet_path,
        severity="info" if is_mise and not missing_sdk_lines else "low",
        summary=(
            "dotnet resolves through the mise SDK owner with the declared SDK major lines."
            if is_mise and not missing_sdk_lines
            else f"dotnet is present from {provenance['source']}; declared mise policy is not fully active."
        ),
        details={
            "provenance": provenance,
            "declared_sdk_major_lines": policy_versions,
            "installed_sdk_major_lines": sdk_major_lines,
            "missing_declared_sdk_major_lines": missing_sdk_lines,
            "sdks": sdk_lines,
        },
        recommendation=(
            None
            if is_mise and not missing_sdk_lines
            else "Install the declared SDK lines through mise in a later approved step."
        ),
    )

    legacy_candidates = []
    for candidate in ("/usr/local/share/dotnet/dotnet", "/opt/homebrew/opt/dotnet/bin/dotnet",
                      "/opt/homebrew/opt/dotnet@8/bin/dotnet"):
        if Path(candidate).exists():
            legacy_candidates.append(path_provenance(candidate))
    if legacy_candidates:
        add_finding(
            findings,
            area="dotnet",
            classification="approval_gated_removal",
            name="dotnet.sdk_sources.legacy_present",
            severity="low",
            summary="Legacy .NET SDK source candidates are still present outside mise.",
            details={"candidates": legacy_candidates},
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
        ["dotnet", "tool", "list", "--global"], timeout=20, env=DOTNET_READ_ONLY_ENV
    )
    tool_rows = parse_dotnet_tool_rows(tool_result["stdout"]) if tool_result["stdout"] else []
    installed_tools = {row["package_id"] for row in tool_rows}
    declared_lc = {value.lower(): value for value in declared_tools}
    installed_lc = {value.lower(): value for value in installed_tools}
    missing_tools = sorted(declared_lc[key] for key in declared_lc.keys() - installed_lc.keys())
    undeclared_tools = sorted(installed_lc[key] for key in installed_lc.keys() - declared_lc.keys())
    add_finding(
        findings,
        area="dotnet",
        classification="canonical" if not missing_tools else "declared_absent",
        name="dotnet.global_tools.declared",
        severity="info" if not missing_tools else "medium",
        source=str(DOTNET_TOOLS.relative_to(ROOT)),
        summary=(
            f"{len(declared_tools) - len(missing_tools)}/{len(declared_tools)} declared "
            ".NET global tools appear installed."
        ),
        details={"installed": sorted(installed_tools), "missing": missing_tools},
        recommendation=(
            "A later install task can install missing declared .NET tools."
            if missing_tools
            else None
        ),
    )

    tool_commands = sorted({command for row in tool_rows for command in row.get("commands", [])})
    unavailable_commands = sorted(
        command for command in tool_commands if not shutil.which(command)
    )
    if installed_tools and unavailable_commands:
        add_finding(
            findings,
            area="dotnet",
            classification="drift",
            name="dotnet.global_tools.path",
            severity="medium",
            source=str(HOME / ".dotnet/tools"),
            summary=(
                f"{len(unavailable_commands)} installed .NET global tool commands "
                "are not directly visible on PATH."
            ),
            details={"unavailable_commands": unavailable_commands},
            recommendation="Ensure the shared PATH contract includes ~/.dotnet/tools.",
        )
    if undeclared_tools:
        add_finding(
            findings,
            area="dotnet",
            classification="present_undeclared",
            name="dotnet.global_tools.present_undeclared",
            severity="low",
            source=dotnet_path,
            summary=f"{len(undeclared_tools)} .NET global tools are installed but undeclared.",
            details={"tools": undeclared_tools},
            recommendation="Declare intentional .NET global tools or remove them behind a Reset Approval Gate.",
        )


# --- ai tool surface ---------------------------------------------------------


def check_apm_baseline(findings: list[dict[str, Any]]) -> None:
    manifest = parse_apm_manifest()
    lockfile = parse_apm_lockfile()

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
        return

    refs = [apm_ref_parts(ref) for ref in manifest["apm_refs"]]
    excluded_declared = sorted(
        {part["name"] for part in refs} & EXCLUDED_AI_ASSETS
    )
    manifest_ok = not manifest["parser_errors"] and not excluded_declared
    add_finding(
        findings,
        area="ai_tools",
        classification="canonical" if manifest_ok else "drift",
        name="ai_tools.apm_manifest",
        severity="info" if manifest_ok else "high",
        source="system/ai/apm/apm.yml",
        summary=(
            f"Repo APM manifest declares {len(refs)} baseline dependencies for "
            f"targets {manifest['targets']}."
            if manifest_ok
            else "Repo APM manifest has parse errors or declares excluded assets."
        ),
        details={
            "targets": manifest["targets"],
            "refs": manifest["apm_refs"],
            "parser_errors": manifest["parser_errors"],
            "excluded_assets_declared": excluded_declared,
        },
        recommendation=(
            None
            if manifest_ok
            else "Fix the manifest; excluded assets are listed in this doctor's policy constants (ADR-0003)."
        ),
    )

    if not lockfile["exists"]:
        add_finding(
            findings,
            area="ai_tools",
            classification="missing",
            name="ai_tools.apm_lockfile",
            severity="medium",
            summary="APM manifest exists, but apm.lock.yaml is missing.",
            recommendation="Create the lockfile only through an approved APM lock gate.",
        )
    else:
        locked_paths = [
            str(dep.get("virtual_path"))
            for dep in lockfile["dependencies"]
            if dep.get("virtual_path")
        ]
        expected_paths = [part["virtual_path"] for part in refs]
        missing_locks = sorted(set(expected_paths) - set(locked_paths))
        unexpected_locks = sorted(set(locked_paths) - set(expected_paths))
        unresolved = [
            dep
            for dep in lockfile["dependencies"]
            if not dep.get("resolved_commit") or dep.get("is_virtual") != "true"
        ]
        lock_ok = bool(
            not lockfile["parser_errors"]
            and not missing_locks
            and not unexpected_locks
            and not unresolved
        )
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical" if lock_ok else "drift",
            name="ai_tools.apm_lockfile",
            severity="info" if lock_ok else "high",
            source="system/ai/apm/apm.lock.yaml",
            summary=(
                "APM lockfile pins exactly the manifest dependency set."
                if lock_ok
                else "APM lockfile does not match the manifest dependency set."
            ),
            details={
                "locked_virtual_paths": sorted(locked_paths),
                "missing_locks": missing_locks,
                "unexpected_locks": unexpected_locks,
                "unresolved_dependencies": unresolved,
                "parser_errors": lockfile["parser_errors"],
                "resolved_commits": sorted(
                    {str(dep.get("resolved_commit")) for dep in lockfile["dependencies"] if dep.get("resolved_commit")}
                ),
            },
            recommendation=(
                None if lock_ok else "Re-lock through an approved APM lock gate so the lockfile matches apm.yml."
            ),
        )

    user_files = {
        "apm.yml": symlink_file_state(APM_USER_MANIFEST, APM_MANIFEST),
        "apm.lock.yaml": symlink_file_state(APM_USER_LOCKFILE, APM_LOCKFILE),
    }
    noncanonical = sorted(name for name, info in user_files.items() if not info["canonical"])
    add_finding(
        findings,
        area="ai_tools",
        classification="canonical" if not noncanonical else "drift",
        name="ai_tools.apm_user_project",
        severity="info" if not noncanonical else "medium",
        summary=(
            "Live APM project files are symlinked to the repo manifest and lockfile."
            if not noncanonical
            else "Live APM project files are not symlinked to the repo source files."
        ),
        details={"files": user_files, "noncanonical": noncanonical},
        recommendation=(
            None if not noncanonical else "Run just link to point ~/.apm at the repo source of truth."
        ),
    )

    expected_skills = sorted({part["name"] for part in refs if part["name"]})
    for target in manifest["targets"]:
        skills_dir = SKILL_DIRS_BY_TARGET.get(str(target))
        if skills_dir is None:
            add_finding(
                findings,
                area="ai_tools",
                classification="unknown",
                name=f"ai_tools.baseline.{target}",
                severity="low",
                summary=f"APM target {target} has no known skills directory mapping in this doctor.",
                recommendation="Add the target's skills directory to SKILL_DIRS_BY_TARGET.",
            )
            continue
        vendor_allowlist = CODEX_VENDOR_RUNTIME_SKILLS if target == "codex" else set()
        state = deployed_baseline_state(skills_dir, expected_skills, vendor_allowlist)
        if not state["exists"]:
            add_finding(
                findings,
                area="ai_tools",
                classification="migration_pending",
                name=f"ai_tools.baseline.{target}",
                severity="low",
                summary=f"{target} baseline target output is not deployed yet.",
                details=state,
                recommendation="Deploy target output only through an approved APM target-write gate.",
            )
        elif state["canonical"]:
            add_finding(
                findings,
                area="ai_tools",
                classification="canonical",
                name=f"ai_tools.baseline.{target}",
                summary=f"{target} has the approved APM-managed skill baseline.",
                details=state,
            )
        else:
            add_finding(
                findings,
                area="ai_tools",
                classification="drift",
                name=f"ai_tools.baseline.{target}",
                severity="medium",
                summary=f"{target} live skills do not match the manifest baseline.",
                details=state,
                recommendation=(
                    "Review live target output against the APM manifest and use an "
                    "approved deployment or cleanup gate for changes."
                ),
            )


def deployed_baseline_state(
    skills_dir: Path, expected_skills: list[str], vendor_allowlist: set[str]
) -> dict[str, Any]:
    state: dict[str, Any] = {
        "path": str(skills_dir),
        "exists": skills_dir.is_dir(),
        "expected_skills": expected_skills,
        "missing_skills": expected_skills,
        "skills_without_skill_md": [],
        "extra_skills": [],
        "excluded_present": [],
        "canonical": False,
    }
    if not skills_dir.is_dir():
        return state
    try:
        names = sorted(item.name for item in skills_dir.iterdir() if item.is_dir())
    except OSError:
        return state
    name_set = set(names)
    state["missing_skills"] = sorted(set(expected_skills) - name_set)
    state["skills_without_skill_md"] = sorted(
        name
        for name in expected_skills
        if name in name_set and not (skills_dir / name / "SKILL.md").is_file()
    )
    state["extra_skills"] = sorted(
        name_set - set(expected_skills) - vendor_allowlist - EXCLUDED_AI_ASSETS
    )
    state["excluded_present"] = sorted(name_set & EXCLUDED_AI_ASSETS)
    state["canonical"] = bool(
        not state["missing_skills"]
        and not state["skills_without_skill_md"]
        and not state["extra_skills"]
        and not state["excluded_present"]
    )
    return state


def check_claude_code(findings: list[dict[str, Any]], brew_declared: dict[str, set[str]]) -> None:
    declared_casks = brew_declared["cask"]
    cli_declared = "claude-code" in declared_casks or "claude-code@latest" in declared_casks
    active = shutil.which("claude")
    provenance = path_provenance(active)
    if active and provenance["source"] == "homebrew":
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="claude.command",
            summary="Claude Code active CLI resolves through the declared Homebrew cask.",
            details={"active_command": provenance},
        )
    elif active and cli_declared:
        add_finding(
            findings,
            area="ai_tools",
            classification="migration_pending",
            name="claude.command",
            severity="low",
            summary="Claude Code is declared in the Brewfile, but the active CLI is still manual-local.",
            details={"active_command": provenance, "declared": cli_declared},
            recommendation=(
                "Migrate Claude Code to the Homebrew cask in a separate approved reinstall task."
            ),
        )
    elif active:
        add_finding(
            findings,
            area="ai_tools",
            classification="managed_exception",
            name="claude.command",
            severity="low",
            summary="Claude Code active CLI is present, but no repo-owned installer is declared.",
            details={"active_command": provenance},
            recommendation="Declare a Claude Code installer before cleanup or migration.",
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="declared_absent" if cli_declared else "missing",
            name="claude.command",
            severity="low",
            summary="Claude Code active CLI is not present on PATH.",
            recommendation="Install Claude Code only through a separate approved Homebrew task.",
        )

    if CLAUDE_VERSIONS_DIR.is_dir() and path_exists_or_symlink(CLAUDE_COMMAND):
        try:
            active_version = CLAUDE_COMMAND.resolve(strict=False).name
            old_versions = sorted(
                item.name
                for item in CLAUDE_VERSIONS_DIR.iterdir()
                if not item.name.startswith(".") and item.name != active_version
            )
        except OSError:
            old_versions = []
        if old_versions:
            add_finding(
                findings,
                area="ai_tools",
                classification="approval_gated_removal",
                name="claude.versions.cleanup_candidates",
                severity="low",
                summary="Older Claude Code versioned executable artifacts are present.",
                details={
                    "versions_path": str(CLAUDE_VERSIONS_DIR),
                    "old_versions": old_versions,
                },
                recommendation=(
                    "Remove older Claude Code artifacts only in a separate cleanup task with explicit approval."
                ),
            )


def check_ai_commands(findings: list[dict[str, Any]], brew_declared: dict[str, set[str]]) -> None:
    detected = {
        command: [path_provenance(path) for path in which_all(command)]
        for command in AI_COMMANDS
        if which_all(command)
    }
    if detected:
        # Homebrew and pnpm are the declared installers for AI CLIs
        # (system/ai/README.md); anything else is a managed exception.
        undeclared_sources = sorted(
            {
                str(info.get("source"))
                for paths in detected.values()
                for info in paths
                if info.get("source") not in {"homebrew", "pnpm"}
            }
        )
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical" if not undeclared_sources else "managed_exception",
            name="ai_tools.path",
            severity="info" if not undeclared_sources else "low",
            summary=(
                "All AI Tool Surface commands resolve through declared installers."
                if not undeclared_sources
                else "Some AI Tool Surface commands resolve outside the declared installers."
            ),
            details={"commands": detected, "undeclared_sources": undeclared_sources},
            recommendation=(
                None
                if not undeclared_sources
                else "Declare or clean up each manual CLI through its own tool-surface policy."
            ),
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="unknown",
            name="ai_tools.path",
            summary="No codex, claude, opencode, pi, or apm commands were found on PATH.",
        )

    check_claude_code(findings, brew_declared)

    opencode = shutil.which("opencode")
    opencode_declared = equivalent_member("opencode", brew_declared["brew"])
    if opencode and path_source(opencode) == "homebrew" and opencode_declared:
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical",
            name="opencode.command",
            summary="opencode active CLI resolves through the declared Homebrew formula.",
            details={"active_command": path_provenance(opencode)},
        )
    elif opencode:
        add_finding(
            findings,
            area="ai_tools",
            classification="managed_exception",
            name="opencode.command",
            severity="low",
            summary="opencode CLI is present, but not through the declared Homebrew formula.",
            details={"active_command": path_provenance(opencode), "declared": opencode_declared},
            recommendation="Declare the selected opencode installer or migrate the CLI behind an approved cleanup task.",
        )
    elif opencode_declared:
        add_finding(
            findings,
            area="ai_tools",
            classification="declared_absent",
            name="opencode.command",
            severity="low",
            summary="opencode is declared in the Brewfile but is not on PATH.",
            recommendation="Install opencode through the declared Homebrew formula.",
        )

    pi = shutil.which("pi")
    if pi:
        pi_source = path_source(pi)
        add_finding(
            findings,
            area="ai_tools",
            classification="canonical" if pi_source == "pnpm" else "managed_exception",
            name="pi.command",
            severity="info" if pi_source == "pnpm" else "low",
            summary=(
                "Pi CLI resolves through the canonical pnpm global path."
                if pi_source == "pnpm"
                else f"Pi CLI is present via {pi_source}, not the canonical pnpm global path."
            ),
            details={"active_command": path_provenance(pi)},
            recommendation=(
                None
                if pi_source == "pnpm"
                else "Install Pi through the declared pnpm global manifest."
            ),
        )

    apm_paths = which_all("apm")
    if apm_paths:
        primary = path_provenance(apm_paths[0])
        manual_paths = [
            path_provenance(path)
            for path in apm_paths
            if path_source(path) in {"manual/pkg", "manual/local"}
        ]
        if primary.get("source") == "homebrew":
            add_finding(
                findings,
                area="ai_tools",
                classification="canonical",
                name="apm.command",
                summary="apm resolves through the declared Homebrew formula.",
                details={"primary": primary, "legacy_manual_paths": manual_paths},
            )
            if manual_paths:
                add_finding(
                    findings,
                    area="ai_tools",
                    classification="approval_gated_removal",
                    name="apm.command.legacy_manual_duplicate",
                    severity="low",
                    summary="A legacy manual APM binary is still present after Homebrew migration.",
                    details={"paths": manual_paths},
                    recommendation="Remove the legacy APM install only in a separate cleanup task.",
                )
        else:
            add_finding(
                findings,
                area="ai_tools",
                classification="managed_exception",
                name="apm.command",
                severity="low",
                summary="apm is present but does not resolve through Homebrew.",
                details={"primary": primary},
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

    check_apm_baseline(findings)


# --- manual apps -------------------------------------------------------------


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
            if not is_dev_related(item.name):
                continue
            if item.is_symlink() and not item.exists():
                # Dangling symlinks fail the executable check but are still
                # drift: a leftover pointing at an uninstalled tool.
                tools.append(
                    {
                        "name": item.name,
                        "path": str(item),
                        "resolved_source": "dangling_symlink",
                        "link_target": os.readlink(item),
                    }
                )
                continue
            if not os.access(item, os.X_OK):
                continue
            source = path_source(str(item))
            if source == "homebrew":
                continue
            tools.append({"name": item.name, "path": str(item), "resolved_source": source})
    except OSError:
        return tools
    return sorted(tools, key=lambda item: item["name"].lower())


def check_manual_apps(
    findings: list[dict[str, Any]],
    brew_declared: dict[str, set[str]],
) -> None:
    add_manifest_presence(findings, "manual_apps", MANUAL_APPS, "manual apps")
    manual_declared = parse_manual_apps(MANUAL_APPS)

    installed_cask_norms: set[str] = set()
    cask_result = command_result(["brew", "list", "--cask"]) if shutil.which("brew") else None
    if cask_result and cask_result["ok"]:
        installed_cask_norms = {normalize_app_name(value) for value in lines(cask_result["stdout"])}
    declared_cask_norms = {normalize_app_name(value) for value in brew_declared["cask"]}

    apps = scan_applications([Path("/Applications"), HOME / "Applications"])
    manual_dev_apps = []
    for app in apps:
        normalized = normalize_app_name(app["name"])
        if normalized in installed_cask_norms or normalized in declared_cask_norms:
            continue
        if normalized in manual_declared:
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
            recommendation=(
                "Declare intentional manual apps in system/packages/manual-apps.md "
                "or move them to a canonical installer."
            ),
        )
    else:
        add_finding(
            findings,
            area="manual_apps",
            classification="canonical",
            name="manual_apps.applications",
            source="/Applications, ~/Applications",
            summary="No obvious manual dev applications were detected outside declared Homebrew casks.",
        )

    bin_tools = scan_bin_dir(Path("/usr/local/bin")) + scan_bin_dir(HOME / ".local/bin")
    # Dangling symlinks are incomplete removals; a manual-apps.md mention
    # documents history but does not exempt the leftover link itself.
    dangling = [tool for tool in bin_tools if tool["resolved_source"] == "dangling_symlink"]
    bin_tools = [tool for tool in bin_tools if tool["resolved_source"] != "dangling_symlink"]
    if dangling:
        add_finding(
            findings,
            area="manual_apps",
            classification="approval_gated_removal",
            name="manual_apps.dangling_symlinks",
            severity="low",
            source="/usr/local/bin, ~/.local/bin",
            summary=f"{len(dangling)} dangling dev-tool symlink(s) point at removed targets.",
            details={"tools": dangling},
            recommendation=(
                "Remove the dead links (root-owned ones need sudo, e.g. "
                "sudo rm /usr/local/bin/<name>)."
            ),
        )
    unknown_bin_tools = [
        tool
        for tool in bin_tools
        if normalize_app_name(tool["name"]) not in manual_declared
        and normalize_app_name(Path(tool["path"]).name) not in manual_declared
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
        )


# --- payload and output ------------------------------------------------------


def build_payload() -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    brew_declared = check_brew(findings)
    check_js_toolchain(findings)
    check_vscode_extensions(findings)
    pnpm_installed = check_pnpm(findings)
    check_npm(findings, set(clean_manifest_lines(PNPM_GLOBAL)), pnpm_installed)
    check_fnm(findings, brew_declared)
    check_runtime_managers(findings)
    check_shell_contract(findings)
    check_dotnet(findings)
    check_ai_commands(findings, brew_declared)
    check_manual_apps(findings, brew_declared)

    by_classification = Counter(finding["classification"] for finding in findings)
    by_area = Counter(finding["area"] for finding in findings)
    return {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(ROOT),
        "read_only": True,
        "execution_context": {
            "python_executable": sys.executable,
            "shell": os.environ.get("SHELL"),
            "path_entries": [
                entry for entry in os.environ.get("PATH", "").split(os.pathsep) if entry
            ],
        },
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


DETAIL_KEYS = (
    "missing",
    "packages",
    "tools",
    "formulae",
    "casks",
    "extensions",
    "apps",
    "commands",
    "installed_versions",
)


def emit_finding_lines(finding: dict[str, Any], fix_label: str) -> None:
    details = finding.get("details", {})
    interesting = [
        f"{key}: {format_items(details[key])}"
        for key in DETAIL_KEYS
        if key in details and details[key]
    ]
    if interesting:
        print(f"  - details: {'; '.join(interesting)}")
    if finding.get("recommendation"):
        print(f"  - {fix_label}: {finding['recommendation']}")


def emit_full_markdown(payload: dict[str, Any]) -> None:
    print("# Development Ecosystem Doctor")
    print()
    print(f"- Repo: `{payload['repo_root']}`")
    print("- Mode: read-only audit; no installs, uninstalls, migrations, backups, or rewrites")
    print(f"- Findings: {payload['summary']['total_findings']}")
    counts = payload["summary"]["by_classification"]
    print("- Classifications: " + ", ".join(f"{key}={value}" for key, value in counts.items()))

    context = payload["execution_context"]
    print()
    print("## execution-context")
    print(f"- `SHELL`: `{context.get('shell')}`")
    print(f"- Python executable: `{context.get('python_executable')}`")
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
            emit_finding_lines(finding, "later")


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
            emit_finding_lines(finding, "fix")

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
