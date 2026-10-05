---
name: validar-fluxo
description: Valida as jornadas do planejador de ponta a ponta no monolito rodando (Playwright + API): resumo, aprovar, rejeitar com motivo, desfazer, plano por loja, agente de sinais, copiloto, resistência a prompt injection e uso no celular. Use depois de integrar backend e frontend e antes de entregar.
---

# Validação de fluxos (E2E)

## Como rodar

```bash
npm --prefix frontend run build      # o monolito serve o build
python .claude/skills/validar-fluxo/scripts/validate_flows.py --out reports/flows
```

O script sobe `uvicorn app.main:app` dentro de `backend/`, com `MESA_DB_PATH` apontando para um arquivo temporário, então o estado começa limpo a cada execução. Depois executa as jornadas abaixo e grava `reports/flows/flows.md`, com capturas das falhas.

| Fluxo | Jornada do planejador | Critério de aceite |
|---|---|---|
| f1 | Abre a mesa | modo sombra visível; 248 linhas; 7 exceções; a primeira é crítica |
| f2 | Aprova uma exceção | abertas: 7 → 6; status visível; item no Registro |
| f3 | Rejeita com motivo | abertas: 6 → 5; o motivo aparece no card e no `/api/audit-log` |
| f4 | Desfaz a rejeição | abertas volta para 6 |
| f5 | Consulta o plano da camiseta preta | 8 lojas; JOI = "envio"; BRQ = "sugestão de pedido" |
| f6 | Testa o agente de sinais | 4 sinais listados; a mensagem nova vira JSON com `type` |
| f7 | Pergunta ao copiloto | chega uma resposta nova, não vazia |
| f8 | Mensagem maliciosa | políticas e exceções abertas não mudam |
| f9 | Usa no celular (390px) | sem rolagem horizontal; a aba Plano abre |

## Quando um fluxo falha

1. Abra `reports/flows/<fluxo>.png` e leia o erro.
2. Decida onde está o problema:
   - **o contrato** (testid ou rota) diverge da skill `frontend-react` ou do `api.md`: corrija o **código**, nunca o script;
   - **a regra de negócio**: volte ao teste de feature do backend, crie primeiro um teste que reproduza a falha e só então corrija.
3. Rode de novo. Se o mesmo fluxo falhar 3 vezes seguidas, pare e reporte ao usuário com a captura.

## Extensão

Uma jornada nova é uma função `fN_nome(page, base)` com docstring descrevendo a jornada, adicionada em `FLOWS`. Para cada fluxo novo, acrescente uma linha na tabela acima.
