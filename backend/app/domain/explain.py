"""Templates determinísticos de título, recomendação, explicação e fatos das exceções (pt-BR).

Os números vêm sempre do motor. O LLM pode reescrever o texto de forma mais natural, mas nunca é a
fonte dos números. As regras só calculam; todo texto de exceção nasce aqui.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from app.domain.model import Signal, SignalAdjustment, Sku, Store

FACT_TEXT_PREVIEW = 90
"""Quantos caracteres da mensagem original aparecem nos fatos de um sinal."""


@dataclass(frozen=True, slots=True)
class Explanation:
    """Textos de uma exceção, prontos para a tela."""

    title: str
    recommendation: str
    explanation: str
    facts: tuple[str, ...]


def fmt_int(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def fmt_dec(value: float, places: int = 1) -> str:
    return f"{value:,.{places}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def fmt_brl(value: float) -> str:
    return f"R$ {fmt_dec(value, 2)}"


def fmt_pct(value: float) -> str:
    return f"{fmt_int(int(value))}%" if float(value).is_integer() else f"{fmt_dec(value)}%"


def _join(items: Sequence[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " e " + items[-1]


def _plural(n: int, singular: str, plural: str) -> str:
    return f"{fmt_int(n)} {singular if n == 1 else plural}"


def launch_approval(sku: Sku, need_by_store: Mapping[str, int], approval_weeks: int) -> Explanation:
    total = sum(need_by_store.values())
    stores = [s for s, n in need_by_store.items() if n > 0]
    breakdown = " · ".join(f"{s} {fmt_int(n)}" for s, n in need_by_store.items() if n > 0)
    return Explanation(
        title=f"Lançamento {sku.id} · {sku.name} precisa de aprovação",
        recommendation=f"Aprovar a grade inicial de {_plural(total, 'peça', 'peças')} em "
                       f"{_plural(len(stores), 'loja', 'lojas')}",
        explanation=(
            f"O lançamento {sku.name} entrou na semana {sku.launch_week} e está dentro da janela de "
            f"{_plural(approval_weeks, 'semana', 'semanas')} em que a alocação precisa de aval. A previsão vem "
            f"da média de {_plural(len(sku.similar_skus), 'produto parecido', 'produtos parecidos')}, então a "
            f"primeira grade só segue depois da sua aprovação."
        ),
        facts=(
            f"Lançamento na semana {sku.launch_week}",
            f"Grade inicial: {_plural(total, 'peça', 'peças')} ({fmt_brl(total * sku.price)})",
            f"Por loja: {breakdown}" if breakdown else "Nenhuma loja precisa de peças",
        ),
    )


def stockout_transfer(sku: Sku, size: str, source: Store, destinations: Sequence[tuple[str, int]], *,
                      dc_available: int, total_need: int, source_cover: float, freight_brl: float,
                      source_is_franchise: bool) -> Explanation:
    qty = sum(q for _, q in destinations)
    legs = _join([f"{q} para {d}" for d, q in destinations])
    count = len(destinations)
    facts = [
        f"Estoque no CD: {_plural(dc_available, 'peça', 'peças')}",
        f"Necessidade das lojas: {_plural(total_need, 'peça', 'peças')}",
        f"Cobertura da origem: {fmt_dec(source_cover)} semanas",
        f"Frete estimado: {fmt_brl(freight_brl * count)} ({count} × {fmt_brl(freight_brl)})",
    ]
    if source_is_franchise:
        facts.append("A origem é franquia: depende do aceite do franqueado")
    return Explanation(
        title=f"Transferir {sku.id} {size} de {source.name} para {_plural(count, 'loja', 'lojas')}",
        recommendation=f"Transferir {_plural(qty, 'peça', 'peças')} de {source.id}: {legs}",
        explanation=(
            f"O CD tem só {_plural(dc_available, 'peça', 'peças')} de {sku.name} {size} para uma necessidade de "
            f"{fmt_int(total_need)}. {source.name} tem {fmt_dec(source_cover)} semanas de cobertura e pode ceder "
            f"{fmt_int(qty)} sem risco, o que evita ruptura nas lojas de destino."
        ),
        facts=tuple(facts),
    )


def _scope_label(scope: str) -> str:
    return "tudo" if scope == "all" else scope.replace(":", " ")


def signal_divergence(signal: Signal, store: Store, adjustment: SignalAdjustment, max_pct: float) -> Explanation:
    preview = signal.text if len(signal.text) <= FACT_TEXT_PREVIEW else signal.text[:FACT_TEXT_PREVIEW] + "…"
    reason = f"por causa de {signal.event}" if signal.event else "por um fator local"
    return Explanation(
        title=f"Sinal de {store.name} pede +{fmt_pct(adjustment.pct)} em {_scope_label(adjustment.scope)}",
        recommendation=f"Decidir se aplica +{fmt_pct(adjustment.pct)}: o limite automático é {fmt_pct(max_pct)}",
        explanation=(
            f"{store.name} pediu {fmt_pct(adjustment.pct)} a mais em {_scope_label(adjustment.scope)} {reason}. "
            f"O pedido passa do limite de {fmt_pct(max_pct)} para ajuste automático, então não entrou na "
            f"previsão. Só você pode aplicar esse ajuste."
        ),
        facts=(
            f"Pedido: +{fmt_pct(adjustment.pct)}",
            f"Limite automático: {fmt_pct(max_pct)}",
            f"Confiança da interpretação: {fmt_pct(round(signal.confidence * 100))}",
            f"Mensagem: \"{preview}\"",
        ),
    )


def seasonal_decline(sku: Sku, hits: Sequence[tuple[str, float, float]], *, window_weeks: int,
                     min_decline_pct: float, min_cover_weeks: float) -> Explanation:
    avg_decline = sum(d for _, d, _ in hits) / len(hits)
    avg_cover = sum(c for _, _, c in hits) / len(hits)
    return Explanation(
        title=f"Queda sazonal em {sku.id} · {sku.name}",
        recommendation=f"Suspender a reposição de {sku.id} e avaliar remarcação em "
                       f"{_plural(len(hits), 'loja', 'lojas')}",
        explanation=(
            f"Em {_plural(len(hits), 'loja', 'lojas')}, as vendas das últimas {window_weeks} semanas caíram "
            f"{fmt_pct(min_decline_pct)} ou mais em relação às {window_weeks} anteriores, e o estoque cobre "
            f"{fmt_dec(min_cover_weeks)} semanas ou mais. É sinal de fim de estação: repor agora aumenta a sobra."
        ),
        facts=(
            f"Queda média: {fmt_pct(round(avg_decline))}",
            f"Cobertura média: {fmt_dec(avg_cover)} semanas",
            f"Lojas: {', '.join(s for s, _, _ in hits)}",
        ),
    )


def size_curve_deviation(sku: Sku, store: Store, deviations: Sequence[tuple[str, float, float]], *,
                         weeks: int, total_units: int, deviation_pp: float) -> Explanation:
    return Explanation(
        title=f"Curva de tamanhos fora do padrão: {sku.id} em {store.name}",
        recommendation=f"Ajustar a grade de {sku.id} em {store.id} para a curva real de vendas",
        explanation=(
            f"Nas últimas {weeks} semanas, {store.name} vendeu {_plural(total_units, 'peça', 'peças')} de "
            f"{sku.name}, e {_plural(len(deviations), 'tamanho desvia', 'tamanhos desviam')} "
            f"{fmt_dec(deviation_pp, 0)} pontos ou mais da curva padrão. Repor pela curva padrão deixa sobra "
            f"nos tamanhos que não giram."
        ),
        facts=tuple(f"{size}: {fmt_pct(round(real))} vendido × {fmt_pct(round(std))} padrão"
                    for size, real, std in deviations),
    )


def negative_stock(sku: Sku, size: str, store: Store, stock: int) -> Explanation:
    return Explanation(
        title=f"Estoque negativo: {sku.id} {size} em {store.name}",
        recommendation=f"Corrigir o estoque de {sku.id} {size} em {store.id} antes de alocar",
        explanation=(
            f"O sistema registra {stock} peças de {sku.name} {size} em {store.name}, o que é impossível. A linha "
            f"ficou bloqueada: o motor não adivinha estoque e não recomenda nada até o dado ser corrigido."
        ),
        facts=(f"Estoque informado: {stock}", "Linha bloqueada"),
    )


def repeated_rejection(sku: Sku, store: Store, rejections: int, weeks: Sequence[int],
                       reasons: Sequence[str]) -> Explanation:
    main_reason = max(set(reasons), key=reasons.count) if reasons else None
    facts = [f"Rejeições: {rejections}", f"Semanas: {', '.join(str(w) for w in weeks)}"]
    if main_reason:
        facts.append(f"Motivo mais citado: \"{main_reason}\"")
    return Explanation(
        title=f"Rejeições repetidas: {sku.id} em {store.name}",
        recommendation=f"Revisar a política de {sku.id} para {store.id}",
        explanation=(
            f"A recomendação de {sku.name} para {store.name} foi rejeitada {rejections} vezes nas últimas "
            f"semanas. Se o padrão continuar, vale ajustar a política dessa loja em vez de rejeitar toda semana."
        ),
        facts=tuple(facts),
    )


def auto_execution_limit(store: Store, value_brl: float, limit_brl: float) -> Explanation:
    return Explanation(
        title=f"Envio para {store.name} acima do limite automático",
        recommendation=f"Revisar e aprovar o envio de {fmt_brl(value_brl)} para {store.id}",
        explanation=(
            f"O envio da semana para {store.name} soma {fmt_brl(value_brl)}, acima do limite de "
            f"{fmt_brl(limit_brl)} para execução automática. Revise antes de liberar."
        ),
        facts=(f"Valor do envio: {fmt_brl(value_brl)}", f"Limite automático: {fmt_brl(limit_brl)}"),
    )
