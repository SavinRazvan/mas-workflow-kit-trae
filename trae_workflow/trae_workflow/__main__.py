"""
File: __main__.py
Path: trae_workflow/__main__.py
Role: Entry for python -m trae_workflow delegating to install CLI.
Used By:
 - python -m trae_workflow
Depends On:
 - .ai_infra/install/trae_workflow/cli.py
Notes:
 - importlib load of install package cli module.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_CLI = Path(__file__).resolve().parent.parent / ".ai_infra" / "install" / "trae_workflow" / "cli.py"
_spec = importlib.util.spec_from_file_location("trae_workflow_cli", _CLI)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

if __name__ == "__main__":
    raise SystemExit(_mod.main())
