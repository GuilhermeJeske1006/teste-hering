# 0017. Deploy do ambiente de teste no Render, declarado em Blueprint (`render.yaml`)

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** tech lead, arquiteto de software
- **Relacionadas:** [0002](0002-monolito-modular-fastapi-react.md), [0008](0008-persistencia-sqlite-seed-json.md), [0011](0011-seguranca-e-governanca-de-ia.md), [0014](0014-ci-cd-github-actions-ghcr.md), [0015](0015-endurecimento-do-pipeline.md)

## Contexto

A ADR 0014 deixou o deploy para quando houvesse um destino. O destino agora existe: o projeto `teste-hering` no Render, ambiente `Production`. Em 2026-10-05, o serviço `mesa-alocacao` foi criado à mão no dashboard e está no ar em https://mesa-alocacao.onrender.com. O layout (6 combinações) e os 9 fluxos E2E passaram contra essa URL.

Fatos e restrições:

- O monolito cabe num único contêiner (ADR 0002), e o Dockerfile já passa pelo smoke test e pelo Trivy no CI (ADR 0015).
- O serviço está no plano Free: 0,1 CPU e 512 MB. Ele desliga depois de cerca de 15 minutos sem tráfego, e a volta leva uns 30 s, com 502 nesse intervalo. O plano Free não aceita disco persistente.
- Decisões e auditoria ficam em SQLite em `/data` (ADR 0008). Sem disco, esse arquivo some a cada desligamento e a cada deploy.
- `ANTHROPIC_API_KEY` não pode ir para o git nem para a imagem (ADR 0011).
- A configuração feita à mão não é versionada nem revisada. Ela também pode divergir do que o time acredita estar no ar.
- No primeiro push, os jobs do GitHub Actions falharam sem rodar, com a mensagem "job was not acquired by Runner". É um problema de cota ou cobrança da conta, não do código.

## Opções consideradas

1. **Web Service Docker buildado pelo Render a partir do repositório, declarado em `render.yaml`, com `autoDeployTrigger: checksPass`**
   - Prós: a configuração fica versionada e passa por PR. O Render usa o mesmo Dockerfile e o mesmo commit que o CI testou. Não precisa de segredo extra no GitHub nem no Render. O `checksPass` só implanta commits com o CI verde.
   - Contras: a imagem no ar não é, byte a byte, a publicada no GHCR, porque o `apt-get upgrade` pode trazer pacotes diferentes (ADR 0015).
2. **Render puxando a imagem do GHCR, com o deploy disparado pelo job `imagem`**
   - Prós: o que vai ao ar é exatamente a imagem que passou no smoke test e no Trivy.
   - Contras: o GHCR é privado, então o Render precisaria de uma credencial de registro (um PAT). O GitHub precisaria do Deploy Hook como segredo. E o deploy dependeria do Actions, que hoje não aloca runner.
3. **Manter a configuração só no dashboard**
   - Prós: já está pronta.
   - Contras: não é versionada, não é revisada e pode divergir sem ninguém perceber.
4. **Outro provedor (Fly.io, Cloud Run)**
   - Prós: alguns oferecem volume no plano gratuito.
   - Contras: o projeto `teste-hering` e a conta já existem no Render. Trocar exigiria nova conta, nova integração com o GitHub e novos segredos.

## Decisão

Usaremos o **Blueprint `render.yaml` na raiz** para declarar o Web Service `mesa-alocacao`:

- runtime Docker, a partir de `master`, na região `ohio`, no projeto `teste-hering` (ambiente `Production`);
- plano Free, health check em `/api/health` e `PORT=8000`;
- `autoDeployTrigger: checksPass`, para que só commits com o CI verde subam;
- `buildFilter` restrito a `Dockerfile`, `.dockerignore`, `backend/**` e `frontend/**`, para que ADRs e relatórios não disparem build;
- `ANTHROPIC_API_KEY` com `sync: false`: o dashboard pede o valor, e o git nunca o vê.

O plano Free vale **só para o ambiente de teste**. Antes de qualquer uso com decisões reais, o serviço passa para `starter` com disco em `/data`. O bloco `disk` já está comentado no `render.yaml`.

## Consequências

- **Positivas:**
  - A configuração do ambiente é revisada em PR como o resto do código.
  - Nenhum segredo novo no GitHub e nenhuma chave no repositório.
  - Commit com CI vermelho não chega ao ambiente.
  - O mesmo `render.yaml` recria o serviço do zero.
- **Negativas:**
  - **No Free, decisões e auditoria são perdidas** a cada desligamento ou deploy. Isso contraria o invariante 4 se alguém usar o ambiente para decidir de verdade. Aqui ele serve só para demonstração.
  - O primeiro acesso depois de inatividade espera uns 30 s e pode receber 502.
  - Enquanto o Actions não alocar runner, o `checksPass` não implanta nada. O deploy manual pelo dashboard continua possível.
  - A imagem no ar é rebuildada pelo Render e pode diferir da imagem do GHCR por causa do `apt-get upgrade`.
  - O `render blueprints validate` do CLI só valida `repo` e `branch` se a conta do CLI enxergar o repositório.
  - A documentação do Render não garante que um bloco `projects:` reaproveite um projeto existente com o mesmo nome. Na primeira vinculação, confira o preview do Blueprint antes de aplicar.
- **A monitorar:**
  - A cota ou cobrança do Actions: sem ela, o deploy automático para.
  - O primeiro uso com decisões reais: é o gatilho para `starter` + disco.
  - Se o rebuild do Render divergir da imagem testada, reavaliar a opção 2.
  - Um `HEAD /` hoje responde 405. Isso pode quebrar monitores de uptime que usem HEAD.

## Conformidade

- `make render-validate` (`render blueprints validate render.yaml`) passa.
- `render.yaml` não tem `value:` para `ANTHROPIC_API_KEY`. O pre-commit já bloqueia chaves `sk-ant-` (ADR 0014).
- Depois de cada deploy, `validate_layout.py --url https://mesa-alocacao.onrender.com` e `validate_flows.py --url https://mesa-alocacao.onrender.com --no-server` passam.
- No dashboard, o serviço aparece vinculado ao Blueprint e sem divergências pendentes de sincronização.
