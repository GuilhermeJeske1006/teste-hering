MESA_PORT ?= 8000
PY := $(CURDIR)/.venv/bin/python
NPM := npm --prefix frontend
ENV_FILE := $(wildcard $(CURDIR)/.env)
ENV_OPT := $(if $(ENV_FILE),--env-file $(ENV_FILE))

.PHONY: install hooks dev test build run validate e2e docker-build docker-run docker-smoke docker-scan

install: ## Instala dependências do backend e do frontend
	$(PY) -m pip install -e "backend[dev]"
	$(PY) -m playwright install chromium
	$(NPM) install
	$(MAKE) hooks

hooks: ## Ativa os hooks de commit e push (.githooks)
	git config core.hooksPath .githooks
	@echo "Hooks ativos: pre-commit, commit-msg e pre-push."

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

IMAGE ?= mesa-alocacao:local

docker-build: ## Imagem do monolito (a mesma que o CD publica no GHCR)
	docker build -t $(IMAGE) .

docker-run: ## Sobe a imagem em http://localhost:$(MESA_PORT), com o .env se existir
	docker run --rm -p $(MESA_PORT):8000 $(if $(ENV_FILE),--env-file $(ENV_FILE)) -v mesa-data:/data $(IMAGE)

docker-smoke: ## Sobe a imagem e confere healthcheck, SPA, modo sombra e usuário não-root (o CD roda o mesmo)
	bash scripts/smoke-image.sh $(IMAGE)

TRIVY_IMAGE ?= aquasec/trivy:0.75.0

docker-scan: ## Varre a imagem com o Trivy: falha em vulnerabilidade CRITICAL/HIGH com correção disponível
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache \
		$(TRIVY_IMAGE) image --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed --no-progress $(IMAGE)
