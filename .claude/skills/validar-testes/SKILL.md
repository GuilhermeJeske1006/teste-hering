---
name: validar-testes
description: Roda e avalia toda a suíte de qualidade da Mesa de Alocação (ruff, mypy, pytest unit/feature/golden com cobertura, Vitest com cobertura, build do frontend) e diagnostica falhas. Use ao fim de cada fase de implementação e sempre antes de declarar algo pronto.
---

# Validação de testes

## Como rodar

```bash
bash .claude/skills/validar-testes/scripts/run_tests.sh
```

O script roda as etapas abaixo, nesta ordem. Ele não para na primeira falha. No fim, grava `reports/tests.md` e sai com código 1 se alguma etapa falhar.

| Etapa | Comando | Critério |
|---|---|---|
| lint-py | `ruff check backend` | 0 erros |
| types-py | `mypy --strict backend/app/domain backend/app/application` | 0 erros |
| unit-py | `pytest backend/tests/unit --cov=app.domain --cov=app.application --cov-fail-under=90` | todos passam, cobertura ≥ 90% |
| feature-py | `pytest backend/tests/feature --cov=app --cov-fail-under=80` | todos passam, inclusive o golden |
| unit-js | `npm --prefix frontend run test -- --run --coverage` | todos passam, linhas ≥ 80% |
| lint-js | `npm --prefix frontend run lint` | 0 erros |
| build-js | `npm --prefix frontend run build` | sem erro de tipo; gera `backend/app/static/index.html` |

## Quando algo falha

1. Leia a **primeira** falha de cada etapa. Erros seguintes costumam ser efeito do primeiro.
2. Classifique a causa:
   - **o código está errado:** corrija o código;
   - **o teste está errado:** só aceite essa conclusão se o teste contradiz `regras.md` ou `api.md`. Nesse caso, corrija o teste e cite a seção do documento;
   - **a especificação é ambígua:** registre uma ADR e pergunte ao usuário.
3. **Nunca** apague teste, use `skip` ou `xfail`, nem baixe o limite de cobertura para ficar verde. Se não houver outra saída, pare e explique ao usuário.
4. Se o golden falhar, compare linha por linha com `expected_week41.json` e mostre as 5 primeiras diferenças. Rode `scripts/oracle.py` para conferir o comportamento esperado.

## Qualidade dos testes (revise, não basta passar)

- Cada teste checa **um** comportamento e tem nome no formato `test_<comportamento>_quando_<condição>`.
- Os testes de feature descrevem o cenário em Dado/Quando/Então, em comentários ou na docstring.
- Sem `sleep`, sem rede real (o LLM real só roda em um teste marcado como `@pytest.mark.llm`, que fica fora do padrão) e sem ordem de execução implícita.
- Todo bug corrigido ganha um teste de regressão.

## Saída

Use `reports/tests.md`, que o script gera, e acrescente um parágrafo de diagnóstico se houver falhas.
