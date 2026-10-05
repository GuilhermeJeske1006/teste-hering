# 0005. Regras de exceção como estratégias plugáveis (`ExceptionRule`)

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** arquiteto de software, líder de planejamento
- **Relacionadas:** [0003](0003-arquitetura-hexagonal-solid.md), [0004](0004-motor-deterministico-llm-nao-calcula.md)

## Contexto

O valor do produto está em transformar 248 linhas em poucas **exceções explicadas** (7 no seed). As regras vão crescer: hoje são 8 (lançamento, ruptura com transferência, sinal divergente, queda sazonal, curva de tamanho, estoque negativo, rejeição repetida, limite de execução automática). O planejador vai pedir regras novas com frequência, e cada uma tem severidade, agrupamento e texto próprios.

## Opções consideradas

1. **Uma classe por regra implementando o protocolo `ExceptionRule` e registrada em `default_rules()`** — prós: regra nova é um arquivo novo (aberto/fechado), testável isoladamente, ordem de saída explícita; contras: mais arquivos, contexto de avaliação precisa ser rico o bastante para todas as regras.
2. **Motor com `if/elif` por tipo de regra** — prós: tudo em um lugar; contras: cresce sem limite, toda regra nova mexe no motor, testes acoplados.
3. **Regras declarativas (DSL/JSON configurável pelo planejador)** — prós: o negócio edita sem deploy; contras: interpretador e validação complexos para o MVP, regras como curva de tamanho não cabem em expressão simples.

## Decisão

Usaremos **estratégias plugáveis**: cada regra é uma classe em `domain/rules/` que implementa `ExceptionRule.evaluate(context) -> list[AllocationException]`; `default_rules()` define a ordem da tabela do `regras.md` §8. Os limites vêm de `Policies` e os textos de `domain/explain.py`.

## Consequências

- **Positivas:** adicionar regra não toca no motor; cada regra tem seu teste; o teste de extensibilidade injeta uma regra fake.
- **Negativas:** o `RuleContext` concentra muitos dados (linhas, transferências, histórico, sinais), o que pode virar um objeto grande; a ordem de saída depende da ordem do registro.
- **A monitorar:** crescimento do `RuleContext`; regras com custo alto (varredura de histórico) quando o volume crescer.

## Conformidade

- `tests/unit/domain/test_extensibility.py`: uma regra fake injetada aparece no resultado sem mudança no motor.
- `check_architecture.py` avisa sobre `if/elif` encadeado por `rule`/`type` e proíbe literais numéricos em `domain/rules/`.
