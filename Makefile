PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: install-dry-run smoke-consumer test gates sync-plugin check-plugin check-payload-git check-trae-parity integrate-validate drift-validate ci-seed verify-all doc-validate type-check contract-json-check coverage-index clean-legacy-contract

install-dry-run:
	rm -rf /tmp/workflow-kit-dry-run
	$(PYTHON) -m trae_workflow install \
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

contract-json-check:
	$(PYTHON) .ai_infra/scripts/architecture/check_contract_json_sync.py --directory .

gates:
	$(PYTHON) -m trae_workflow gates

PROFILE ?= default

sync-plugin:
	$(PYTHON) .ai_infra/scripts/release/sync_plugin_bundle.py --profile $(PROFILE)

check-plugin:
	$(PYTHON) .ai_infra/scripts/release/sync_plugin_bundle.py --check --profile $(PROFILE)

check-payload-git:
	$(PYTHON) .ai_infra/scripts/release/sync_plugin_bundle.py --check-git --profile $(PROFILE)

check-trae-parity:
	$(PYTHON) .ai_infra/scripts/architecture/check_trae_parity.py

integrate-validate:
	$(PYTHON) -m trae_workflow integrate validate --directory .

drift-validate:
	$(PYTHON) -m trae_workflow drift validate --directory .

doc-validate:
	$(PYTHON) -m trae_workflow doc validate --directory .

verify-all:
	$(PYTHON) -m trae_workflow verify all --directory .

ci-seed:
	$(PYTHON) .ai_infra/scripts/ci/seed_kit_workspace.py --directory .

coverage-index:
	$(PYTHON) .ai_infra/scripts/ci/generate_coverage_index.py --directory .

.PHONY: clean-legacy-contract
clean-legacy-contract:
	rm -rf .cursor .agents .cursor-plugin
	@echo "Removed gitignored legacy contract trees (.cursor, .agents, .cursor-plugin). SSOT: .trae/"
