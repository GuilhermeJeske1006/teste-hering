# 0002. Monolito modular: FastAPI serve a API e o build do React

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** arquiteto de software, tech lead
- **Relacionadas:** [0003](0003-arquitetura-hexagonal-solid.md), [0010](0010-frontend-react-ts-vite.md)

## Contexto

O MVP atende um time pequeno de planejadores (dezenas de usuários), com um ciclo diário de recálculo de 248 linhas no seed e, em produção, alguns milhares. O time de desenvolvimento é pequeno, o deploy precisa ser simples e o sistema roda em modo sombra, sem integrações de escrita. Ao mesmo tempo, a interface precisa ser rica (abas, copiloto, decisões com desfazer).

## Opções consideradas

1. **Monolito: FastAPI serve `/api` e o build estático do React em um único processo** — prós: um deploy, um processo, sem CORS, versões de API e tela sempre casadas; contras: escala de API e de front juntas; build do front precisa existir antes de subir o backend.
2. **SPA e API separadas (dois deploys)** — prós: escalas e ciclos independentes, CDN para o front; contras: CORS, dois pipelines, contratos podem divergir entre versões.
3. **Next.js (BFF em Node + React)** — prós: SSR e roteamento prontos; contras: segunda linguagem no backend, o motor de cálculo ficaria em Python de qualquer forma, servidor Node em produção.
4. **Microsserviços (motor, sinais, copiloto)** — prós: isolamento de falhas; contras: complexidade operacional desproporcional ao MVP, transações e auditoria distribuídas.

## Decisão

Usaremos **um monolito modular**: o FastAPI (`backend/app/main.py`) expõe `/api/*` e serve `backend/app/static` (o build do Vite), com fallback de SPA para qualquer GET fora de `/api`.

## Consequências

- **Positivas:** `make build && make run` sobe tudo em `http://localhost:8000`; testes E2E rodam contra um único processo; sem CORS.
- **Negativas:** não há escala independente entre front e API; uma mudança de front exige redeploy do backend; o diretório `static/` é artefato de build e precisa ser gerado antes do `run`.
- **A monitorar:** tempo de build e tamanho do bundle; se o copiloto (LLM) passar a dominar a latência, avaliar extrair um worker.

## Conformidade

- Teste de feature confirma que `GET /` e `GET /qualquer-rota` devolvem o `index.html` e que `/api/*` inexistente devolve 404 em JSON.
- O fluxo E2E (`validar-fluxo`) sobe apenas `uvicorn app.main:app`.
