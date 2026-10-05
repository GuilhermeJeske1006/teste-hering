# 0016. Respostas do copiloto em Markdown restrito, mostradas sem HTML

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** tech lead, designer de produto
- **Relacionadas:** [0006](0006-llmclient-como-port.md), [0010](0010-frontend-react-ts-vite.md), [0011](0011-seguranca-e-governanca-de-ia.md)

## Contexto

O copiloto respondia com um único parágrafo de até 6 frases, com os ids das exceções no meio do texto. Uma resposta como "o que depende de mim?" juntava a contagem, três exceções, as recomendações e o aviso de modo sombra num bloco só. Dava para ler, mas não para bater o olho: o planejador não via de cara a ordem de prioridade nem os números de cada exceção.

Restrições:

- O contrato `{answer, sources}` já é usado pela API, pelos testes de feature e pelos fluxos E2E.
- O texto vem do LLM, e o contexto inclui sinais de lojas e franqueados, então pode carregar marcação maliciosa (ADR 0011).
- O frontend não usa biblioteca de UI (ADR 0010).
- O cliente determinístico (ADR 0006) precisa produzir o mesmo formato que o LLM.

## Opções consideradas

1. **Manter o texto corrido.**
   - Prós: nada muda.
   - Contras: o problema de leitura continua.
2. **Markdown restrito no campo `answer` + renderizador próprio** (parágrafos, listas `- ` e `1. ` com detalhe recuado, `**negrito**` e `[id]`).
   - Prós: o contrato não muda de forma; LLMs escrevem esse formato com naturalidade; texto antigo ou sem marcação continua aparecendo como parágrafo; o renderizador cria só elementos conhecidos, então HTML vira texto.
   - Contras: o LLM pode fugir do formato (o que sobrar aparece como texto literal); temos um parser próprio para manter.
3. **JSON estruturado (`{resumo, itens[], decisao}`) validado por schema.**
   - Prós: a estrutura é garantida.
   - Contras: muda o contrato da API; o LLM pode errar o JSON, o que pede retentativa e aumenta a latência; respostas fora do molde (por exemplo "não sei") ficam forçadas.
4. **Biblioteca de Markdown (`react-markdown`).**
   - Prós: cobre o Markdown inteiro.
   - Contras: é uma dependência a mais; suporta links e, se mal configurada, HTML, o que abre caminho para phishing via prompt injection; contraria a ADR 0010.

## Decisão

Usaremos **Markdown restrito** no `answer` do copiloto:

- O prompt pede o formato: frase de abertura, lista numerada para prioridades, lista com `- ` para fatos, negrito só no essencial, nada de títulos, tabelas, links, código ou HTML, e uma frase final dizendo quem decide.
- O `DeterministicLLMClient` gera o mesmo formato.
- No frontend, `parseRichText` converte o texto numa árvore de dados e o `RichText` monta só `p`, `ol`, `ul`, `li`, `strong`, `br` e o selo de fonte. Nunca usa `dangerouslySetInnerHTML`.
- As mensagens do planejador continuam como texto simples.

## Consequências

- **Positivas:**
  - Prioridades numeradas, fatos em lista e fontes como selos que batem com a lista "Fontes".
  - O contrato da API não muda de forma.
  - HTML, imagens e links injetados aparecem como texto.
  - Ao chegar mensagem nova, a conversa rola até a última pergunta.
- **Negativas:**
  - Se o LLM fugir do formato, a resposta pode sair com marcação literal (`#`, `|`).
  - O parser é mais um código para manter.
  - As respostas do modo determinístico ficaram mais longas, com mais linhas.
- **A monitorar:**
  - Respostas do LLM real fora do formato, a revisar nos logs do piloto.
  - Se aparecer pedido por tabelas ou links, reavaliar com uma ADR nova. Links continuam proibidos enquanto o contexto tiver texto de terceiros.

## Conformidade

- `frontend/src/richText.test.ts` e `components/RichText.test.tsx`: estrutura do parser e HTML, imagem e link renderizados como texto.
- `tests/unit/application/test_ask_copilot.py`: o prompt contém as regras de formato.
- `tests/unit/infrastructure/test_llm_deterministic.py` e `tests/feature/test_copiloto.py`: o modo determinístico responde em blocos com lista numerada.
- Revisão de código: nenhum `dangerouslySetInnerHTML` em `frontend/src` (`grep -rn dangerouslySetInnerHTML frontend/src` não retorna nada).
