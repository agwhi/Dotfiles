#!/usr/bin/env python3
"""Tests for doctor.py's hand-rolled parsers. Stdlib only; exits non-zero on failure."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "doctor", Path(__file__).resolve().parent / "doctor.py"
)
doctor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(doctor)

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: object = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}: {detail}")
        FAILURES.append(name)


# --- apm_ref_parts -----------------------------------------------------------

parts = doctor.apm_ref_parts("mattpocock/skills/skills/engineering/grill-with-docs#v1.0.1")
check("ref repo_url", parts["repo_url"] == "mattpocock/skills", parts)
check("ref virtual_path", parts["virtual_path"] == "skills/engineering/grill-with-docs", parts)
check("ref name", parts["name"] == "grill-with-docs", parts)
check("ref requested_ref", parts["requested_ref"] == "v1.0.1", parts)

# --- real APM manifest and lockfile -----------------------------------------

manifest = doctor.parse_apm_manifest()
check("manifest parses", not manifest["parser_errors"], manifest["parser_errors"])
check("manifest targets", manifest["targets"] == ["codex", "claude", "opencode"], manifest["targets"])
check("manifest has refs", len(manifest["apm_refs"]) >= 1, manifest["apm_refs"])

lockfile = doctor.parse_apm_lockfile()
check("lockfile parses", not lockfile["parser_errors"], lockfile["parser_errors"])
check(
    "lockfile covers manifest",
    {doctor.apm_ref_parts(r)["virtual_path"] for r in manifest["apm_refs"]}
    == {d.get("virtual_path") for d in lockfile["dependencies"]},
    lockfile["dependencies"],
)
check(
    "lockfile resolved",
    all(d.get("resolved_commit") for d in lockfile["dependencies"]),
    lockfile["dependencies"],
)

# --- malformed manifest produces errors, not a crash -------------------------

with tempfile.TemporaryDirectory() as tmp:
    bad = Path(tmp) / "apm.yml"
    bad.write_text("targets: [inline, unsupported]\ndependencies:\n  npm:\n    - x\n")
    original = doctor.APM_MANIFEST
    doctor.APM_MANIFEST = bad
    try:
        malformed = doctor.parse_apm_manifest()
    finally:
        doctor.APM_MANIFEST = original
    check("malformed manifest errors", bool(malformed["parser_errors"]), malformed)

# --- parse_manual_apps ignores the Completed Cleanup history section ---------

with tempfile.TemporaryDirectory() as tmp:
    manual = Path(tmp) / "manual-apps.md"
    manual.write_text(
        "# Manual Apps\n\n"
        "## Manual Or Local Tool State\n\n"
        "- `keeper`: intentionally manual tool.\n\n"
        "## Completed Cleanup\n\n"
        "- Homebrew `ghost`: removed on 2026-07-07.\n\n"
        "## Intentional Exclusions\n\n"
        "- `bystander`: outside the baseline for now.\n"
    )
    exempt = doctor.parse_manual_apps(manual)
    check("exemption kept", "keeper" in exempt, exempt)
    check("exclusion kept", "bystander" in exempt, exempt)
    check("history not exempt", "ghost" not in exempt, exempt)

# ------------------------------------------------------------------------------

if FAILURES:
    print(f"\n{len(FAILURES)} test(s) failed")
    raise SystemExit(1)
print("\nall doctor parser tests passed")
