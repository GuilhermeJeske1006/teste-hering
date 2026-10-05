# 0001. Registrar decisões de arquitetura com ADRs

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** arquiteto de software, tech lead
- **Relacionadas:** todas as demais

## Contexto

A Mesa de Alocação nasce com decisões difíceis de reverter (monolito, hexagonal, LLM sem contas, modo sombra) e é construída em boa parte por um agente (Claude Code) que precisa de uma fonte de verdade escrita para não "inventar" arquitetura. O time de planejamento também precisa entender por que o sistema recomenda e não executa. Sem registro, o motivo de cada escolha se perde em conversas e commits.

## Opções consideradas

1. **ADRs em MADR enxuto, em pt-BR, versionadas no repositório** — prós: ficam ao lado do código, revisadas no mesmo PR, legíveis pelo time de negócio; contras: exigem disciplina para atualizar o índice e criar ADR nova em vez de editar a antiga.
2. **Wiki externa (Confluence/Notion)** — prós: edição fácil por não desenvolvedores; contras: desatualiza em relação ao código, não passa por revisão, o agente não lê sem integração.
3. **Só comentários no código e mensagens de commit** — prós: zero processo; contras: não registra alternativas descartadas nem consequências, e se espalha.

## Decisão

Usaremos **ADRs no formato MADR enxuto, em pt-BR, em `docs/adr/NNNN-titulo.md`**, com índice em `docs/adr/README.md` e ciclo `Proposta → Aceita → (Depreciada | Substituída por NNNN)`.

## Consequências

- **Positivas:** decisões e trade-offs ficam rastreáveis; o agente consulta as ADRs antes de contrariar uma decisão; revisão de PR inclui a ADR.
- **Negativas:** custo de escrita em cada decisão relevante; risco de ADRs burocráticas para escolhas triviais.
- **A monitorar:** ADRs com status "Proposta" há mais de duas semanas; índice divergente dos arquivos.

## Conformidade

- Checklist da skill `adr` em todo PR que muda arquitetura.
- Revisão manual: o índice lista todos os arquivos `docs/adr/[0-9]*.md` (`ls docs/adr | wc -l` bate com a tabela).
