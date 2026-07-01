#!/usr/bin/env python3
"""Read-only Development Ecosystem doctor for this Orchestrator Repo."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

BREWFILE = ROOT / "system/packages/Brewfile"
VSCODE_EXTENSIONS = ROOT / "system/packages/vscode-extensions.txt"
CURSOR_EXTENSIONS = ROOT / "system/packages/cursor-extensions.txt"
PNPM_GLOBAL = ROOT / "system/packages/pnpm-global.txt"
DOTNET_TOOLS = ROOT / "system/packages/dotnet-tools.txt"
MANUAL_APPS = ROOT / "system/packages/manual-apps.md"
NUSHELL_CONFIG = ROOT / "system/nushell/config.nu"
NUSHELL_ENV = ROOT / "system/nushell/env.nu"
DOTNET_READ_ONLY_ENV = {
    **os.environ,
    "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
    "DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE": "1",
    "DOTNET_NOLOGO": "1",
    "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
}

AREA_ORDER = [
    "brew",
    "js_toolchain",
    "vscode",
    "cursor",
    "pnpm",
    "npm",
    "fnm",
    "runtime_managers",
    "dotnet",
    "ai_tools",
    "manual_apps",
    "other",
]

SHELL_NAMES = {"bash", "fish", "nu", "nushell", "sh", "zsh"}
JS_COMMANDS = ["node", "npm", "npx", "pnpm", "corepack"]

DEV_RE = re.compile(
    r"(ai|apm|ast-grep|aws|azure|bash|biome|bun|cargo|cdk|clang|claude|"
    r"cmake|codex|colima|composer|ctags|cursor|deno|docker|dotenv|dotnet|"
    r"editorconfig|eslint|fd|ffmpeg|fnm|gcloud|gh|git|gitleaks|go|gradle|"
    r"graphviz|helm|jenv|jq|just|kotlin|kubectl|kubernetes|lambda|llm|lua|"
    r"mise|mysql|node|npm|nu|nushell|nvm|ollama|opencode|pnpm|podman|"
    r"poppler|postman|pycharm|pyenv|python|rbenv|redis|ripgrep|ripsecrets|"
    r"ruby|rust|rustup|sdkman|semgrep|serverless|shell|terraform|tmux|"
    r"typescript|unbound|uv|vim|volta|vscode|watchman|xcode|yarn|zsh)"
)

DEV_APP_RE = re.compile(
    r"(android studio|chatgpt atlas|codex|cursor|datagrip|docker|ghostty|"
    r"intellij|iterm|leapp|postman|pycharm|rider|session manager plugin|"
    r"sublime|tableplus|visual studio code|warp|webstorm|xcode)",
    re.IGNORECASE,
)

AI_COMMANDS = ["codex", "claude", "opencode", "open-code", "pi", "apm"]
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
        apps.add(normalize_app_name(value))
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
    if resolved.startswith("/opt/homebrew/") or "/opt/homebrew/Cellar/" in resolved:
        return with_source("homebrew")
    if resolved.startswith("/usr/local/Homebrew/") or "/usr/local/Cellar/" in resolved:
        return with_source("homebrew")
    if resolved.startswith(f"{home}/.local/share/mise") or original.startswith(
        f"{home}/.local/share/mise"
    ):
        return with_source("mise")
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
    nu_env = {key: value for key, value in sorted(os.environ.items()) if key.startswith("NU_")}
    chain = parent_process_chain()
    parent_shells = [
        item.get("basename")
        for item in chain
        if isinstance(item.get("basename"), str)
        and str(item["basename"]).lower() in SHELL_NAMES
    ]
    shell_env = os.environ.get("SHELL")
    shell_env_name = Path(shell_env).name if shell_env else None
    appears_from_nushell = bool(nu_env) or any(
        str(item.get("basename", "")).lower() in {"nu", "nushell"} for item in chain
    )
    return {
        "pid": os.getpid(),
        "python_executable": sys.executable,
        "argv": sys.argv,
        "path": path_raw,
        "path_entries": path_entries,
        "shell_env": shell_env,
        "shell_env_name": shell_env_name,
        "nu_env": nu_env,
        "parent_process_chain": chain,
        "detected_parent_shells": parent_shells,
        "appears_running_from_nushell": appears_from_nushell,
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
    path_entries = [pnpm_home]
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

    undeclared_formulae = sorted(
        name
        for name in installed_leaves
        if not equivalent_member(name, declared["brew"]) and is_dev_related(name)
    )
    undeclared_casks = sorted(
        name
        for name in installed_casks
        if not equivalent_member(name, declared["cask"]) and is_dev_related(name)
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
        legacy_globals = sorted(installed - set(duplicate_with_pnpm))
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

        add_finding(
            findings,
            area="npm",
            classification=classification,
            name=f"npm.globals.{scope['scope']}",
            severity="medium" if trusted and installed else "low",
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


def model_nushell_fnm_config() -> dict[str, Any]:
    config_text = NUSHELL_CONFIG.read_text(encoding="utf-8") if NUSHELL_CONFIG.exists() else ""
    env_text = NUSHELL_ENV.read_text(encoding="utf-8") if NUSHELL_ENV.exists() else ""
    checks = {
        "config_exists": NUSHELL_CONFIG.exists(),
        "env_exists": NUSHELL_ENV.exists(),
        "config_calls_fnm_env_json": "fnm env --json" in config_text,
        "config_loads_fnm_env": "load-env" in config_text and "fnm env --json" in config_text,
        "config_prepends_fnm_multishell_bin": "FNM_MULTISHELL_PATH" in config_text
        and "prepend" in config_text,
        "config_has_pwd_hook": "hooks.env_change.PWD" in config_text,
        "config_hook_can_install_on_cd": "--install-if-missing" in config_text,
        "env_declares_pnpm_home": "PNPM_HOME" in env_text,
    }
    configured = all(
        checks[key]
        for key in (
            "config_exists",
            "config_calls_fnm_env_json",
            "config_loads_fnm_env",
            "config_prepends_fnm_multishell_bin",
        )
    )
    return {
        "configured": configured,
        "checks": checks,
        "config_path": str(NUSHELL_CONFIG),
        "env_path": str(NUSHELL_ENV),
        "method": "static read-only model of repo Nushell files; does not source config.nu",
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
            "scope": "current process PATH only; not a login-shell or Nushell assertion",
        },
    )

    model = model_nushell_fnm_config()
    add_finding(
        findings,
        area="fnm",
        classification="canonical" if model["configured"] else "unknown",
        name="fnm.nushell_configured",
        source=str(NUSHELL_CONFIG.relative_to(ROOT)),
        severity="info" if model["configured"] else "low",
        summary=(
            "Repo Nushell config is modeled as configuring fnm."
            if model["configured"]
            else "Repo Nushell config is not modeled as fully configuring fnm."
        ),
        details=model,
        recommendation=(
            "Check system/nushell/config.nu before treating fnm as configured for Nushell."
            if not model["configured"]
            else None
        ),
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


def check_dotnet(findings: list[dict[str, Any]]) -> None:
    add_manifest_presence(findings, "dotnet", DOTNET_TOOLS, ".NET global tool")
    declared = set(clean_manifest_lines(DOTNET_TOOLS))
    dotnet_path = shutil.which("dotnet")
    if not dotnet_path:
        add_finding(
            findings,
            area="dotnet",
            classification="unknown",
            name="dotnet.command",
            severity="medium",
            summary="dotnet is not on PATH; SDKs and global tools were not audited.",
            recommendation=(
                "Use the ADR-0006 mise .NET SDK source and dotnet tool manifest "
                "as desired state."
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
    candidates = [
        dotnet_inventory(candidate)
        for candidate in dotnet_candidate_paths(dotnet_path)
    ]
    add_finding(
        findings,
        area="dotnet",
        classification="canonical" if active_source == "mise_dotnet" else "unknown",
        name="dotnet.sdk_source",
        source=dotnet_path,
        severity="info" if active_source == "mise_dotnet" else "medium",
        summary=f"dotnet is present from {active_source}.",
        details={
            "active": active_inventory,
            "candidates": candidates,
            "path_matches": [path_provenance(path) for path in which_all("dotnet")],
            "provenance": provenance,
            "runtimes": active_inventory["runtimes"],
            "sdks": sdk_lines,
            "workloads": active_inventory["workloads"],
        },
        recommendation=(
            "Compare this active SDK source with ADR-0006 before removing any .NET installation."
            if active_source != "mise_dotnet"
            else None
        ),
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


def scan_ai_tools(findings: list[dict[str, Any]]) -> None:
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
            classification="present_undeclared",
            name="ai_tools.path",
            severity="low",
            summary="AI/dev CLI commands were found on PATH, but no canonical AI package source is declared yet.",
            details={"commands": detected_details},
            recommendation="When the AI Asset Manager is selected, declare intentional AI Tool Surface CLIs and assets.",
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="unknown",
            name="ai_tools.path",
            summary="No codex, claude, opencode, pi, apm, or obvious variants were found on PATH.",
        )

    apm_paths = which_all("apm")
    if apm_paths:
        add_finding(
            findings,
            area="ai_tools",
            classification="unknown",
            name="apm.command",
            severity="low",
            summary="apm is present, but the canonical AI Asset Manager has not been selected.",
            details={"paths": [path_provenance(path) for path in apm_paths]},
            recommendation="Document whether this apm is the intended AI Asset Manager or an unrelated legacy tool.",
        )
    else:
        add_finding(
            findings,
            area="ai_tools",
            classification="unknown",
            name="apm.command",
            summary="apm is not on PATH.",
        )


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
    for app in apps:
        normalized = normalize_app_name(app["name"])
        if normalized in installed_cask_norms or normalized in declared_cask_norms:
            canonical_apps.append(app)
            continue
        if normalized in manual_declared or DEV_APP_RE.search(app["name"]):
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
            details={"canonical_app_count": len(canonical_apps)},
        )

    bin_tools = scan_bin_dir(Path("/usr/local/bin")) + scan_bin_dir(HOME / ".local/bin")
    if bin_tools:
        add_finding(
            findings,
            area="manual_apps",
            classification="manual",
            name="manual_apps.bin_tools",
            severity="low",
            source="/usr/local/bin, ~/.local/bin",
            summary="Manual dev-related executables were detected in local bin directories.",
            details={"tools": bin_tools[:80], "truncated": len(bin_tools) > 80},
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
    compare_extensions(
        findings,
        area="cursor",
        command="cursor",
        manifest=CURSOR_EXTENSIONS,
        label="Cursor",
    )
    pnpm_installed = check_pnpm(findings, js_commands)
    check_npm(findings, set(clean_manifest_lines(PNPM_GLOBAL)), pnpm_installed, js_commands)
    check_fnm(findings, brew_declared)
    check_runtime_managers(findings)
    check_dotnet(findings)
    scan_ai_tools(findings)
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


def emit_markdown(payload: dict[str, Any]) -> None:
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
    print(f"- Appears running from Nushell: `{context.get('appears_running_from_nushell')}`")
    parent_shells = context.get("detected_parent_shells") or []
    print(f"- Detected parent/current shells: `{', '.join(parent_shells) if parent_shells else 'none'}`")
    print(f"- Python executable: `{context.get('python_executable')}`")
    print("- Parent process chain:")
    for item in context.get("parent_process_chain", []):
        pid = item.get("pid")
        ppid = item.get("ppid")
        command = item.get("command") or item.get("basename") or "unknown"
        print(f"  - pid={pid} ppid={ppid} command=`{command}`")
    nu_env = context.get("nu_env", {})
    if nu_env:
        print("- `NU_*` signals:")
        for key, value in nu_env.items():
            print(f"  - `{key}`=`{value}`")
    else:
        print("- `NU_*` signals: none")
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only audit of this dotfiles Development Ecosystem."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of markdown.",
    )
    args = parser.parse_args()

    payload = build_payload()
    if args.json:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        print()
    else:
        emit_markdown(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
