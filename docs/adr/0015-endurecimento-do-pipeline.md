# 0015. Endurecimento do pipeline: gatilhos, actions por SHA, smoke test e varredura da imagem

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** tech lead, arquiteto de software
- **Relacionadas:** [0014](0014-ci-cd-github-actions-ghcr.md), [0011](0011-seguranca-e-governanca-de-ia.md), [0002](0002-monolito-modular-fastapi-react.md)

## Contexto

Revisamos o pipeline da ADR 0014 com actionlint, shellcheck e hadolint e rodamos localmente cada job. Os linters passaram, mas a revisão achou lacunas:

- O CI rodava duas vezes por PR, uma pelo push (qualquer branch) e outra pelo `pull_request`.
- As actions eram referenciadas por tag móvel (`@v4`), e quem controla a tag controla o código que roda no job com `packages: write`.
- A imagem era publicada sem ser executada nem varrida. Na primeira varredura, o Trivy achou uma CVE HIGH que já tem correção, a CVE-2026-103111 em `libpcre2-8-0`. Ela vem da base `python:3.12-slim` de 01/10/2026, a mais recente no Docker Hub.
- O `.gitignore` e o pre-commit só cobriam `.env`, então `.env.local` e `.env.production` passavam.
- O HEALTHCHECK usava a forma shell (DL3025 no hadolint) e o `USER` era um nome (DL3066), que o Kubernetes não consegue verificar com `runAsNonRoot`.
- Quando o monolito não subia no job `e2e`, o log do uvicorn não aparecia.

## Opções consideradas

1. **Gatilhos do CI**
   - **(a) Push em toda branch + PR (como estava):** prós: uma branch sem PR também passa pelo CI. Contras: cada PR roda duas vezes e gasta o dobro de minutos.
   - **(b) Push só na branch padrão e nas tags `v*`, mais PR:** prós: uma execução por mudança. Contras: uma branch sem PR só tem o `pre-push` local.
2. **Referência das actions**
   - **(a) Tag maior (`@v4`):** prós: as atualizações chegam sozinhas. Contras: a tag é móvel, então é um vetor de supply chain.
   - **(b) SHA completo + Dependabot:** prós: a referência é imutável e cada atualização é revisada num PR. Contras: um PR semanal do Dependabot para revisar.
3. **Verificação da imagem antes de publicar**
   - **(a) Nenhuma:** contras: uma imagem quebrada ou vulnerável chega ao GHCR.
   - **(b) Smoke test + Trivy no contêiner `aquasec/trivy` com versão fixa, pelos alvos `make docker-smoke` e `make docker-scan`:** prós: a máquina local e o CI rodam o mesmo comando, sem action de terceiros. Contras: o banco do Trivy é baixado a cada execução.
   - **(c) `trivy-action`:** contras: é mais uma action de terceiros com acesso ao job, e o contêiner fixo faz o mesmo.
4. **Base com CVE corrigida no Debian e ainda não na imagem oficial**
   - **(a) Esperar a imagem base:** contras: o gate fica vermelho por dias.
   - **(b) `apt-get upgrade` no estágio runtime:** prós: fecha a janela já no próximo build. Contras: o build fica menos reprodutível.
   - **(c) Trocar a base por distroless ou Chainguard:** contras: muda o runtime. Fica para depois.

## Decisão

Fecharemos as lacunas assim:

- **Gatilhos:** o CI roda no push de `main`/`master` e de tags `v*`, mais `pull_request`. O `concurrency` só cancela execuções de PR, nunca uma publicação.
- **Actions:** todas fixadas por SHA, com a versão no comentário. O Dependabot propõe toda semana as atualizações das actions e das imagens base.
- **Job `imagem`:** roda em toda execução. Faz o build local, depois `make docker-smoke` (healthcheck *healthy*, `/api/health`, SPA, modo sombra, usuário não-root e nenhuma chave na imagem) e `make docker-scan` (Trivy 0.75.0, que falha em CRITICAL ou HIGH com correção disponível). Só publica no GHCR na branch padrão ou numa tag, com o mesmo builder e o mesmo cache do build testado.
- **Dockerfile:** `apt-get upgrade` no estágio runtime, `USER 10001:10001` e HEALTHCHECK em JSON.
- **Segredos:** `.env.*` é ignorado pelo git e bloqueado no pre-commit. A única exceção é `.env.example`.
- **Diagnóstico:** o job `e2e` falha explicitamente se o monolito não subir e mostra o `uvicorn.log`.

## Consequências

- **Positivas:**
  - A imagem publicada é a que passou no smoke test e na varredura.
  - O PR já mostra se a imagem quebraria.
  - A referência das actions é imutável.
  - A máquina local e o CI usam os mesmos alvos do `make`.
- **Negativas:**
  - O job `imagem` roda em todo PR, o que soma alguns minutos e o download do banco do Trivy.
  - O `apt-get upgrade` deixa o build menos reprodutível.
  - Uma CVE nova, sem relação com a mudança, pode travar o merge até a base ser corrigida.
  - Os PRs do Dependabot precisam de revisão.
  - Uma branch sem PR não passa pelo CI.
- **A monitorar:**
  - Falsos positivos do Trivy: se um aparecer, registre no `.trivyignore` com justificativa e prazo.
  - O tempo do job `imagem`.
  - O tamanho da imagem.
  - Se o `apt-get upgrade` continuar necessário, reavaliar a opção 4c.

## Conformidade

- `grep -nE 'uses: [^@]+@v[0-9]' .github/workflows/*.yml` não retorna nada: toda action está fixada por SHA.
- `actionlint`, `shellcheck` (hooks e `scripts/smoke-image.sh`) e `hadolint` passam sem achados.
- `make docker-build docker-smoke docker-scan` passa localmente.
- Teste do pre-commit num repositório descartável: `.env`, `.env.local` e `config/.env.production` são rejeitados, e `.env.example` é aceito.
