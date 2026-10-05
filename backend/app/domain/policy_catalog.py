"""Rótulos, descrições e unidades das políticas, para a tela de Políticas (pt-BR)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PolicyMeta:
    """Metadados de exibição de uma política."""

    key: str
    label: str
    description: str
    unit: str


POLICY_CATALOG: tuple[PolicyMeta, ...] = (
    PolicyMeta("forecast_weights", "Pesos da média móvel",
               "Peso de cada uma das últimas semanas, da mais recente para a mais antiga.", "pesos"),
    PolicyMeta("horizon_weeks", "Horizonte de cobertura", "Semanas cobertas pela previsão e pelo alvo.", "semanas"),
    PolicyMeta("cover_factor", "Fator de cobertura", "Multiplica a previsão do horizonte para chegar ao alvo.", "×"),
    PolicyMeta("min_display_basic", "Exposição mínima de básicos", "Peças mínimas por tamanho em produtos básicos.",
               "peças"),
    PolicyMeta("min_display_other", "Exposição mínima dos demais", "Peças mínimas por tamanho nos demais produtos.",
               "peças"),
    PolicyMeta("excess_trigger_factor", "Gatilho de excesso",
               "Estoque acima da previsão do horizonte vezes este fator vira excesso.", "×"),
    PolicyMeta("excess_keep_factor", "Estoque mantido ao liberar excesso",
               "Ao liberar excesso, a loja fica com a previsão do horizonte vezes este fator.", "×"),
    PolicyMeta("auto_execution_max_value_brl", "Limite de execução automática",
               "Valor máximo de envio automático por loja própria na semana.", "R$"),
    PolicyMeta("launch_approval_weeks", "Janela de aprovação de lançamentos",
               "Semanas após o lançamento em que a grade precisa de aprovação.", "semanas"),
    PolicyMeta("stockout_alert_cover_weeks", "Alerta de ruptura",
               "Cobertura abaixo da qual a loja está em risco de ruptura.", "semanas"),
    PolicyMeta("transfer_min_source_cover_weeks", "Cobertura mínima da origem",
               "Uma loja só cede peças se a própria cobertura passar disso.", "semanas"),
    PolicyMeta("transfer_freight_brl", "Frete por transferência", "Custo estimado de cada transferência entre lojas.",
               "R$"),
    PolicyMeta("signal_max_auto_adjust_pct", "Ajuste automático máximo por sinal",
               "Acima disso, o ajuste pedido por uma loja exige decisão humana.", "%"),
    PolicyMeta("seasonal_decline_pct", "Queda que indica fim de estação",
               "Queda de vendas entre as janelas comparadas que dispara a regra sazonal.", "%"),
    PolicyMeta("seasonal_min_cover_weeks", "Cobertura na queda sazonal",
               "Cobertura mínima para considerar que há sobra de estoque.", "semanas"),
    PolicyMeta("seasonal_min_stores", "Lojas na queda sazonal", "Quantas lojas precisam cair ao mesmo tempo.",
               "lojas"),
    PolicyMeta("seasonal_window_weeks", "Janela da queda sazonal",
               "Semanas recentes comparadas com o mesmo número de semanas anteriores.", "semanas"),
    PolicyMeta("size_curve_deviation_pp", "Desvio da curva de tamanhos",
               "Diferença, em pontos percentuais, que conta como desvio de um tamanho.", "p.p."),
    PolicyMeta("size_curve_min_units", "Volume mínimo para avaliar a curva",
               "Peças vendidas na janela para a curva ser confiável.", "peças"),
    PolicyMeta("size_curve_min_sizes", "Tamanhos fora da curva", "Quantos tamanhos precisam desviar ao mesmo tempo.",
               "tamanhos"),
    PolicyMeta("size_curve_weeks", "Janela da curva de tamanhos", "Semanas de vendas usadas para medir a curva.",
               "semanas"),
    PolicyMeta("repeated_rejection_count", "Rejeições repetidas",
               "Rejeições da mesma loja e produto que pedem revisão da política.", "rejeições"),
)
