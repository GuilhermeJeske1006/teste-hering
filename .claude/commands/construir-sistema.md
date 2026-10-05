---
description: Constrói do zero a Mesa de Alocação (monolito FastAPI + React) com ADRs, SOLID, testes unitários, de feature e E2E, e validações de layout e fluxo via skills.
argument-hint: "[--direto] [--fase N]"
---

# /construir-sistema

Você vai construir a **Mesa de Alocação**, o sistema AI First de alocação e reposição de lojas, como um **monolito**: backend Python (FastAPI) servindo um frontend React (Vite + TypeScript) em um único processo e um único repositório.

Argumentos recebidos: `$ARGUMENTS`

- Sem `--direto`: **pare e peça aprovação** ao usuário ao final das fases 1 e 3 (os pontos marcados com ⏸).
- Com `--fase N`: retome a partir da fase N. Antes, rode `/validar` para conhecer o estado atual.

## Regras gerais (valem para todas as fases)

1. **Antes de cada fase, carregue as skills indicadas.** Elas são a fonte da verdade. Se o pedido do usuário contradisser uma skill, pergunte antes de seguir.
2. **TDD:** teste vermelho → código mínimo → refatoração. Nenhum código de produção sem um teste que o exija.
3. **Commits pequenos**, um por passo concluído e verde, no formato Conventional Commits (`feat(domain): ...`, `test(feature): ...`, `docs(adr): ...`).
4. Use o task list para mostrar o progresso, com uma tarefa por fase.
5. Ao fim de cada fase, rode a validação indicada. **Uma fase só termina quando a validação passar.** Se não passar depois de 3 tentativas, pare e reporte.
6. Nunca invente regra de negócio: tudo está em `.claude/skills/dominio-alocacao/references/`.

---

## Fase 0: Ambiente

1. Verifique `python --version` (≥ 3.12), `node --version` (≥ 20) e `git --version`. Se faltar algo, pare e diga como instalar.
2. Se a pasta não for um repositório, rode `git init`. Crie o `.gitignore` (Python, Node, `backend/app/static/`, `backend/data/`, `reports/`, `.env`).
3. Crie `.venv` e o `backend/pyproject.toml`:
   - dependências: `fastapi`, `uvicorn[standard]`, `pydantic>=2`, `httpx`;
   - dependências de desenvolvimento: `pytest`, `pytest-cov`, `ruff`, `mypy`, `playwright`.

   Depois rode `pip install -e "backend[dev]"` e `python -m playwright install chromium`.
4. Crie o frontend com `npm create vite@latest frontend -- --template react-ts` e instale `vitest @vitest/coverage-v8 @testing-library/react @testing-library/user-event @testing-library/jest-dom jsdom eslint` mais as configs.
5. Crie um `Makefile` com os alvos `dev`, `test`, `build`, `run`, `validate` e `e2e`.

## Fase 1: Decisões (ADRs)

**Skills:** `adr`, `dominio-alocacao`.

Crie `docs/adr/README.md` (o índice) e as ADRs abaixo, todas com status **Aceita**, seguindo o template e o checklist da skill. Cada uma precisa de opções reais e de pelo menos uma consequência negativa.

| Nº | Decisão a registrar |
|---|---|
| 0001 | Registrar decisões de arquitetura com ADRs (MADR enxuto, pt-BR) |
| 0002 | Monolito modular: FastAPI serve a API e o build do React em um único processo (alternativas: SPA e API separadas; Next.js; microsserviços) |
| 0003 | Arquitetura hexagonal (ports & adapters) com SOLID como critério de revisão |
| 0004 | Previsão e alocação determinísticas atrás de interfaces; **o LLM não faz contas** (alternativas: LLM calculando; ML externo desde o dia 1; solver OR-Tools) |
| 0005 | Regras de exceção como estratégias plugáveis (`ExceptionRule`), seguindo o princípio aberto/fechado |
| 0006 | `LLMClient` como port, com adaptador Anthropic (httpx) e adaptador determinístico como padrão sem chave e nos testes |
| 0007 | Modo sombra: o sistema recomenda e registra, e nunca escreve no ERP ou WMS no MVP |
| 0008 | Persistência em SQLite via repositórios; seed em JSON como fonte dos dados de demonstração |
| 0009 | Estratégia de testes: pirâmide (unidade, feature com golden e E2E com Playwright) e limites de cobertura |
| 0010 | Frontend em React + TS + Vite, sem lib de estado global, com cliente de API único e contrato de `data-testid` |
| 0011 | Segurança e governança de IA: texto de sinal é dado e não instrução; saída do LLM validada por schema; `requires_human` recalculado no código; trilha de auditoria append-only |

