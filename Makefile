MESA_PORT ?= 8000
PY := $(CURDIR)/.venv/bin/python
NPM := npm --prefix frontend
ENV_FILE := $(wildcard $(CURDIR)/.env)
ENV_OPT := $(if $(ENV_FILE),--env-file $(ENV_FILE))

.PHONY: install dev test build run validate e2e

install: ## Instala dependências do backend e do frontend
	$(PY) -m pip install -e "backend[dev]"
	$(PY) -m playwright install chromium
	$(NPM) install

dev: ## Backend com reload (8000) + Vite (5173) com proxy de /api
	trap 'kill 0' EXIT; \
	(cd backend && $(PY) -m uvicorn app.main:app --reload --port $(MESA_PORT) $(ENV_OPT)) & \
	$(NPM) run dev

test: ## Suíte completa de qualidade (skill validar-testes)
	PYTHON=$(PY) bash .claude/skills/validar-testes/scripts/run_tests.sh

build: ## Build do React em backend/app/static
	$(NPM) run build

run: ## Monolito em http://localhost:8000
	cd backend && $(PY) -m uvicorn app.main:app --port $(MESA_PORT) $(ENV_OPT)

e2e: build ## Fluxos de ponta a ponta (skill validar-fluxo)
	$(PY) .claude/skills/validar-fluxo/scripts/validate_flows.py --out reports/flows

validate: ## Testes, SOLID, layout e fluxos (não para na primeira falha)
	@mkdir -p reports; fail=0; \
	$(MAKE) test || fail=1; \
	$(PY) .claude/skills/revisar-solid/scripts/check_architecture.py backend/app || fail=1; \
	(cd backend && $(PY) -m uvicorn app.main:app --port $(MESA_PORT) >/dev/null 2>&1) & pid=$$!; \
	sleep 3; \
	$(PY) .claude/skills/validar-layout/scripts/validate_layout.py --url http://localhost:$(MESA_PORT) --out reports/layout || fail=1; \
	kill $$pid 2>/dev/null; pkill -f "uvicorn app.main:app --port $(MESA_PORT)" 2>/dev/null; \
	$(PY) .claude/skills/validar-fluxo/scripts/validate_flows.py --out reports/flows || fail=1; \
	exit $$fail
