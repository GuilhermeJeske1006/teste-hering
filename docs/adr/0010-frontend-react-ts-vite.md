# 0010. Frontend em React + TypeScript + Vite, sem estado global, com cliente de API único

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** tech lead, designer de produto
- **Relacionadas:** [0002](0002-monolito-modular-fastapi-react.md), [0009](0009-estrategia-de-testes.md)

## Contexto

A tela é uma "mesa" com KPIs, abas (Exceções, Plano por loja, Sinais, Políticas, Registro) e um copiloto lateral. O estado é quase todo do servidor; o estado local se resume a aba ativa, formulário de rejeição e histórico do copiloto. Os testes E2E e de layout dependem de `data-testid` estáveis. O build precisa sair estático para o FastAPI servir.

## Opções consideradas

1. **React 18 + TypeScript strict + Vite, hooks por recurso, `ApiProvider` com cliente único, CSS próprio com tokens** — prós: build estático simples, tipagem do contrato, sem dependências de UI/estado; contras: escrevemos componentes e estilos do zero; sem cache de dados sofisticado.
2. **React + Redux/Zustand + biblioteca de componentes (MUI)** — prós: componentes prontos, estado global previsível; contras: peso e estilo genérico, mais dependências, estado global desnecessário para dados do servidor.
3. **HTMX + templates no FastAPI** — prós: sem build de front; contras: interações ricas (copiloto, desfazer, abas) ficam mais difíceis; contrato JSON da API perde o consumidor principal.

## Decisão

Usaremos **React 18 + TypeScript strict + Vite**, sem biblioteca de estado global nem de UI. Todo acesso HTTP passa por `src/api/client.ts`, injetado por contexto (`ApiProvider`) nos hooks. O contrato de `data-testid` da skill `frontend-react` é obrigatório. O build sai em `backend/app/static`.

Notas de implementação: o template atual do Vite traz React 19 e oxlint; fixamos **React 18** e **ESLint** (configs recomendadas de `react-hooks` e `typescript-eslint`) para seguir a skill. O `frontend/.npmrc` usa `legacy-peer-deps=true` para contornar um erro do npm 10.9 ao resolver dependências opcionais do Vitest 5.

## Consequências

- **Positivas:** bundle pequeno; testes com client fake sem mockar `fetch`; o contrato de testids protege os E2E.
- **Negativas:** sem cache e revalidação automática (refetch manual após decisão); componentes e acessibilidade são responsabilidade nossa; `legacy-peer-deps` deixa de checar peers automaticamente.
- **A monitorar:** duplicação de lógica de carregamento entre hooks; tamanho do bundle; necessidade real de React 19.

## Conformidade

- `npm --prefix frontend run lint`, `test -- --coverage` (≥ 80% de linhas) e `build` sem erros.
- `validate_layout.py` checa os testids obrigatórios e o grid de duas colunas.
