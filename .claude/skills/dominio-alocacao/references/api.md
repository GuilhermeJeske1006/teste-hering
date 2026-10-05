# Contrato da API (prefixo `/api`)

- JSON em `snake_case` e datas em ISO 8601.
- Erros seguem o formato `{"error": {"code": "...", "message": "..."}}`. A mensagem é em pt-BR e voltada ao usuário.
- O frontend consome a API **somente** pelo módulo `frontend/src/api/client.ts`.

| Método | Rota | Corpo / Query | Resposta | Erros |
|---|---|---|---|---|
| GET | `/api/health` | — | `{status:"ok", llm:"anthropic"\|"deterministic"}` | — |
| GET | `/api/summary` | — | `{week:{year,iso_week,start,end}, total_lines, within_policy, open_exceptions, transfers, shadow_mode}` | — |
| GET | `/api/skus` | — | `[{id,name,category,size_grid,sizes[],price,is_basic,is_launch}]` | — |
| GET | `/api/stores` | — | `[{id,name,ownership,execution_mode}]` | — |
| GET | `/api/plan` | `?sku=CB-PT` | `{sku, sizes[], rows:[{store_id,store_name,execution_mode,cells:[{size,stock,forecast_horizon,target,dc_allocated,transfer_in,transfer_out,excess,status}],total_movement}]}` | 404 `sku_not_found` |
| GET | `/api/transfers` | — | `[{sku,size,source,destination,qty}]` | — |
| GET | `/api/exceptions` | `?status=open\|approved\|rejected` (opcional) | `[{id,rule,severity,title,recommendation,explanation,facts[],status,decision?}]` em ordem de severidade | 422 em status inválido |
| POST | `/api/exceptions/{id}/decision` | `{action:"approve"\|"reject"\|"undo", reason?}` | a exceção atualizada | 404, 409 `already_decided`, 422 `reason_required` |
| GET | `/api/signals` | — | `[{id,store,author_role,received_at,text,interpreted}]` | — |
| POST | `/api/signals/interpret` | `{text, store?}` (texto de 1 a 2000 caracteres) | `{store,type,event,adjustments[],confidence,requires_human,reason}` | 422 `unparseable` |
| POST | `/api/copilot/ask` | `{question, history:[{role,content}], focus_sku?}` | `{answer, sources:[exception_id...]}` | 422, 503 `llm_unavailable` |
| GET | `/api/policies` | — | `[{key,label,description,value,unit}]` | — |
| GET | `/api/audit-log` | `?limit=50` | `[{timestamp,actor,action,subject,detail}]` do mais novo para o mais antigo | — |

O `answer` do copiloto vem em **Markdown restrito** (ADR 0016), com estes elementos:

- parágrafos separados por linha em branco;
- listas com `- ` e listas numeradas com `1. `, em que a linha seguinte recuada com 3 espaços é o detalhe do item;
- `**negrito**`;
- ids de exceção citados entre colchetes (`[abc123def0]`).

O frontend troca os ids por selos numerados que batem com `sources` e mostra todo o resto como texto. Nada vira HTML: títulos, links, tabelas e código aparecem literalmente.

Fora do prefixo `/api`, qualquer rota GET serve o `index.html` do build do React (fallback de SPA). `/assets/*` serve os estáticos.
