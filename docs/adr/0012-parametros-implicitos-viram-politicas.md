# 0012. Parâmetros implícitos do `regras.md` viram políticas com valor padrão

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** arquiteto de software, líder de planejamento
- **Relacionadas:** [0004](0004-motor-deterministico-llm-nao-calcula.md), [0005](0005-regras-de-excecao-plugaveis.md)

## Contexto

O `regras.md` §8.4 define a queda sazonal comparando "as últimas 3 semanas sobre as 3 anteriores", mas o `seed.policies` não traz esse 3. A mesma especificação diz que nenhum número de regra pode ficar fixo no código, e o `check_architecture.py` proíbe literais numéricos em `domain/rules/` (exceto 0, 1, -1, 2 e 100).

## Opções consideradas

1. **Criar a política `seasonal_window_weeks` em `Policies`, com padrão 3 quando o seed não informa** — prós: segue a regra "números vêm de Policies", aparece na aba Políticas, o golden não muda; contras: a política existe no código mas não no seed, então há um valor padrão fora do arquivo de dados.
2. **Constante de módulo fora de `domain/rules/`** — prós: simples; contras: esconde um parâmetro de negócio do planejador e contorna o espírito da verificação.
3. **Exigir o campo no seed** — prós: tudo explícito no dado; contras: muda o seed de referência do kit e quebra a compatibilidade com o oráculo.

## Decisão

Usaremos **a política `seasonal_window_weeks` (padrão 3)** em `Policies`, exibida em `/api/policies` como "Janela da queda sazonal". Futuros parâmetros implícitos seguem o mesmo caminho.

## Consequências

- **Positivas:** o planejador vê e, no futuro, ajusta a janela; o golden continua igual (padrão 3); a verificação estática passa sem exceções.
- **Negativas:** há um valor padrão no código que não está no seed; `/api/policies` mostra uma política a mais do que o `seed.policies`.
- **A monitorar:** novos parâmetros implícitos no `regras.md`; divergência entre o padrão do código e o que o seed vier a trazer.

## Conformidade

- `tests/unit/domain/test_model.py::test_policies_carregam_janela_sazonal_padrao_quando_omitida`.
- `tests/unit/domain/test_signals_and_catalog.py`: o catálogo de políticas cobre todos os campos de `Policies`.
- `check_architecture.py` sem literais em `domain/rules/`.
