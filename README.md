# Kit Claude Code: Mesa de Alocação

Este kit tem o comando, as skills e a especificação para o Claude Code construir na sua máquina a **Mesa de Alocação**: um monolito em FastAPI e React, com ADRs, SOLID, testes unitários, de feature e E2E, e validação de layout e de fluxo.

## Como usar

```bash
mkdir mesa-alocacao && cd mesa-alocacao
# copie para cá o conteúdo deste kit (CLAUDE.md, README.md e a pasta .claude/)
claude
```

Dentro do Claude Code:

```
/construir-sistema            # constrói fase a fase e pausa para sua aprovação nas fases 1 e 3
/construir-sistema --direto   # sem pausas
/construir-sistema --fase 4   # retoma de uma fase
/validar                      # diagnóstico completo (testes, solid, layout, fluxo)
/validar layout               # uma validação só
```

**Requisitos:** Python 3.12+, Node 20+, git e acesso a pypi.org e registry.npmjs.org. O LLM real é opcional: exporte `ANTHROPIC_API_KEY`. Sem a chave, o sistema usa um adaptador determinístico.

## O que vem no kit

```
CLAUDE.md                                  # contexto permanente do projeto para o Claude Code
.claude/commands/
  construir-sistema.md                     # o comando principal (fases 0 a 6, com validação no fim de cada uma)
  validar.md                               # só diagnóstico
.claude/skills/
  dominio-alocacao/                        # regras normativas, contrato da API, glossário, seed, golden e oráculo
    references/regras.md  api.md  glossario.md  seed.json  expected_week41.json
    scripts/oracle.py
  adr/                                     # como escrever ADRs + template
  backend-python-solid/                    # camadas hexagonais, SOLID aplicado, testes do backend
  frontend-react/                          # estrutura, contrato de data-testid, testes do frontend
  revisar-solid/scripts/check_architecture.py   # fronteiras de camada e sinais de violação SOLID
  validar-testes/scripts/run_tests.sh      # ruff, mypy, pytest (cobertura), vitest, lint, build
  validar-layout/scripts/validate_layout.py     # Playwright: 3 viewports × 2 temas, contraste, overflow, testids
  validar-fluxo/scripts/validate_flows.py       # Playwright: 9 jornadas do planejador, incluindo prompt injection
```

## Por que o kit é assim

- **A especificação é executável.** O `seed.json` tem os dados fictícios da semana 41, e o `expected_week41.json` tem a saída esperada (248 linhas, 3 transferências e 7 exceções). O `oracle.py` é a implementação de referência que gerou essa saída. O sistema construído precisa bater com o golden, então "funcionou" passa a ser verificável.
- **As validações são skills com scripts.** Elas não ficam só em instruções em texto: dá para rodar de novo a qualquer momento com `/validar`.
- **As pausas da fase 1 (ADRs) e da fase 3 (golden e API)** são os pontos em que a sua decisão humana muda o resto do trabalho.
