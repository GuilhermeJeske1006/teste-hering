# 0007. Modo sombra: recomendar e registrar, nunca escrever no ERP ou WMS

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** líder de planejamento, arquiteto de software, diretoria de operações
- **Relacionadas:** [0004](0004-motor-deterministico-llm-nao-calcula.md), [0011](0011-seguranca-e-governanca-de-ia.md)

## Contexto

O sistema é novo, o planejamento ainda opera na planilha e um erro de envio custa frete, ruptura e atrito com franqueados. Antes de automatizar, precisamos medir a qualidade das recomendações contra o que o planejador decide. Franquias têm estoque próprio, então o sistema só pode sugerir pedido para elas.

## Opções consideradas

1. **Modo sombra: o sistema recomenda, o planejador decide e tudo vai para auditoria; nada é escrito no ERP/WMS** — prós: risco operacional zero, gera base para medir acurácia, ganha confiança; contras: o planejador ainda precisa lançar as ordens no ERP manualmente, sem ganho de tempo na execução.
2. **Execução automática do que está dentro da política desde o dia 1** — prós: ganho imediato de produtividade; contras: sem histórico de acurácia, erro vira movimento físico de estoque, integração de escrita aumenta o escopo.
3. **Execução com aprovação item a item no ERP** — prós: controle total; contras: integração bidirecional complexa, mesma carga de trabalho da planilha.

## Decisão

Usaremos **modo sombra no MVP**: o resumo traz `shadow_mode: true`, a interface mostra "Modo sombra · nada é executado" e não existe nenhum adaptador de escrita para ERP ou WMS.

## Consequências

- **Positivas:** risco operacional nulo; cada decisão vira dado para calibrar políticas; o discurso para o time é "o sistema sugere, você decide".
- **Negativas:** o ganho de produtividade fica limitado à triagem; há retrabalho de lançar ordens no ERP; o valor percebido pode cair se o modo durar demais.
- **A monitorar:** taxa de aprovação por regra (candidata a sair do modo sombra quando passar de um limite combinado); tempo do planejador por semana.

## Conformidade

- Teste de feature: `GET /api/summary` devolve `shadow_mode: true`.
- Revisão: nenhum port de escrita externa em `application/ports.py`; `check_architecture.py` restringe imports de rede ao adaptador do LLM.
- Fluxo E2E f1 verifica a tag de modo sombra visível.
