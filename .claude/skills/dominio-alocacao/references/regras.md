# Regras normativas do motor de alocação

Os valores numéricos vêm sempre de `seed.policies`. Nunca coloque números fixos no código: injete-os via `Policies`.
A notação `cur` é a semana ISO corrente (`seed.current_week.iso_week`, que vale 41). O horizonte `H` é `policies.horizon_weeks` (2).

## 1. Linha de decisão

Cada linha é uma combinação **loja × produto × tamanho** que tem registro em `seed.stock`. São 248 linhas com o seed.

## 2. Previsão semanal (`weekly_forecast`)

- **Produto com histórico:** média ponderada das 4 últimas semanas, `Σ forecast_weights[i] × vendas[cur-1-i]`, com pesos `[0.4, 0.3, 0.2, 0.1]` (o primeiro peso vai para a semana mais recente). Semana sem registro conta como 0.
- **Lançamento** (`launch_week` definido): média de `qty_first_2_weeks` dos `similar_skus` na mesma loja e no mesmo tamanho, dividida por 2. Usa `reference_sales`. Se não houver referência, a previsão é 0.

## 3. Previsão do horizonte (`forecast_horizon`)

`forecast_horizon = weekly × H × (1 + uplift_evento + uplift_sinais)`

- **uplift_evento:** soma de `uplift_by_category[categoria]` dos eventos em que a loja está em `stores` e que se sobrepõem ao horizonte (`start_week ≤ cur+H-1` e `end_week ≥ cur`).
- **uplift_sinais:** soma de `pct/100` dos ajustes de sinais da mesma loja com `pct ≤ signal_max_auto_adjust_pct` e escopo `"all"`, `"<SKU>"` ou `"<SKU>:<TAM>"` compatível. Ajustes acima do limite **não** entram no cálculo e geram a exceção `signal_divergence`.

## 4. Alvo, necessidade e excesso

- Se `stock < 0`, a linha fica `status = "blocked"`, com `target`, `need` e `excess` iguais a 0.
- Caso contrário:
  - `min_display` é `min_display_basic` se `is_basic`, senão `min_display_other`;
  - `target = max(min_display, ceil(forecast_horizon × cover_factor))`;
  - `need = target - stock`, quando positivo;
  - se `need ≤ 0` e `stock > forecast_horizon × excess_trigger_factor`, então `excess = floor(stock - forecast_horizon × excess_keep_factor)`;
  - nos demais casos, `need = excess = 0`.

## 5. Rateio do CD (por produto × tamanho)

- `total = Σ need` e `avail = dc_stock`.
- Se `total ≤ avail`, cada linha recebe `dc_allocated = need`.
- Caso contrário, o rateio é proporcional:
  1. `dc_allocated = floor(need × avail / total)`;
  2. as unidades que sobram vão, uma por linha, na ordem de **maior falta** (`need - dc_allocated` decrescente) e, em empate, pelo id da loja.

## 6. Transferência entre lojas (só quando o CD não cobre)

1. Percorra as linhas com necessidade pela **maior venda perdida estimada** (`forecast_horizon - stock - dc_allocated`, decrescente; em empate, pelo id da loja).
2. A linha é candidata a receber transferência se `short = need - dc_allocated > 0` e a cobertura após o rateio, `(stock + dc_allocated) / weekly`, for menor que `H`.
3. As origens possíveis são linhas do mesmo produto e tamanho com excesso ainda disponível (`excess - transfer_out > 0`) e cobertura própria `stock / weekly > transfer_min_source_cover_weeks`. Elas são ordenadas pelo maior excesso disponível e, em empate, pelo id da loja.
4. A quantidade transferida é `min(excesso disponível, short)`. Ela atualiza `transfer_out` na origem e `transfer_in` no destino.

## 7. Modo de execução

- Loja própria (`ownership = "own"`) usa `execution_mode = "ship"`.
- Franquia usa `execution_mode = "order_suggestion"`.

## 8. Regras de exceção (cada uma é uma classe independente, que implementa `ExceptionRule`)