**Validação:** todas as ADRs passam pelo checklist da skill `adr`, e o índice está completo.
⏸ Mostre ao usuário a tabela do índice e um resumo de uma linha por ADR, e espere o "ok".

## Fase 2: Domínio e casos de uso (backend, de dentro para fora)

**Skills:** `dominio-alocacao`, `backend-python-solid`.

1. Copie `references/seed.json` para `backend/app/seed/seed.json`.
2. Escreva `domain/model.py` e os testes unitários dos invariantes, como `Policies` imutável e `AllocationLine` válida.
3. Implemente, nesta ordem e sempre com teste primeiro, cada item de `regras.md`:
   - previsão (§2–3), incluindo o decorator de uplift;
   - `LineCalculator` (§4);
   - `DcRationer` (§5);
   - `TransferPlanner` (§6);
   - modo de execução (§7);
   - **uma classe por regra de exceção** (§8), com `default_rules()`;
   - `explain.py`.
4. Escreva o teste de extensibilidade: uma regra fake injetada aparece no resultado sem nenhuma mudança no motor.
5. Crie `application/ports.py` e os casos de uso (§9–12), com fakes nos testes.
6. Escreva a suíte de contrato do `LLMClient` e a dos repositórios.

**Validação:**
- skill `validar-testes`, nas etapas `lint-py`, `types-py` e `unit-py`;
- skill `revisar-solid`, na parte automática.

## Fase 3: Infraestrutura, API e golden

**Skills:** `backend-python-solid`, `dominio-alocacao` (`api.md`).

1. Implemente os adaptadores: `JsonSeedSource`, `Sqlite*`, `InMemory*`, `DeterministicLLMClient` e `AnthropicLLMClient` (com timeout de 30 s, uma nova tentativa e erro mapeado para 503).
2. Escreva `container.py` (o composition root) e `api/` exatamente conforme `api.md`, incluindo o formato de erro.
3. Escreva o teste golden (`tests/feature/test_golden_week41.py`) e todos os testes de feature obrigatórios da skill do backend.
4. Faça o `main.py` servir `backend/app/static` com fallback de SPA.

**Validação:**
- skill `validar-testes`, nas etapas `lint-py`, `types-py`, `unit-py` e `feature-py`;
- skill `revisar-solid`, na parte automática.

⏸ Mostre ao usuário o resultado do golden (as 7 exceções e as 3 transferências) e um `curl` de `/api/summary`. Espere o "ok".

## Fase 4: Frontend

**Skills:** `frontend-react`, `dominio-alocacao` (`api.md` e `glossario.md`).

1. Escreva `tokens.css` com os temas claro e escuro, a escala tipográfica e as cores de severidade.
2. Escreva `api/client.ts` e `api/types.ts`, testados com um fetch fake injetado.
3. Escreva os componentes apresentacionais, com teste primeiro, e depois os hooks, seguindo os cenários obrigatórios da skill.
4. Monte `pages/AllocationDesk.tsx` com o contêiner `data-layout="main"` e todos os `data-testid` do contrato.
5. Configure o `vite.config.ts` com o build em `../backend/app/static` e o proxy de `/api` no modo dev.

**Validação:** skill `validar-testes`, nas etapas `unit-js`, `lint-js` e `build-js`.

## Fase 5: Integração e validação de ponta a ponta

**Skills:** `validar-testes`, `validar-layout`, `validar-fluxo`, `revisar-solid`.

1. Rode `make build` e `make run`, e confirme que `http://localhost:8000` abre a mesa.
2. Rode a skill `validar-testes` completa.
3. Rode a skill `validar-layout`, incluindo a **revisão visual das capturas**.
4. Rode a skill `validar-fluxo`, com os 9 fluxos.
5. Rode a skill `revisar-solid` completa, com o script e o checklist manual.
6. Corrija o que falhar, respeitando os limites de ciclos de cada skill. Toda correção de comportamento ganha um teste de regressão.

## Fase 6: Entrega

1. Escreva o `README.md` da raiz:
   - o que é o sistema, com a tese do produto;
   - como rodar (`make dev`, `make run`) e como habilitar o LLM real (`ANTHROPIC_API_KEY`);
   - o mapa da arquitetura em um diagrama mermaid;
   - links para as ADRs;
   - como rodar cada validação.
2. Escreva `reports/RESUMO.md` com:
   - o status de cada validação (testes, layout, fluxos, SOLID) e os números de cobertura;
   - as decisões que divergiram do plano e a ADR de cada uma;
   - o que ficou de fora de propósito no MVP: integração com ERP, todas as categorias e autenticação;
   - os próximos passos.
3. Mostre ao usuário o `RESUMO.md` e os comandos para abrir o sistema.
