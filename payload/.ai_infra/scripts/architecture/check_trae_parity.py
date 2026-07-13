"""
File: check_trae_parity.py
Path: .ai_infra/scripts/architecture/check_trae_parity.py
Role: Verify .trae/ contract plane matches SSOT (Trae edition or .cursor/ dual-IDE).
Used By:
 - verify_all.py
 - Makefile gates (kit-dev)
Depends On:
 - .ai_infra/scripts/release/sync_trae_contract.py
 - .ai_infra/ide_contract_paths.py
Notes:
 - Regenerates expected .trae/ to temp and structural-compares with committed tree.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

for _candidate in (Path(__file__).resolve(), *Path(__file__).resolve().parents):
    bootstrap = _candidate / ".ai_infra" / "bootstrap.py"
    if bootstrap.is_file():
        if str(_candidate / ".ai_infra") not in sys.path:
            sys.path.insert(0, str(_candidate / ".ai_infra"))
        from bootstrap import ensure_paths_import

        ROOT = ensure_paths_import(__file__)
        break
else:
    raise RuntimeError("kit root not found above check_trae_parity.py")

from ide_contract_paths import uses_trae_ssot  # noqa: E402
from paths import kit_root_from_script

ROOT = kit_root_from_script(__file__)
RELEASE = ROOT / ".ai_infra" / "scripts" / "release"
if str(RELEASE) not in sys.path:
    sys.path.insert(0, str(RELEASE))

import sync_trae_contract  # noqa: E402


def _skill_folder_names(skills_dir: Path) -> set[str]:
    if not skills_dir.is_dir():
        return set()
    return {p.name for p in skills_dir.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}


def _rule_body_normalized(path: Path) -> str:
    return _rule_body_normalized_text(path.read_text(encoding="utf-8"))


def _rule_body_normalized_text(text: str) -> str:
    if text.startswith("<!-- GENERATED"):
        end = text.find("-->")
        if end != -1:
            text = text[end + 3 :].lstrip("\n")
    return text


def _compare_trae_trees(expected: Path, actual: Path, errors: list[str], *, prefix: str = "") -> None:
    for rel in ("rules", "skills", "agents", "mcp.json"):
        src = expected / rel
        dst = actual / rel
        if src.is_file() and dst.is_file():
            if src.read_bytes() != dst.read_bytes():
                errors.append(f"{prefix}regen drift file: .trae/{rel}")
        elif src.is_dir() and dst.is_dir():
            for path in sorted(src.rglob("*")):
                if path.is_file():
                    rel_path = path.relative_to(src)
                    other = dst / rel_path
                    if not other.is_file() or path.read_bytes() != other.read_bytes():
                        errors.append(f"{prefix}regen drift: .trae/{rel}/{rel_path}")
                        break


def _run_trae_ssot_checks(kit_root: Path, trae_dir: Path) -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="trae-parity-") as tmp:
        tmp_trae = Path(tmp) / ".trae"
        sync_trae_contract.sync_trae_contract(kit_root, tmp_trae, profile="default")
        _compare_trae_trees(tmp_trae, trae_dir, errors)
    return errors


def _run_cursor_ssot_checks(kit_root: Path, trae_dir: Path) -> list[str]:
    errors: list[str] = []
    cursor_rules = kit_root / ".cursor" / "rules"
    cursor_skills = kit_root / ".cursor" / "skills"
    cursor_agents = kit_root / ".cursor" / "agents"

    expected_rule_stems = sync_trae_contract.expected_rule_basenames(cursor_rules)
    expected_agent_rule_stems = sync_trae_contract.expected_agent_rule_basenames(cursor_agents)
    trae_rules = trae_dir / "rules"
    actual_rule_stems = {p.stem for p in trae_rules.glob("*.md")} if trae_rules.is_dir() else set()

    missing_rules = (expected_rule_stems | expected_agent_rule_stems) - actual_rule_stems
    if missing_rules:
        errors.append(f".trae/rules missing stems: {sorted(missing_rules)[:8]}")

    cursor_skill_names = _skill_folder_names(cursor_skills)
    maintainer = kit_root / ".agents" / "skills"
    cursor_skill_names |= _skill_folder_names(maintainer)
    trae_skill_names = _skill_folder_names(trae_dir / "skills")
    if cursor_skill_names != trae_skill_names:
        errors.append(
            f"skill folder mismatch cursor={sorted(cursor_skill_names)[:6]} "
            f"trae={sorted(trae_skill_names)[:6]}"
        )

    for mdc in sorted(cursor_rules.glob("*.mdc")):
        trae_rule = trae_rules / f"{mdc.stem}.md"
        if not trae_rule.is_file():
            errors.append(f"missing .trae/rules/{mdc.stem}.md")
            continue
        expected_body = _rule_body_normalized_text(
            sync_trae_contract.transform_rule_mdc_to_md(mdc.read_text(encoding="utf-8"))
        )
        trae_body = _rule_body_normalized(trae_rule)
        if expected_body != trae_body:
            errors.append(f"rule body drift: {mdc.stem}")

    with tempfile.TemporaryDirectory(prefix="trae-parity-") as tmp:
        tmp_trae = Path(tmp) / ".trae"
        sync_trae_contract.sync_trae_contract(kit_root, tmp_trae)
        _compare_trae_trees(tmp_trae, trae_dir, errors)

    return errors


def run_checks(root: Path | None = None, *, profile: str = "default") -> list[str]:
    kit_root = (root or ROOT).resolve()
    trae_dir = kit_root / ".trae"

    if not trae_dir.is_dir():
        return [".trae/ missing — run: make sync-plugin"]

    if uses_trae_ssot(kit_root, profile):
        return _run_trae_ssot_checks(kit_root, trae_dir)
    return _run_cursor_ssot_checks(kit_root, trae_dir)


def main() -> int:
    errors = run_checks()
    if errors:
        print("check_trae_parity FAILED:")
        for err in errors:
            print(f" - {err}")
        return 1
    print("check_trae_parity PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
