---
name: adr
description: Cria, numera e atualiza Architecture Decision Records (formato MADR enxuto, em pt-BR) em docs/adr. Use sempre que uma decisão de arquitetura, tecnologia, padrão ou trade-off for tomada ou revista, e antes de implementar algo que contrarie uma ADR existente.
---

# ADRs

## Onde ficam e como se chamam

- Os arquivos ficam em `docs/adr/NNNN-titulo-em-kebab-case.md`, com numeração sequencial de 4 dígitos e sem reaproveitar números.
- `docs/adr/README.md` é o índice: uma tabela com `Nº | Título | Status | Data`. Atualize-o a cada ADR criada ou alterada.

## Quando escrever uma ADR

Escreva quando a decisão:

- for difícil de reverter, como linguagem, framework, persistência, fronteiras de camada ou contrato de API;
- tiver alternativas razoáveis que foram descartadas;
- impuser uma regra ao time, como "o LLM não calcula" ou "nada escreve no ERP".

Escolhas triviais, como o nome de uma variável ou a cor de um botão, não precisam de ADR.

## Como escrever

1. Copie `templates/adr.md`.
2. Em **Contexto**, descreva o problema e as restrições, com fatos.
3. Em **Opções consideradas**, liste pelo menos 2, cada uma com prós e contras reais.
4. Em **Decisão**, escreva uma frase no imperativo ("Usaremos X para Y").
5. Em **Consequências**, inclua as positivas, as **negativas** e o que precisará ser monitorado. Uma ADR sem consequência negativa está incompleta.
6. Em **Conformidade**, diga como verificar que a decisão está sendo seguida: um teste, uma regra de lint, um script ou um item de revisão.

## Status e ciclo de vida

- O ciclo é `Proposta → Aceita → (Depreciada | Substituída por NNNN)`.
- Nunca apague uma ADR nem reescreva a decisão de uma ADR que já foi aceita. Crie uma nova e marque a antiga como `Substituída por NNNN`.

## Checklist antes de concluir

- [ ] Número sequencial e índice atualizados.
- [ ] Pelo menos 2 opções, com prós e contras.
- [ ] Pelo menos 1 consequência negativa.
- [ ] Seção de Conformidade com uma verificação concreta.
- [ ] Links para as ADRs relacionadas.
