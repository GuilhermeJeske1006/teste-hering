# 0006. `LLMClient` como port, com adaptador Anthropic e adaptador determinístico

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** arquiteto de software, tech lead
- **Relacionadas:** [0003](0003-arquitetura-hexagonal-solid.md), [0004](0004-motor-deterministico-llm-nao-calcula.md), [0011](0011-seguranca-e-governanca-de-ia.md)

## Contexto

O agente de sinais e o copiloto usam LLM, mas o sistema precisa rodar sem chave (demonstração, CI, testes) e os testes não podem depender de rede. O provedor pode mudar, e o SDK oficial traria dependência e versão a mais para duas chamadas simples. A chamada real precisa de timeout e de tratamento de indisponibilidade.

## Opções consideradas

1. **Port `LLMClient.complete(messages, *, max_tokens) -> str` com dois adaptadores: `AnthropicLLMClient` (httpx, timeout de 30 s, uma nova tentativa) e `DeterministicLLMClient` (sem rede, padrão sem chave)** — prós: testes determinísticos, troca de provedor sem tocar casos de uso, demo funciona offline; contras: o adaptador determinístico é uma heurística e não representa a qualidade real do LLM.
2. **SDK oficial `anthropic` direto nos casos de uso** — prós: menos código próprio, recursos do SDK; contras: acopla a aplicação a um provedor, testes exigem mock do SDK, dependência obrigatória mesmo sem chave.
3. **Framework de orquestração (LangChain ou similar)** — prós: abstrações prontas; contras: dependência grande, abstrações demais para duas chamadas, mais superfície de ataque.

## Decisão

Usaremos **`LLMClient` como port** com interface mínima (`complete`). `container.py` escolhe `AnthropicLLMClient` quando existe `ANTHROPIC_API_KEY` (modelo em `ANTHROPIC_MODEL`, padrão `claude-haiku-4-5`) e `DeterministicLLMClient` caso contrário. Falha do provedor vira `LlmUnavailable`, mapeada para HTTP 503.

## Consequências

- **Positivas:** a suíte inteira roda offline; `/api/health` informa o cliente ativo; a mesma suíte de contrato valida todos os adaptadores (Liskov).
- **Negativas:** o comportamento do LLM real só é exercitado em um teste marcado `@pytest.mark.llm`, fora do padrão; mantemos código HTTP próprio em vez do SDK.
- **A monitorar:** taxa de 503 e latência do adaptador real; mudanças na API de mensagens da Anthropic.

## Conformidade

- `tests/unit/contracts/test_llm_client_contract.py` parametrizado por todos os adaptadores (o Anthropic com transporte httpx falso).
- `check_architecture.py`: só `container.py` instancia adaptadores.
