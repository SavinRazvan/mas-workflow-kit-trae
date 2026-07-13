"""
File: sync_plugin_bundle.py
Path: .ai_infra/scripts/release/sync_plugin_bundle.py
Role: Build and verify Trae edition activate payload (payload/.trae + payload/trae_workflow).
Used By:
 - Makefile sync-plugin / check-plugin
Depends On:
 - .ai_infra/manifest.yaml
 - .ai_infra/bootstrap.py
Notes:
 - payload/ is the ADR-001 install source tree for `trae_workflow activate`.
 - Committed payload/ must match sources — run `make sync-plugin` after contract changes.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

for _candidate in (Path(__file__).resolve(), *Path(__file__).resolve().parents):
    bootstrap = _candidate / ".ai_infra" / "bootstrap.py"
    if bootstrap.is_file():
        if str(_candidate / ".ai_infra") not in sys.path:
            sys.path.insert(0, str(_candidate / ".ai_infra"))
        from bootstrap import ensure_paths_import

        KIT_ROOT = ensure_paths_import(__file__)
        break
else:
    raise RuntimeError("kit root not found above sync_plugin_bundle.py")

from paths import ai_infra_dir

MANIFEST_PATH = ai_infra_dir() / "manifest.yaml"
PAYLOAD_DIR = KIT_ROOT / "payload"
TRAE_WORKFLOW_SRC = KIT_ROOT / "trae_workflow"
PAYLOAD_EXTRA_AI_INFRA = ("install/trae_workflow", "scripts/install")
LICENSE_FILES = ("LICENSE", "NOTICE")

_SKIP_DIR_NAMES = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache"})
_SKIP_FILE_SUFFIXES = (".pyc", ".pyo")


def _ignore_bundle_artifacts(_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in _SKIP_DIR_NAMES or name.endswith(_SKIP_FILE_SUFFIXES):
            ignored.add(name)
    return ignored


def _is_bundle_artifact(path: Path) -> bool:
    return any(part in _SKIP_DIR_NAMES for part in path.parts) or path.suffix in _SKIP_FILE_SUFFIXES


def _load_manifest() -> dict[str, Any]:
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "profiles" not in data:
        raise RuntimeError(f"invalid manifest: {MANIFEST_PATH}")
    return data


def _resolve_profile(manifest: dict[str, Any], name: str) -> dict[str, Any]:
    profiles = manifest["profiles"]
    if name not in profiles:
        raise ValueError(f"unknown profile: {name}")
    raw = profiles[name]
    if "extends" not in raw:
        return raw
    base = _resolve_profile(manifest, raw["extends"])
    merged: dict[str, Any] = {
        "copy_dirs": list(base.get("copy_dirs", [])),
        "copy_ai_infra": list(base.get("copy_ai_infra", [])),
        "copy_files": list(base.get("copy_files", [])),
    }
    for key in ("copy_dirs", "copy_ai_infra", "copy_files"):
        merged[key] = merged[key] + list(raw.get(key, []))
    if "copy_dirs_replace" in raw:
        merged["copy_dirs"] = list(raw["copy_dirs_replace"])
    return merged


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _copy_tree(src: Path, dst: Path, *, ignore: Any | None = None) -> None:
    if not src.is_dir():
        raise FileNotFoundError(f"missing source directory: {src}")
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=ignore or _ignore_bundle_artifacts)


def _load_consumer_bundle_paths() -> Any:
    arch = KIT_ROOT / ".ai_infra" / "scripts" / "architecture"
    arch_str = str(arch)
    if arch_str not in sys.path:
        sys.path.insert(0, arch_str)
    import consumer_bundle_paths

    return consumer_bundle_paths


def _copy_ai_infra_rel(ai_src: Path, ai_dst: Path, rel: str) -> None:
    src = ai_src / rel
    dst = ai_dst / rel
    cbp = _load_consumer_bundle_paths()
    if cbp.is_local_workspace_copy(rel):
        _copy_tree(src, dst, ignore=cbp.ignore_local_workspace_ci)
        return
    if cbp.is_operations_copy(rel):
        _copy_tree(src, dst, ignore=cbp.ignore_operations_maintainer)
        return
    _copy_tree(src, dst)


def _copy_file(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise FileNotFoundError(f"missing source file: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def sync_payload(payload_dir: Path, _plugin_dir: Path, profile: str = "default") -> None:
    manifest = _load_manifest()
    spec = _resolve_profile(manifest, profile)
    ai_src = KIT_ROOT / ".ai_infra"
    ai_dst = payload_dir / ".ai_infra"

    if payload_dir.exists():
        shutil.rmtree(payload_dir)
    payload_dir.mkdir(parents=True)

    for rel in spec.get("copy_ai_infra", []):
        _copy_ai_infra_rel(ai_src, ai_dst, rel)

    for rel in PAYLOAD_EXTRA_AI_INFRA:
        _copy_tree(ai_src / rel, ai_dst / rel)

    agents_stub = ai_src / "templates" / "AGENTS.stub.md"
    if agents_stub.is_file():
        _copy_file(agents_stub, ai_dst / "templates" / "AGENTS.stub.md")

    for rel in spec.get("copy_files", []):
        if rel == "requirements-mcp.txt":
            _copy_file(KIT_ROOT / rel, payload_dir / rel)
        else:
            _copy_file(ai_src / rel, ai_dst / rel)

    _copy_tree(TRAE_WORKFLOW_SRC, payload_dir / "trae_workflow")

    for name in LICENSE_FILES:
        _copy_file(KIT_ROOT / name, payload_dir / name)

    trae_src = KIT_ROOT / ".trae"
    if trae_src.is_dir():
        _copy_tree(trae_src, payload_dir / ".trae")


def _collect_files(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not root.exists():
        return out
    for path in sorted(root.rglob("*")):
        if path.is_file() and not _is_bundle_artifact(path):
            rel = path.relative_to(root).as_posix()
            out[rel] = _sha256(path)
    return out


def check_bundle(profile: str = "default") -> list[str]:
    errors: list[str] = []
    if not PAYLOAD_DIR.is_dir():
        return [
            "payload/ missing — run: python .ai_infra/scripts/release/sync_plugin_bundle.py --sync"
        ]
    with tempfile.TemporaryDirectory(prefix="mas-plugin-check-") as tmp:
        tmp_root = Path(tmp)
        expected_payload = tmp_root / "payload"
        sync_payload(expected_payload, KIT_ROOT, profile)
        expected = _collect_files(expected_payload)
        actual = _collect_files(PAYLOAD_DIR)
        if expected != actual:
            missing = sorted(set(expected) - set(actual))
            extra = sorted(set(actual) - set(expected))
            changed = sorted(
                rel for rel in expected if rel in actual and expected[rel] != actual[rel]
            )
            if missing:
                errors.append(f"payload: missing files: {missing[:8]}")
            if extra:
                errors.append(f"payload: extra files: {extra[:8]}")
            if changed:
                errors.append(f"payload: content drift: {changed[:8]}")
    required = [
        PAYLOAD_DIR / ".ai_infra" / "scripts" / "pr" / "prepare.py",
        PAYLOAD_DIR / ".ai_infra" / "scripts" / "install" / "scaffold.py",
        PAYLOAD_DIR / "trae_workflow" / "__main__.py",
        PAYLOAD_DIR / "LICENSE",
        PAYLOAD_DIR / "NOTICE",
        PAYLOAD_DIR / ".trae" / "rules" / "pr-workflow-enforcement.md",
        PAYLOAD_DIR / ".trae" / "skills" / "workflow-activate" / "SKILL.md",
        PAYLOAD_DIR / ".trae" / "mcp.json",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required bundle file: {path.relative_to(KIT_ROOT)}")
    return errors


def sync_all(profile: str = "default") -> None:
    sync_payload(PAYLOAD_DIR, KIT_ROOT, profile)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync or verify MAS Workflow Kit plugin bundle.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify agents/, rules/, skills/, and payload/ match sources (exit 1 on drift)",
    )
    parser.add_argument(
        "--profile",
        default="default",
        choices=("default",),
        help="Manifest profile for payload (Trae edition: default only)",
    )
    args = parser.parse_args()

    if args.check:
        errors = check_bundle(args.profile)
        if errors:
            print("Plugin bundle check failed:")
            for err in errors:
                print(f" - {err}")
            return 1
        print("Plugin bundle check passed.")
        return 0

    sync_all(args.profile)
    print(f"Synced payload/.trae/ + payload/trae_workflow/ (profile={args.profile}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
