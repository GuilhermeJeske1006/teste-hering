# 0008. Persistência em SQLite via repositórios; seed em JSON para demonstração

- **Status:** Aceita
- **Data:** 2026-10-05
- **Decisores:** arquiteto de software, tech lead
- **Relacionadas:** [0003](0003-arquitetura-hexagonal-solid.md), [0011](0011-seguranca-e-governanca-de-ia.md)

## Contexto

O MVP precisa persistir apenas decisões humanas (status das exceções) e o registro de auditoria. Os dados de entrada (lojas, produtos, vendas, estoque) vêm do ERP no futuro; hoje vêm do `seed.json` da semana 41/2026. O deploy é um único processo e os testes E2E precisam de estado limpo a cada execução.

## Opções consideradas

1. **SQLite da stdlib atrás de repositórios (`DecisionReader`/`DecisionWriter`, `AuditLog`) e seed JSON lido por `SeedSource`** — prós: zero infraestrutura, arquivo por ambiente (`MESA_DB_PATH`), troca futura por Postgres só no adaptador; contras: concorrência de escrita limitada, sem migrações formais.
2. **Postgres desde o início** — prós: concorrência e operação de produção; contras: exige serviço extra para dev, CI e demo; desproporcional ao volume do MVP.
3. **Só memória** — prós: o mais simples; contras: perde decisões e auditoria ao reiniciar, inaceitável para trilha de auditoria.

## Decisão

Usaremos **SQLite via repositórios** (`MESA_DB_PATH`, padrão `backend/data/mesa.db`) para decisões e auditoria, e **`JsonSeedSource`** (`MESA_SEED_PATH`, padrão `backend/app/seed/seed.json`) como fonte dos dados de entrada. Os testes usam `InMemory*` e arquivos temporários.

## Consequências

- **Positivas:** sobe sem dependências; os mesmos testes de contrato rodam para `InMemory` e `Sqlite`; o plano é recalculado do seed a cada inicialização, então é sempre consistente.
- **Negativas:** sem migrações (o schema é criado no start); escrita concorrente serializada; o plano não é persistido, só as decisões.
- **A monitorar:** tamanho do arquivo de auditoria; necessidade de múltiplas instâncias (sinal para migrar para Postgres).

## Conformidade

- `tests/unit/contracts/test_repository_contract.py` parametrizado por `InMemory` e `Sqlite`.
- `check_architecture.py` proíbe `sqlite3` fora de `infrastructure/`.
