"""
File: __main__.py
Path: trae_workflow/__main__.py
Role: Entrypoint for python -m trae_workflow.
Used By:
 - Makefile, README install examples
Depends On:
 - trae_workflow/cli.py
"""

from trae_workflow.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
