---
name: validar-layout
description: Valida o layout da Mesa de Alocação no navegador (Playwright) em 390, 768 e 1280 px, nos temas claro e escuro, checando rolagem horizontal, vazamento, contraste AA, alvos de toque, testids obrigatórios, erros de console e o grid de colunas, e depois revisa as capturas visualmente. Use depois de qualquer mudança no frontend e antes de entregar.
---

# Validação de layout

## Pré-requisitos

- O build do frontend existe (`npm --prefix frontend run build`).
- O monolito está rodando: `cd backend && uvicorn app.main:app --port 8000`.
- O Playwright está instalado (`pip install playwright && playwright install chromium`).

## 1. Checagem automática

```bash
python .claude/skills/validar-layout/scripts/validate_layout.py --url http://localhost:8000 --out reports/layout
```

O script exige que o contêiner principal tenha `data-layout="main"`, com grid de 2 colunas em telas ≥ 980px e 1 coluna abaixo disso. Ele também exige todos os testids do contrato da skill `frontend-react`.

## 2. Revisão visual (obrigatória; o script não substitui)

Abra **cada** captura em `reports/layout/*.png` com a ferramenta de leitura de imagem e verifique:

- [ ] A hierarquia está clara: título → KPIs → abas → fila. A exceção crítica é a primeira coisa que o olho encontra.
- [ ] A severidade é legível sem depender de cor (aparece o texto "Crítica", "Alta" etc.).
- [ ] Os números estão alinhados (tabular-nums) na tabela do plano e nos KPIs.
- [ ] O Copiloto não cobre o conteúdo; em 390px ele aparece depois do conteúdo.
- [ ] O tema escuro não tem texto apagado, borda sumida nem fundo branco perdido.
- [ ] Nenhum texto está cortado e nenhum botão está quebrado em duas linhas de forma estranha.
- [ ] O estado vazio e o de erro estão desenhados (force um erro com `?simulate=error` se o frontend suportar; senão, revise o componente).

## 3. Correção

- Corrija usando os tokens de `styles/tokens.css`, nunca com cor literal.
- Depois de corrigir, rode o script mais uma vez e olhe só as capturas afetadas. **No máximo 2 ciclos**; se ainda falhar, liste o que ficou pendente no relatório.

## Saída

Use `reports/layout/layout.md` e acrescente o checklist visual preenchido.
