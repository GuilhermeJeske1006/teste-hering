---
name: revisar-solid
description: Revisa o código da Mesa de Alocação contra os princípios SOLID e as fronteiras da arquitetura hexagonal, com um script estático e um checklist manual. Use depois de implementar ou refatorar o backend ou o frontend, e antes de dar uma fase como concluída.
---

# Revisão SOLID e de arquitetura

## 1. Checagem automática (obrigatória)

```bash
python .claude/skills/revisar-solid/scripts/check_architecture.py backend/app
```

- **ERRO** bloqueia: corrija e rode de novo.
- **Aviso** exige uma de duas coisas: refatorar, ou justificar em uma linha no relatório final (por exemplo, "o `container.py` é grande porque é o composition root").

## 2. Checklist manual (leia o código e responda cada item com sim ou não, citando arquivo:linha)

**S (responsabilidade única)**
- [ ] Cada caso de uso tem um único método público, `execute`.
- [ ] Os routers só convertem schema ↔ caso de uso, sem regra de negócio.
- [ ] Os textos de explicação estão em `domain/explain.py`, não nas regras.

**O (aberto/fechado)**
- [ ] Para criar uma regra de exceção nova, basta um arquivo em `domain/rules/` e uma linha em `default_rules()`. Prove isso escrevendo um teste com uma regra fake injetada no motor.
- [ ] `ExceptionCard` (frontend) não tem `switch` por `rule`.

**L (substituição de Liskov)**
- [ ] A suíte de contrato do `LLMClient` roda para todos os adaptadores.
- [ ] A suíte de contrato dos repositórios roda para `InMemory` e `Sqlite`.

**I (segregação de interfaces)**
- [ ] Nenhum port tem mais de 3 métodos.
- [ ] Nenhum caso de uso recebe um port do qual usa menos da metade dos métodos.

**D (inversão de dependência)**
- [ ] Só `container.py` importa `app.infrastructure`.
- [ ] Os hooks do React recebem o client por contexto, e os testes injetam um client fake.

**Invariantes do domínio** (ver skill `dominio-alocacao`)
- [ ] Nenhum número de previsão ou alocação sai do LLM.
- [ ] Nada chama ERP ou WMS.
- [ ] `requires_human` é recalculado pelo código.

## 3. Saída

Escreva `reports/solid.md` com o resultado do script, o checklist preenchido e as refatorações feitas.
