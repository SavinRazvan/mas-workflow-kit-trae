"""
File: check_contract_json_sync.py
Path: .ai_infra/scripts/architecture/check_contract_json_sync.py
Role: Fail when committed .trae/ contract JSON drifts from payload/.trae/ without sync-plugin.
Used By:
 - .ai_infra/scripts/architecture/verify_all.py
 - Makefile contract-json-check target
Depends On:
 - hashlib, pathlib (stdlib)
Notes:
 - Kit-dev only; compares SHA-256 of contract files present in both trees.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

CONTRACT_FILES = (
    ".trae/mcp.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_contract_json_sync(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in CONTRACT_FILES:
        src = root / rel
        payload_rel = Path("payload") / rel
        dst = root / payload_rel
        if not src.is_file():
            continue
        if not dst.is_file():
            errors.append(f"missing payload mirror: {payload_rel.as_posix()} (run make sync-plugin)")
            continue
        if _sha256(src) != _sha256(dst):
            errors.append(
                f"contract drift: {rel} != {payload_rel.as_posix()} — run make sync-plugin and commit"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify .trae/ contract JSON matches payload/.trae/")
    parser.add_argument("--directory", type=Path, default=".")
    args = parser.parse_args(argv)
    root = args.directory.resolve()
    if not (root / ".trae").is_dir():
        print("contract-json-sync: skipped (no .trae/)")
        return 0
    errors = check_contract_json_sync(root)
    if errors:
        print("contract-json-sync: FAIL")
        for err in errors:
            print(f" - {err}")
        return 1
    print("contract-json-sync: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
