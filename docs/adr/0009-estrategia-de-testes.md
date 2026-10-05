# 0009. Estratégia de testes: pirâmide com golden e E2E, e limites de cobertura

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** tech lead, QA
- **Relacionadas:** [0003](0003-arquitetura-hexagonal-solid.md), [0004](0004-motor-deterministico-llm-nao-calcula.md), [0010](0010-frontend-react-ts-vite.md)

## Contexto

O critério de aceite do motor é numérico e exato (248 linhas, 3 transferências, 7 exceções). O sistema é construído com TDD, em parte por um agente, e "funcionou" precisa ser verificável por máquina. Há também jornadas de UI (aprovar, rejeitar, desfazer) e riscos de segurança de IA (prompt injection) que só aparecem de ponta a ponta.

## Opções consideradas

1. **Pirâmide: unitários (domain/application com fakes), feature (API via TestClient + golden) e E2E (Playwright no monolito), com cobertura mínima** — prós: feedback rápido na base, golden prova a regra, E2E prova a integração; contras: três suítes para manter, E2E mais lento e sensível a timing.
2. **Só E2E** — prós: testa o que o usuário vê; contras: lento, falhas difíceis de diagnosticar, cobertura de regra ruim.
3. **Só unitários** — prós: rápidos; contras: não provam contrato da API nem integração com o front.

## Decisão

Usaremos a **pirâmide de testes**: `backend/tests/unit` (< 1 s, sem I/O), `backend/tests/feature` (histórias Dado/Quando/Então e o golden), Vitest no frontend e os fluxos E2E da skill `validar-fluxo`. Limites: **90%** de cobertura em `domain/` + `application/`, **80%** no backend total e **80%** de linhas no frontend. O LLM real só roda em teste marcado `@pytest.mark.llm`, fora do padrão.

## Consequências

- **Positivas:** regressão de regra aparece no golden; contrato da API protegido; jornadas validadas no navegador.
- **Negativas:** custo de manter fixtures e golden; cobertura como meta pode induzir testes rasos; E2E depende de Chromium instalado.
- **A monitorar:** tempo total da suíte; testes instáveis no E2E; testes que só sobem cobertura sem checar comportamento.

## Conformidade

- `bash .claude/skills/validar-testes/scripts/run_tests.sh` (com `--cov-fail-under`) e `reports/tests.md` aprovado.
- `python .claude/skills/validar-fluxo/scripts/validate_flows.py` com os 9 fluxos.
