# Glossário (o código usa o termo em inglês; a tela usa o termo em pt-BR)

| Código | Tela (pt-BR) | Significado |
|---|---|---|
| `AllocationLine` | linha de decisão | loja × produto × tamanho |
| `weekly_forecast` / `forecast_horizon` | previsão semanal / previsão 2 semanas | §2–3 de regras.md |
| `target` | alvo | estoque desejado ao fim do horizonte |
| `need` | necessidade | quanto falta para chegar ao alvo |
| `excess` | excesso | o que pode sair da loja |
| `dc_allocated` | envio do CD / sugestão de pedido | depende de `execution_mode` |
| `transfer_in` / `transfer_out` | transferência de entrada / saída | entre lojas |
| `ExecutionMode.SHIP` / `ORDER_SUGGESTION` | envio / sugestão de pedido | loja própria / franquia |
| `ExceptionRule` | regra de exceção | classe plugável (OCP) |
| `AllocationException` | exceção | decisão que precisa de humano |
| `Severity` | crítica / alta / média / baixa | critical / high / medium / low |
| `Signal` | sinal | mensagem de loja ou franqueado, estruturada |
| `Policies` | políticas | limites definidos pelo planejador |
| `AuditEvent` | registro | evento append-only |
| shadow mode | modo sombra | recomenda e registra, não executa |
| `SignalInterpreter` | agente de sinais | LLM + validação de schema |
| `Copilot` | copiloto | LLM que explica |
