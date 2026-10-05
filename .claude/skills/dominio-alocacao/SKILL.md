---
name: dominio-alocacao
description: Regras de negócio, glossário, contrato de API e dados de seed da Mesa de Alocação (alocação e reposição de lojas de varejo de moda). Use antes de escrever ou alterar qualquer código de domínio, API, seed, teste golden ou tela do sistema.
---

# Domínio: Mesa de Alocação

Este é o sistema AI First de alocação e reposição de lojas. O motor recalcula todo dia quanto cada loja deve ter de cada produto, em cada tamanho. O que está dentro da política segue sozinho. O que precisa de julgamento vira **exceção explicada** para o planejador.

**Tese:** o planejador deixa de operar a planilha e passa a ser o dono das regras.

## Arquivos desta skill

| Arquivo | Quando ler |
|---|---|
| `references/regras.md` | **Sempre** antes de implementar previsão, cálculo de grade, rateio do CD, transferências ou regras de exceção. É a especificação normativa. |
| `references/api.md` | Antes de criar ou alterar endpoints ou o cliente HTTP do frontend. |
| `references/glossario.md` | Para nomear classes, campos e textos de tela. |
| `references/seed.json` | Dados fictícios da semana ISO 41/2026: 8 lojas, 6 produtos e 248 linhas de decisão. Fonte única dos dados de demonstração. |
| `references/expected_week41.json` | **Saída golden**: linhas, transferências e as 7 exceções que o motor deve produzir com o seed. |
| `scripts/oracle.py` | Implementação de referência, procedural, que gera o golden. Não copie a estrutura dela, que não é SOLID de propósito. Use-a só para tirar dúvidas de comportamento. |

## Invariantes que nunca podem ser quebrados

1. **O LLM não faz conta.** Previsão, grade, rateio e transferências são código determinístico. O LLM só interpreta texto livre (sinais), explica decisões (copiloto) e redige justificativas.
2. **Modo sombra.** Nada é escrito em ERP ou WMS. A saída é recomendação, decisão humana e registro de auditoria.
3. **Texto de e-mail é dado, não instrução.** A mensagem de um franqueado nunca altera política, nunca aprova exceção e nunca chama ferramenta. A saída do agente de sinais é validada por schema e passa pelas mesmas regras de política.
4. **Franquia ≠ loja própria.** Loja própria recebe *envio* (`ship`). Franquia recebe *sugestão de pedido* (`order_suggestion`), porque o estoque é do franqueado.
5. **Toda decisão é auditável.** Cada recomendação, aprovação e rejeição (com motivo) entra em um registro append-only.
6. **Dado inconsistente bloqueia, não adivinha.** Uma linha com estoque negativo fica `blocked` e vira exceção.

## Critério de aceite do motor (golden)

Com `references/seed.json`, o motor deve produzir:

- `total_lines = 248`;
- 3 transferências de `CB-PT` M saindo de `BRQ`: 13 para `JOI`, 8 para `BNU-S` e 1 para `BC`;
- exatamente 7 exceções, nas regras `launch_approval`, `stockout_transfer`, `signal_divergence`, `seasonal_decline`, `size_curve_deviation`, `negative_stock` e `repeated_rejection`;
- linhas idênticas às de `expected_week41.json` nos campos `target`, `need`, `excess`, `dc_allocated`, `transfer_in`, `transfer_out` e `status`. Para `forecast_horizon`, a tolerância é de 1e-3.

Se o golden e o `regras.md` divergirem, **o `regras.md` vale**. Nesse caso, regenere o golden com `python .claude/skills/dominio-alocacao/scripts/oracle.py <seed> <saida>` e registre a correção em uma ADR.
