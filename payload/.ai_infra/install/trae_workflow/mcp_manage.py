"""
File: mcp_manage.py
Path: .ai_infra/install/trae_workflow/mcp_manage.py
Role: Merge kit + user MCP JSON; validate registry against mcp.json.
Used By:
 - .ai_infra/install/trae_workflow/cli.py
 - .ai_infra/scripts/install/scaffold.py
Depends On:
 - json, yaml (PyYAML)
 - .ai_infra/ide_contract_paths.py
Notes:
 - Never overwrites existing mcp.user.json on install.
 - default: emits merged MCP for both .cursor/ and .trae/ (ADR-008).
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

_AI_INFRA = Path(__file__).resolve().parents[2]
if str(_AI_INFRA) not in sys.path:
    sys.path.insert(0, str(_AI_INFRA))

from ide_contract_paths import (  # noqa: E402
    CURSOR,
    TRAE,
    all_ides,
    mcp_json,
    mcp_kit_example,
    mcp_registry,
    mcp_registry_example,
    mcp_user_example,
    mcp_user_json,
    normalize_ide,
)


def _kit_fragment(ide: str) -> Path:
    return Path(normalize_ide(ide)).joinpath("mcp.json.kit.example")


def _user_fragment(ide: str) -> Path:
    return Path(normalize_ide(ide)).joinpath("mcp.user.json")


def _mcp_dest(ide: str) -> Path:
    return Path(normalize_ide(ide)).joinpath("mcp.json")


def _registry_path(ide: str) -> Path:
    return Path(normalize_ide(ide)).joinpath("mcp.registry.yaml")


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def _strip_private_keys(obj: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in obj.items():
        if str(key).startswith("_"):
            continue
        if isinstance(value, dict):
            cleaned[key] = _strip_private_keys(value)
        else:
            cleaned[key] = value
    return cleaned


def merge_mcp_configs(kit: dict[str, Any], user: dict[str, Any] | None = None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    kit_servers = kit.get("mcpServers", {})
    if not isinstance(kit_servers, dict):
        raise ValueError("kit mcpServers must be an object")
    merged_servers = {k: v for k, v in kit_servers.items()}
    if user:
        user_servers = user.get("mcpServers", {})
        if not isinstance(user_servers, dict):
            raise ValueError("user mcpServers must be an object")
        for name, spec in user_servers.items():
            if str(name).startswith("_"):
                continue
            merged_servers[name] = spec
    merged["mcpServers"] = merged_servers
    return merged


def write_merged_mcp(root: Path, *, ide: str = CURSOR, dry_run: bool = False) -> Path:
    ide_key = normalize_ide(ide)
    kit_path = mcp_kit_example(root, ide_key)
    if not kit_path.is_file():
        raise FileNotFoundError(f"missing kit MCP fragment: {kit_path}")
    kit = _strip_private_keys(_read_json(kit_path))
    user_path = mcp_user_json(root, ide_key)
    user = _strip_private_keys(_read_json(user_path)) if user_path.is_file() else None
    merged = merge_mcp_configs(kit, user)
    dest = mcp_json(root, ide_key)
    if dry_run:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return dest


def write_merged_mcp_all(root: Path, *, ides: tuple[str, ...] | None = None, dry_run: bool = False) -> list[Path]:
    targets = ides if ides is not None else all_ides()
    written: list[Path] = []
    for ide in targets:
        kit_path = mcp_kit_example(root, ide)
        if kit_path.is_file():
            written.append(write_merged_mcp(root, ide=ide, dry_run=dry_run))
    return written


def load_registry(root: Path, *, ide: str = CURSOR) -> dict[str, Any]:
    ide_key = normalize_ide(ide)
    path = mcp_registry(root, ide_key)
    if not path.is_file():
        example = mcp_registry_example(root, ide_key)
        if not example.is_file():
            raise FileNotFoundError(f"missing registry: {path} or {example}")
        path = example
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"invalid registry YAML: {path}")
    return data


def validate_registry(root: Path, *, ide: str = CURSOR) -> list[str]:
    errors: list[str] = []
    ide_key = normalize_ide(ide)
    registry_path = mcp_registry(root, ide_key)
    if not registry_path.is_file():
        return []
    try:
        registry = load_registry(root, ide=ide_key)
    except (FileNotFoundError, ValueError) as exc:
        return [str(exc)]

    servers = registry.get("servers", {})
    if not isinstance(servers, dict):
        return ["registry servers must be a mapping"]

    dest = mcp_json(root, ide_key)
    if not dest.is_file():
        return [f"missing merged MCP config: {dest}"]

    mcp = _read_json(dest)
    mcp_servers = mcp.get("mcpServers", {})
    if not isinstance(mcp_servers, dict):
        return [f"{dest} mcpServers must be an object"]

    prefix = f".{ide_key}/"
    for name, spec in servers.items():
        if not isinstance(spec, dict):
            errors.append(f"registry server '{name}' must be a mapping")
            continue
        if name not in mcp_servers:
            tier = spec.get("tier")
            if tier == "external":
                continue
            errors.append(f"registry server '{name}' not in {prefix}mcp.json mcpServers")
        agents = spec.get("agents", [])
        if agents is not None and not isinstance(agents, list):
            errors.append(f"registry server '{name}' agents must be a list")

    return errors


def validate_registry_all(root: Path, *, ides: tuple[str, ...] | None = None) -> list[str]:
    errors: list[str] = []
    for ide in ides or all_ides():
        reg = mcp_registry(root, ide)
        if reg.is_file():
            errors.extend(validate_registry(root, ide=ide))
    return errors


def link_user_server(root: Path, name: str, fragment_file: Path, *, ide: str = CURSOR) -> None:
    ide_key = normalize_ide(ide)
    fragment = _strip_private_keys(_read_json(fragment_file))
    fragment_servers = fragment.get("mcpServers", {})
    if not isinstance(fragment_servers, dict) or not fragment_servers:
        raise ValueError("fragment must contain mcpServers with at least one entry")

    user_path = mcp_user_json(root, ide_key)
    if user_path.is_file():
        user = _read_json(user_path)
    else:
        example = mcp_user_example(root, ide_key)
        user = _read_json(example) if example.is_file() else {"mcpServers": {}}

    user_servers = user.setdefault("mcpServers", {})
    if not isinstance(user_servers, dict):
        raise ValueError("existing mcp.user.json mcpServers must be an object")

    if name in fragment_servers:
        user_servers[name] = fragment_servers[name]
    else:
        if len(fragment_servers) == 1:
            only_key = next(iter(fragment_servers))
            user_servers[name] = fragment_servers[only_key]
        else:
            raise ValueError(
                f"fragment has multiple servers; pass --name matching a key in {fragment_file}"
            )

    user_path.parent.mkdir(parents=True, exist_ok=True)
    user_path.write_text(json.dumps(user, indent=2) + "\n", encoding="utf-8")
    write_merged_mcp(root, ide=ide_key)


def ensure_mcp_gitignore(root: Path) -> None:
    gitignore = root / ".gitignore"
    lines = [".cursor/mcp.user.json", ".trae/mcp.user.json"]
    if gitignore.is_file():
        text = gitignore.read_text(encoding="utf-8")
        for line in lines:
            if line not in text:
                text = text.rstrip() + f"\n{line}\n"
        gitignore.write_text(text, encoding="utf-8")
    else:
        gitignore.write_text("# MCP secrets\n" + "\n".join(lines) + "\n", encoding="utf-8")


def seed_trae_mcp_from_cursor(root: Path) -> None:
    """Copy Cursor MCP exemplars to .trae/ when .trae exists but fragments missing."""
    trae_root = root / ".trae"
    if not trae_root.is_dir():
        return
    pairs = (
        (root / ".cursor" / "mcp.json.kit.example", trae_root / "mcp.json.kit.example"),
        (root / ".cursor" / "mcp.registry.yaml.example", trae_root / "mcp.registry.yaml.example"),
        (root / ".cursor" / "mcp.user.example.json", trae_root / "mcp.user.example.json"),
    )
    for src, dst in pairs:
        if src.is_file() and not dst.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for name in ("mcp.registry.yaml", "mcp.user.json"):
        src = root / ".cursor" / name
        dst = trae_root / name
        if src.is_file() and not dst.is_file():
            shutil.copy2(src, dst)
