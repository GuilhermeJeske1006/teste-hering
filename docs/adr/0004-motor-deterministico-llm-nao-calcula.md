# 0004. Previsão e alocação determinísticas atrás de interfaces; o LLM não faz contas

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** arquiteto de software, líder de planejamento
- **Relacionadas:** [0003](0003-arquitetura-hexagonal-solid.md), [0006](0006-llmclient-como-port.md), [0011](0011-seguranca-e-governanca-de-ia.md)

## Contexto

As recomendações movimentam estoque real (envio do CD e sugestão de pedido para franquias). O planejador precisa confiar e auditar cada número. LLMs erram aritmética, não são reprodutíveis e não explicam de onde veio o número. O `regras.md` define previsão por média ponderada, alvo, rateio proporcional do CD e transferências com ordem determinística, e o golden exige igualdade exata com `expected_week41.json`.

## Opções consideradas

1. **Código determinístico atrás de interfaces (`DemandForecaster`, `LineCalculator`, `DcRationer`, `TransferPlanner`); LLM só interpreta texto e explica** — prós: reprodutível, testável com golden, auditável; contras: modelos estatísticos simples no MVP, menos "inteligência" na previsão.
2. **LLM calculando previsão e alocação** — prós: flexível, entende contexto; contras: não reprodutível, alucina números, impossível validar contra golden, risco regulatório e de confiança.
3. **Modelo de ML externo desde o dia 1** — prós: previsão potencialmente melhor; contras: exige histórico, MLOps e monitoramento antes de provar valor.
4. **Solver de otimização (OR-Tools)** — prós: alocação ótima global; contras: difícil de explicar ao planejador, dependência pesada, o problema do MVP não exige otimização global.

## Decisão

Usaremos **código determinístico** para previsão, grade, rateio e transferências, atrás de interfaces de domínio. O LLM entra **apenas** em `InterpretSignal` e `AskCopilot`, e nunca é fonte de número.

## Consequências

- **Positivas:** golden reproduzível; explicações geradas por template a partir dos mesmos números; troca futura de previsor por ML é só uma nova implementação de `DemandForecaster`.
- **Negativas:** a média ponderada não captura sazonalidade longa nem tendências; o ganho de "IA" no MVP fica na triagem e na explicação, não no número.
- **A monitorar:** erro de previsão por categoria (MAPE) quando houver dados reais; pedidos do negócio para "a IA decidir".

## Conformidade

- `tests/feature/test_golden_week41.py` compara linhas, transferências e exceções com o golden.
- `check_architecture.py` proíbe literais numéricos em `domain/rules/`.
- Revisão: nenhum caso de uso de cálculo depende de `LLMClient`.
