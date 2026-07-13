PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: install-dry-run smoke-consumer test gates sync-plugin check-plugin check-trae-parity integrate-validate drift-validate ci-seed verify-all doc-validate type-check coverage-index

install-dry-run:
	rm -rf /tmp/workflow-kit-dry-run
	$(PYTHON) -m cursor_workflow install \
		--target /tmp/workflow-kit-dry-run \
		--with-venv \
		--with-mcp-json \
		--verify
	$(PYTHON) .ai_infra/scripts/architecture/check_consumer_purity.py --target /tmp/workflow-kit-dry-run

smoke-consumer:
	bash .ai_infra/scripts/install/smoke_marketplace.sh

test:
	$(PYTHON) -m pytest -q

type-check:
	.venv/bin/pyright

gates:
	$(PYTHON) -m cursor_workflow gates

sync-plugin:
	$(PYTHON) .ai_infra/scripts/release/sync_plugin_bundle.py --profile dual_ide

check-plugin:
	$(PYTHON) .ai_infra/scripts/release/sync_plugin_bundle.py --check --profile dual_ide

check-trae-parity:
	$(PYTHON) .ai_infra/scripts/architecture/check_trae_parity.py

integrate-validate:
	$(PYTHON) -m cursor_workflow integrate validate --directory .

drift-validate:
	$(PYTHON) -m cursor_workflow drift validate --directory .

doc-validate:
	$(PYTHON) -m cursor_workflow doc validate --directory .

verify-all:
	$(PYTHON) -m cursor_workflow verify all --directory .

ci-seed:
	$(PYTHON) .ai_infra/scripts/ci/seed_kit_workspace.py --directory .

coverage-index:
	$(PYTHON) .ai_infra/scripts/ci/generate_coverage_index.py --directory .