| # | Regra (`rule`) | Severidade | Condição | Agrupamento |
|---|---|---|---|---|
| 1 | `launch_approval` | critical | O produto é lançamento e `cur - launch_week < launch_approval_weeks` | 1 por produto, com `need` por loja |
| 2 | `stockout_transfer` | high | Existe transferência proposta | 1 por produto × tamanho × origem, com a lista de destinos |
| 3 | `signal_divergence` | high | O ajuste do sinal tem `pct > signal_max_auto_adjust_pct` | 1 por ajuste |
| 4 | `seasonal_decline` | medium | Em ≥ `seasonal_min_stores` lojas, a queda de vendas das últimas 3 semanas sobre as 3 anteriores é ≥ `seasonal_decline_pct`% e a cobertura (estoque total / previsão semanal total do produto na loja) é ≥ `seasonal_min_cover_weeks`. Lançamentos ficam de fora. | 1 por produto |
| 5 | `size_curve_deviation` | medium | Nas últimas `size_curve_weeks` semanas, com total ≥ `size_curve_min_units`, pelo menos `size_curve_min_sizes` tamanhos desviam ≥ `size_curve_deviation_pp` pontos percentuais da curva padrão. Lançamentos ficam de fora. | 1 por loja × produto |
| 6 | `negative_stock` | medium | Linha `blocked` | 1 por linha |
| 7 | `repeated_rejection` | low | O histórico tem ≥ `repeated_rejection_count` rejeições para a mesma loja × produto | 1 por loja × produto |
| 8 | `auto_execution_limit` | medium | Em loja própria, `Σ dc_allocated × price` das linhas não cobertas por `launch_approval` passa de `auto_execution_max_value_brl` | 1 por loja (com o seed, não dispara) |

A ordem de saída das exceções é a ordem da tabela. Dentro de cada regra, a ordem é pelos ids.

Toda exceção tem `id` estável e determinístico (por exemplo, `sha1(rule + chave)[:10]`), `title`, `recommendation` e `explanation` em pt-BR, `facts` (lista de strings curtas com números) e `status` (`open`, `approved` ou `rejected`).

**A explicação é gerada por template determinístico a partir dos números.** O LLM pode reescrevê-la de forma mais natural, mas nunca é a fonte dos números.

## 9. Decisões

- Ações possíveis: `approve` e `reject`. A rejeição exige um `reason` com um dos motivos abaixo:
  - "Conheço um fator que o modelo não vê"
  - "Restrição comercial com o franqueado"
  - "Dado de entrada errado"
  - "Prefiro esperar mais uma semana"
- Decidir uma exceção que já foi decidida retorna **409**. Desfazer (`undo`) volta o status para `open` e também fica registrado no log.
- Toda decisão grava um evento no registro de auditoria: `timestamp`, `actor`, `action`, `subject` (o título da exceção), `detail` (o motivo, quando houver) e `exception_id`.

## 10. KPIs do resumo

- `total_lines`;
- `within_policy`: linhas que não são `blocked` e não são referenciadas por nenhuma exceção aberta;
- `open_exceptions`;
- `transfers`;
- `shadow_mode: true`.

## 11. Agente de sinais (LLM)

- **Entrada:** o texto livre e a loja (opcional).
- **Saída validada** (pydantic):
  - `store`: id existente, ou `null`;
  - `type`: `local_event`, `lost_sales`, `size_curve`, `stock_mismatch` ou `other`;
  - `event`;
  - `adjustments[{scope, pct}]`;
  - `confidence` entre 0 e 1;
  - `requires_human` (bool);
  - `reason`.
- `requires_human` é **recalculado pelo código** a partir da política (qualquer `pct` acima do limite, ou `type` igual a `size_curve`). O valor que vem do LLM é ignorado.
- O prompt delimita a mensagem entre marcadores e manda tratá-la como dado.
- Se o JSON for inválido, há uma única nova tentativa. Se falhar de novo, a resposta é `422` com a mensagem "Não consegui interpretar".

## 12. Copiloto (LLM)

- O contexto vem de um `ContextBuilder`: políticas, exceções com status, sinais e o plano resumido do produto em foco.
- As instruções exigem:
  - responder em pt-BR, em até 6 frases;
  - usar só os dados do contexto;
  - nunca executar nada;
  - dizer quando a decisão é do planejador.
- O histórico vai no máximo até os 8 turnos mais recentes.
- Sem `ANTHROPIC_API_KEY`, o adaptador determinístico responde por template, combinando a pergunta com palavras-chave das exceções.
