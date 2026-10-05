---
description: Roda todas as validações da Mesa de Alocação (testes, SOLID, layout e fluxos) e resume o estado do projeto.
argument-hint: "[testes|solid|layout|fluxo]"
---

# /validar

Escopo pedido: `$ARGUMENTS` (vazio significa todos).

Para cada item do escopo, carregue a skill correspondente e siga as instruções dela **na ordem abaixo**. Se uma etapa falhar, continue rodando as próximas, para que o diagnóstico fique completo.

1. `testes` → skill `validar-testes`.
2. `solid` → skill `revisar-solid`.
3. `layout` → skill `validar-layout`. Antes, faça o build do frontend e suba o monolito em segundo plano na porta 8000; depois, encerre o processo.
4. `fluxo` → skill `validar-fluxo`. O script sobe o próprio servidor.

No fim, mostre uma tabela `Validação | Resultado | Problemas | Relatório`, com os 3 problemas mais importantes e a correção sugerida para cada um. **Não corrija nada** sem o usuário pedir. Este comando só diagnostica.
