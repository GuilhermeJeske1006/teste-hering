# Registro de decisões de arquitetura (ADRs)

Formato MADR enxuto, em pt-BR. Template e checklist: skill `adr` (`.claude/skills/adr`). Ciclo: `Proposta → Aceita → (Depreciada | Substituída por NNNN)`. Nunca reescreva a decisão de uma ADR aceita: crie uma nova.

| Nº | Título | Status | Data |
|---|---|---|---|
| [0001](0001-registrar-decisoes-com-adrs.md) | Registrar decisões de arquitetura com ADRs | Aceita | 2026-10-05 |
| [0002](0002-monolito-modular-fastapi-react.md) | Monolito modular: FastAPI serve a API e o build do React | Aceita | 2026-10-05 |
| [0003](0003-arquitetura-hexagonal-solid.md) | Arquitetura hexagonal (ports & adapters) com SOLID como critério de revisão | Aceita | 2026-10-05 |
| [0004](0004-motor-deterministico-llm-nao-calcula.md) | Previsão e alocação determinísticas; o LLM não faz contas | Aceita | 2026-10-05 |
| [0005](0005-regras-de-excecao-plugaveis.md) | Regras de exceção como estratégias plugáveis (`ExceptionRule`) | Aceita | 2026-10-05 |
| [0006](0006-llmclient-como-port.md) | `LLMClient` como port, com adaptador Anthropic e determinístico | Aceita | 2026-10-05 |
| [0007](0007-modo-sombra.md) | Modo sombra: recomendar e registrar, nunca escrever no ERP ou WMS | Aceita | 2026-10-05 |
| [0008](0008-persistencia-sqlite-seed-json.md) | Persistência em SQLite via repositórios; seed em JSON | Aceita | 2026-10-05 |
| [0009](0009-estrategia-de-testes.md) | Estratégia de testes: pirâmide com golden e E2E, e limites de cobertura | Aceita | 2026-10-05 |
| [0010](0010-frontend-react-ts-vite.md) | Frontend em React + TS + Vite, sem estado global, com cliente de API único | Aceita | 2026-10-05 |
| [0011](0011-seguranca-e-governanca-de-ia.md) | Segurança e governança de IA | Aceita | 2026-10-05 |
| [0012](0012-parametros-implicitos-viram-politicas.md) | Parâmetros implícitos do `regras.md` viram políticas com valor padrão | Aceita | 2026-10-05 |
| [0013](0013-interpretacoes-da-especificacao.md) | Interpretações da especificação onde ela é ambígua | Aceita | 2026-10-05 |
| [0014](0014-ci-cd-github-actions-ghcr.md) | CI/CD com hooks locais, GitHub Actions e imagem Docker no GHCR | Aceita | 2026-10-05 |
