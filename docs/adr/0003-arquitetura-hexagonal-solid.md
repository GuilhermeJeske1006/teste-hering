# 0003. Arquitetura hexagonal (ports & adapters) com SOLID como critério de revisão

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** arquiteto de software, tech lead
- **Relacionadas:** [0002](0002-monolito-modular-fastapi-react.md), [0005](0005-regras-de-excecao-plugaveis.md), [0006](0006-llmclient-como-port.md)

## Contexto

O motor de alocação é regra de negócio pura e precisa ser testado com o golden da semana 41 sem rede, sem banco e sem framework. Em volta dele há adaptadores que vão mudar (seed JSON → ERP, SQLite → Postgres, LLM determinístico → Anthropic). Um monolito sem fronteiras tende a misturar SQL, HTTP e regra no mesmo arquivo.

## Opções consideradas

1. **Hexagonal: `domain` ← `application` (ports) ← `infrastructure`/`api`, com `container.py` como composition root** — prós: domínio testável isoladamente, adaptadores trocáveis, fronteiras verificáveis por script; contras: mais arquivos e indireção, curva para quem não conhece o padrão.
2. **Camadas clássicas (controller → service → repository) sem ports** — prós: familiar, menos arquivos; contras: serviços acoplados a implementações concretas, difícil trocar LLM ou banco nos testes.
3. **Script procedural (como o `oracle.py`)** — prós: curto e direto; contras: impossível estender regras sem `if`, sem pontos de injeção, sem testes por unidade.

## Decisão

Usaremos **arquitetura hexagonal**: `domain/` sem dependências externas, `application/` com casos de uso e ports (`Protocol`), `infrastructure/` com adaptadores, `api/` com routers finos, e **só `container.py` instancia adaptadores**. SOLID é critério de revisão de PR conforme a skill `backend-python-solid`.

## Consequências

- **Positivas:** testes unitários rodam em menos de 1 s com fakes; trocar SQLite ou LLM não toca no domínio; revisão objetiva via script.
- **Negativas:** mais arquivos e mais boilerplate (ports, fakes, container); algumas leituras simples atravessam três camadas.
- **A monitorar:** ports crescendo além de 3 métodos (sinal de violar o I); casos de uso com lógica de domínio duplicada.

## Conformidade

- `python .claude/skills/revisar-solid/scripts/check_architecture.py backend/app` sem erros (camadas, instanciação fora do container, literais em regras).
- `mypy --strict` em `domain/` e `application/`.
