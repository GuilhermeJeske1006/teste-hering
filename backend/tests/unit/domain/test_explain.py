"""Templates determinísticos de explicação (pt-BR)."""
from app.domain import explain
from app.domain.model import SignalAdjustment
from tests.unit.factories import make_signal, make_sku, make_store


def test_formata_inteiro_com_ponto_de_milhar_quando_maior_que_mil() -> None:
    assert explain.fmt_int(12345) == "12.345"


def test_formata_reais_no_padrao_brasileiro_quando_tem_centavos() -> None:
    assert explain.fmt_brl(1234.5) == "R$ 1.234,50"


def test_formata_decimal_com_virgula_quando_tem_fracao() -> None:
    assert explain.fmt_dec(8.44) == "8,4"


def test_formata_percentual_sem_casas_quando_inteiro() -> None:
    assert explain.fmt_pct(40.0) == "40%"
    assert explain.fmt_pct(12.5) == "12,5%"


def test_explicacao_de_lancamento_traz_total_e_lojas_quando_gerada() -> None:
    sku = make_sku("VM-FL", launch_week=41, similar=("A", "B", "C"), price=100.0)
    text = explain.launch_approval(sku, {"BC": 29, "JOI": 16, "GAS": 0}, approval_weeks=2)
    assert text.title.startswith("Lançamento VM-FL · ")
    assert "45 peças em 2 lojas" in text.recommendation
    assert "3 produtos parecidos" in text.explanation
    assert any("R$ 4.500,00" in f for f in text.facts)
    assert any("BC 29" in f for f in text.facts)


def test_explicacao_de_transferencia_lista_destinos_e_frete_quando_gerada() -> None:
    text = explain.stockout_transfer(make_sku(), "M", make_store("BRQ", name="Brusque"),
                                     [("JOI", 13), ("BNU-S", 8), ("BC", 1)], dc_available=50, total_need=72,
                                     source_cover=20.0, freight_brl=38.0, source_is_franchise=True)
    assert text.recommendation == "Transferir 22 peças de BRQ: 13 para JOI, 8 para BNU-S e 1 para BC"
    assert any("R$ 114,00" in f for f in text.facts)
    assert any("franquia" in f for f in text.facts)


def test_explicacao_de_sinal_cita_pedido_e_limite_quando_gerada() -> None:
    signal = make_signal(text="Precisamos de 40% a mais de tudo")
    text = explain.signal_divergence(signal, make_store(name="Blumenau Centro"), SignalAdjustment("all", 40), 20)
    assert "+40%" in text.title and "tudo" in text.title
    assert "20%" in text.recommendation


def test_explicacao_de_estoque_negativo_mostra_o_valor_quando_gerada() -> None:
    text = explain.negative_stock(make_sku("CV-BR"), "P", make_store("GAS", name="Gaspar"), stock=-3)
    assert "-3" in text.explanation
    assert text.title == "Estoque negativo: CV-BR P em Gaspar"
