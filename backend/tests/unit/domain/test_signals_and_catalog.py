from dataclasses import fields

from app.domain.model import Policies, SignalAdjustment, SignalType
from app.domain.policy_catalog import POLICY_CATALOG
from app.domain.signals import signal_requires_human
from tests.unit.factories import make_policies


def test_exige_humano_quando_algum_ajuste_passa_do_limite() -> None:
    adjs = (SignalAdjustment("all", 10), SignalAdjustment("CB-PT", 25))
    assert signal_requires_human(SignalType.LOCAL_EVENT, adjs, make_policies())


def test_exige_humano_quando_sinal_e_de_curva_de_tamanho() -> None:
    assert signal_requires_human(SignalType.SIZE_CURVE, (), make_policies())


def test_nao_exige_humano_quando_ajustes_dentro_do_limite() -> None:
    assert not signal_requires_human(SignalType.LOST_SALES, (SignalAdjustment("all", 20),), make_policies())


def test_catalogo_descreve_todas_as_politicas_quando_comparado_ao_modelo() -> None:
    assert len(POLICY_CATALOG) == len(fields(Policies))
    assert {m.key for m in POLICY_CATALOG} == {f.name for f in fields(Policies)}
