# 0013. Interpretações da especificação onde ela é ambígua

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** arquiteto de software, líder de planejamento (a validar)
- **Relacionadas:** [0005](0005-regras-de-excecao-plugaveis.md), [0011](0011-seguranca-e-governanca-de-ia.md), [0012](0012-parametros-implicitos-viram-politicas.md)

## Contexto

O `regras.md` e o `api.md` deixam alguns pontos em aberto que afetam números exibidos ao planejador. O principal é o KPI "dentro da política" (§10): ele exclui as linhas "referenciadas por exceção aberta", mas a especificação não diz quais linhas cada regra referencia. O golden não cobre esse KPI.

## Opções consideradas

1. **Cada regra declara as linhas que afeta (`line_keys`), de forma explícita e testada** — prós: o KPI fica explicável ("esta linha está fora porque a exceção X a cobre") e cada regra decide seu escopo; contras: o número depende de escolhas por regra que o negócio ainda precisa validar.
2. **Só linhas bloqueadas ficam fora da política** — prós: simples; contras: ignora exceções abertas, contrariando o §10.
3. **Uma exceção referencia todas as linhas do produto** — prós: regra única; contras: superestima o impacto (um estoque negativo tiraria 40 linhas da política).

## Decisão

Usaremos **escopo explícito por regra**:

| Regra | Linhas referenciadas |
|---|---|
| `launch_approval` | todas as linhas do produto lançado |
| `stockout_transfer` | origem e destinos do produto × tamanho |
| `signal_divergence` | linhas da loja compatíveis com o escopo do ajuste (`all` = a loja inteira) |
| `seasonal_decline` | linhas do produto nas lojas em queda |
| `size_curve_deviation` | linhas da loja × produto |
| `negative_stock` | a linha bloqueada |
| `repeated_rejection` | linhas da loja × produto |
| `auto_execution_limit` | linhas da loja com envio, fora de lançamentos em aprovação |

Com o seed, isso dá **131 de 248** linhas dentro da política.

Outras interpretações registradas aqui:

- `undo` em exceção aberta devolve **409 `not_decided`** (o `api.md` só cita `already_decided`).
- Rejeitar com motivo fora da lista devolve **422 `reason_required`**, o mesmo erro de motivo ausente.
- `total_movement` do plano é o **saldo** da loja: `Σ (dc_allocated + transfer_in − transfer_out)`.
- O cálculo do plano grava um evento `recommend` (ator "sistema") no registro de auditoria, para cumprir "cada recomendação entra no registro".
- `repeated_rejection` conta só o `decision_history` do seed; rejeições da semana corrente passam a contar no próximo ciclo.
- `/api/signals/interpret` não persiste o sinal: ele só devolve a interpretação para o planejador avaliar.
- Dentro de cada regra, a ordem é pelo id das entidades (loja, produto, tamanho), como no oráculo.

## Consequências

- **Positivas:** o KPI é auditável e testado; cada escolha fica num lugar só (a regra) e é fácil de mudar.
- **Negativas:** o valor "131" pode não bater com a intuição do negócio, sobretudo no sinal de "+40% em tudo", que tira a loja BNU-C inteira da política; uma mudança de escopo altera o KPI histórico.
- **A monitorar:** feedback dos planejadores sobre o KPI; pedidos de persistir sinais testados.

## Conformidade

- `tests/unit/application/test_get_summary.py` e `tests/feature/test_resumo.py::test_linhas_dentro_da_politica_excluem_as_referenciadas_quando_ha_excecoes` (131).
- Testes de cada regra em `tests/unit/domain/rules/` verificam `line_keys`.
- `tests/feature/test_decisoes.py` cobre `not_decided` e `reason_required`.
