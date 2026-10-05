# 0014. CI/CD com hooks locais, GitHub Actions e imagem Docker no GHCR

- **Status:** Aceita; os gatilhos do CI e as etapas do job `imagem` foram revistos na [0015](0015-endurecimento-do-pipeline.md)
- **Data:** 2026-10-05
- **Decisores:** tech lead, arquiteto de software
- **Relacionadas:** [0002](0002-monolito-modular-fastapi-react.md), [0009](0009-estrategia-de-testes.md), [0011](0011-seguranca-e-governanca-de-ia.md)

## Contexto

As validações (testes, SOLID, layout e fluxos) já existem como scripts das skills, mas só rodavam à mão. Precisamos que elas rodem sozinhas no fluxo de commit e push, que nenhum segredo (`ANTHROPIC_API_KEY` no `.env`) vaze para o git e que cada versão aprovada vire um artefato implantável. O monolito (ADR 0002) cabe numa única imagem. O código fica no GitHub, e ainda não existe um ambiente de destino definido.

## Opções consideradas

1. **Hooks locais (`.githooks`) + GitHub Actions + imagem no GitHub Container Registry** — prós: feedback em segundos no commit; o CI repete as mesmas validações num ambiente limpo; o GHCR usa o `GITHUB_TOKEN`, sem segredo extra; a imagem roda em qualquer destino; contras: os hooks podem ser pulados com `--no-verify`; os minutos do Actions são limitados em repositórios privados.
2. **Só CI, sem hooks** — prós: menos peças; contras: o erro só aparece minutos depois do push e um segredo já teria chegado ao remoto.
3. **Framework `pre-commit` + outro CI (GitLab CI, Jenkins)** — prós: ecossistema de hooks pronto; contras: dependência a mais; o repositório e as credenciais já estão no GitHub.
4. **Deploy direto num provedor (Render, Fly.io, Cloud Run) no CD** — prós: ambiente no ar a cada merge; contras: o destino ainda não foi escolhido e cada provedor exige conta e segredos próprios.

## Decisão

Usaremos **três camadas**, todas reaproveitando os scripts das skills:

- **Hooks locais** (`make hooks` liga `core.hooksPath=.githooks`):
  - `pre-commit` bloqueia `.env` e chaves `sk-ant-` e roda checagens rápidas da área alterada: ruff, mypy, pytest unit e arquitetura no backend, ESLint e Vitest no frontend;
  - `commit-msg` exige Conventional Commits;
  - `pre-push` roda `run_tests.sh` completo mais a arquitetura.
- **CI** (`.github/workflows/ci-cd.yml`), em todo push e pull request: jobs `testes`, `solid` e `e2e` (layout e os 9 fluxos com Playwright), com relatórios como artefatos e no resumo do job.
- **CD**: quando a branch padrão ou uma tag `v*` passa no CI, o job `imagem` publica `ghcr.io/<owner>/<repo>` com as tags `sha-<curto>`, `latest` (branch padrão) e a versão (tag). O deploy no ambiente fica para uma ADR futura, quando o destino for escolhido.

## Consequências

- **Positivas:** nenhuma etapa vermelha chega à imagem; segredo bloqueado antes do commit; a imagem é a mesma em todo ambiente (`ANTHROPIC_API_KEY` só entra em tempo de execução); o `.dockerignore` mantém `.env`, `.git` e relatórios fora da imagem.
- **Negativas:** o `pre-push` leva cerca de 10 s e precisa do `.venv` e do `node_modules`; o job `e2e` instala o Chromium a cada execução (alguns minutos); os hooks são opt-in (`make hooks`) e contornáveis com `--no-verify`, por isso o CI é a barreira de verdade.
- **A monitorar:** tempo do pipeline; instabilidade dos fluxos E2E; crescimento da imagem (274 MB hoje); falta de deploy automático até haver um ambiente.

## Conformidade

- `actionlint` (com shellcheck) no workflow e `shellcheck` nos hooks sem achados.
- Proteção da branch padrão exigindo os checks `testes`, `solid` e `e2e` (configurar no GitHub).
- Teste manual dos bloqueios: `.env` no stage, chave `sk-ant-` no diff e mensagem fora do padrão (todos rejeitados).
