---
name: frontend-react
description: Convenções do frontend React + TypeScript da Mesa de Alocação (estrutura, componentes, cliente de API, tokens de design, data-testid obrigatórios, Vitest + Testing Library). Use ao criar ou alterar qualquer arquivo em frontend/.
---

# Frontend React + TypeScript

**Stack:** Vite, React 18, TypeScript `strict`, Vitest, @testing-library/react, @testing-library/user-event e jsdom. Não use biblioteca de estado global nem de UI: CSS próprio com tokens, em um único `src/styles/tokens.css` mais CSS Modules.

## Estrutura

```
frontend/src/
  api/client.ts          # ÚNICO ponto de fetch. Funções tipadas por endpoint (ver api.md). Lança ApiError{code,message}.
  api/types.ts           # tipos espelhando os schemas do backend
  hooks/                 # useSummary, useExceptions, usePlan(sku), useSignals, usePolicies, useAuditLog, useCopilot
  components/            # apresentacionais, sem fetch: KpiBar, ExceptionCard, ExceptionQueue, PlanTable, SkuPicker,
                         # SignalCard, SignalTester, PolicyList, AuditLog, CopilotPanel, Tabs, SeverityBadge
  pages/AllocationDesk.tsx  # compõe tudo; abas: Exceções | Plano por loja | Sinais | Políticas | Registro
  styles/tokens.css
  test/                  # setup do Vitest, utilidades de render e fixtures (derivadas do seed)
```

## SOLID no frontend

- **S:** um componente apresentacional só renderiza props. Os hooks cuidam de dados e estado.
- **O:** `ExceptionCard` renderiza qualquer `rule` sem `switch`. Severidade e rótulos vêm de um mapa `SEVERITY_META`.
- **D:** os hooks recebem o `client` por contexto (`ApiProvider`). Nos testes, injete um client fake e **não** mocke `fetch` globalmente.

## Layout e UX (validado pela skill `validar-layout`)

- Desktop (≥ 980px): grid `minmax(0,1fr) 380px`, com o conteúdo das abas à esquerda e o Copiloto fixo (sticky) à direita. Em telas menores, uma coluna só, com o Copiloto depois do conteúdo.
- O topo tem título, semana, a tag "Modo sombra · nada é executado" e uma faixa de KPIs.
- Nenhuma rolagem horizontal no `body` em 390px, 768px ou 1280px. Tabelas largas ficam dentro de um contêiner com `overflow-x:auto`.
- Tema claro e escuro via `prefers-color-scheme` e tokens. Contraste AA. Foco visível. Respeite `prefers-reduced-motion`.
- Severidade aparece pela cor da borda **e** por um texto ("Crítica", "Alta", "Média", "Baixa"), nunca só pela cor.
- Textos em pt-BR, voz ativa, botões dizendo exatamente o que fazem ("Aprovar", "Confirmar rejeição").

## `data-testid` obrigatórios (contrato com os testes E2E — não renomeie)

| testid | Elemento |
|---|---|
| `kpi-total`, `kpi-within-policy`, `kpi-open-exceptions` | valores dos KPIs (só o número no texto) |
| `shadow-mode-tag` | a tag de modo sombra |
| `tab-exceptions`, `tab-plan`, `tab-signals`, `tab-policies`, `tab-audit` | botões de aba (`role="tab"`, `aria-selected`) |
| `exception-card` | cada card, com `data-rule`, `data-severity` e `data-status` |
| `btn-approve`, `btn-reject`, `btn-undo`, `btn-ask-copilot` | dentro do card |
| `select-reject-reason`, `btn-confirm-reject` | o formulário de rejeição dentro do card |
| `decision-status` | o texto do status depois da decisão |
| `sku-chip` (com `data-sku`), `plan-table`, `plan-row` (com `data-store`) | aba Plano |
| `signal-card`, `signal-input`, `btn-interpret`, `signal-result` | aba Sinais |
| `policy-row` | aba Políticas |
| `audit-item` | aba Registro |
| `copilot-input`, `btn-ask`, `copilot-message` (com `data-role="user"\|"assistant"`), `copilot-suggestion` | Copiloto |

## Estados

- Todo hook expõe `{data, error, loading}`.
- Carregamento usa skeleton, sem spinner bloqueando a tela.
- Erro mostra a mensagem em pt-BR vinda do `ApiError` e um botão "Tentar de novo".
- Lista vazia tem um texto explicando o que apareceria ali.

## Testes (Vitest)

- Um `*.test.tsx` por componente e por hook, consultando por papel ou rótulo (`getByRole`), e por `testid` só quando não houver papel.
- Cenários obrigatórios:
  - `ExceptionCard` aprova e chama `onDecide("approve")`;
  - rejeitar abre o select, e confirmar envia o motivo;
  - `PlanTable` mostra "envio" e "sugestão de pedido";
  - `CopilotPanel` envia a pergunta e mostra a resposta, e mostra o erro quando o client falha;
  - `KpiBar` formata números em pt-BR.
- Cobertura mínima: **80%** de linhas em `src/` (exceto `main.tsx`).
- `npm run build` sem erros de tipo. `npm run lint` (eslint com as configs recomendadas de react-hooks e typescript) sem erros.

## Integração com o monolito

- O `vite.config.ts` gera o build em `../backend/app/static` e faz proxy de `/api` para `http://localhost:8000` no modo dev.
- Em produção, o FastAPI serve o build. Não existe servidor Node em produção.
