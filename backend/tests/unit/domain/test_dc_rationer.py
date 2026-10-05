"""Rateio do CD por produto × tamanho (regras.md §5)."""
from app.domain.allocation import DcRationer
from tests.unit.factories import make_line


def _need(store: str, need: int):  # type: ignore[no-untyped-def]
    return make_line(store, stock=0, target=need, need=need)


def test_cada_linha_recebe_a_necessidade_quando_cd_cobre_o_total() -> None:
    lines = DcRationer().ration([_need("A", 3), _need("B", 4), make_line("C", stock=9)], available=100)
    assert [ln.dc_allocated for ln in lines] == [3, 4, 0]


def test_rateio_proporcional_com_piso_quando_cd_nao_cobre() -> None:
    lines = DcRationer().ration([_need("A", 10), _need("B", 10)], available=10)
    assert [ln.dc_allocated for ln in lines] == [5, 5]


def test_sobra_vai_para_maior_falta_e_desempata_pela_loja_quando_rateio_tem_resto() -> None:
    # piso: A=floor(5*7/12)=2, B=floor(4*7/12)=2, C=floor(3*7/12)=1 -> resto 2
    # faltas: A=3, B=2, C=2 -> A recebe 1; empate B/C -> B
    lines = DcRationer().ration([_need("C", 3), _need("A", 5), _need("B", 4)], available=7)
    by_store = {ln.store: ln.dc_allocated for ln in lines}
    assert by_store == {"A": 3, "B": 3, "C": 1}
    assert sum(by_store.values()) == 7


def test_nada_e_enviado_quando_cd_vazio() -> None:
    lines = DcRationer().ration([_need("A", 3)], available=0)
    assert lines[0].dc_allocated == 0
