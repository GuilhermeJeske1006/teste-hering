import pytest

from app.application.use_cases.decide_exception import DecideException
from app.domain.errors import AlreadyDecided, ExceptionNotFound, NotDecided, ReasonRequired
from app.domain.model import DecisionAction, ExceptionStatus
from tests.unit.fakes import FakeAudit, FakeDecisions, FixedClock, plan_for
from tests.unit.scenario import small_week


@pytest.fixture
def setup():  # type: ignore[no-untyped-def]
    plan, decisions, audit = plan_for(small_week()), FakeDecisions(), FakeAudit()
    use_case = DecideException(plan, decisions, decisions, audit, FixedClock())
    return use_case, plan.current().exceptions[0], decisions, audit


def test_aprovar_muda_status_e_grava_auditoria_quando_excecao_aberta(setup) -> None:  # type: ignore[no-untyped-def]
    use_case, exc, decisions, audit = setup
    result = use_case.execute(exc.id, DecisionAction.APPROVE)
    assert result.status is ExceptionStatus.APPROVED
    assert decisions.get(exc.id) is not None
    [event] = audit.events
    assert (event.action, event.subject, event.exception_id) == ("approve", exc.title, exc.id)


def test_rejeitar_sem_motivo_falha_quando_reason_ausente(setup) -> None:  # type: ignore[no-untyped-def]
    use_case, exc, _, audit = setup
    with pytest.raises(ReasonRequired):
        use_case.execute(exc.id, DecisionAction.REJECT)
    assert audit.events == []


def test_rejeitar_com_motivo_fora_da_lista_falha_quando_reason_invalido(setup) -> None:  # type: ignore[no-untyped-def]
    use_case, exc, _, _ = setup
    with pytest.raises(ReasonRequired):
        use_case.execute(exc.id, DecisionAction.REJECT, reason="porque sim")


def test_rejeitar_com_motivo_grava_o_motivo_quando_valido(setup) -> None:  # type: ignore[no-untyped-def]
    use_case, exc, _, audit = setup
    result = use_case.execute(exc.id, DecisionAction.REJECT, reason="Restrição comercial com o franqueado")
    assert result.status is ExceptionStatus.REJECTED
    assert audit.events[0].detail == "Restrição comercial com o franqueado"


def test_decidir_de_novo_falha_quando_ja_decidida(setup) -> None:  # type: ignore[no-untyped-def]
    use_case, exc, _, _ = setup
    use_case.execute(exc.id, DecisionAction.APPROVE)
    with pytest.raises(AlreadyDecided):
        use_case.execute(exc.id, DecisionAction.REJECT, reason="Dado de entrada errado")


def test_desfazer_reabre_e_registra_quando_decidida(setup) -> None:  # type: ignore[no-untyped-def]
    use_case, exc, decisions, audit = setup
    use_case.execute(exc.id, DecisionAction.APPROVE)
    result = use_case.execute(exc.id, DecisionAction.UNDO)
    assert result.status is ExceptionStatus.OPEN and result.decision is None
    assert decisions.get(exc.id) is None
    assert [e.action for e in audit.events] == ["approve", "undo"]


def test_desfazer_falha_quando_nada_foi_decidido(setup) -> None:  # type: ignore[no-untyped-def]
    use_case, exc, _, _ = setup
    with pytest.raises(NotDecided):
        use_case.execute(exc.id, DecisionAction.UNDO)


def test_decidir_falha_quando_excecao_nao_existe(setup) -> None:  # type: ignore[no-untyped-def]
    use_case, _, _, _ = setup
    with pytest.raises(ExceptionNotFound):
        use_case.execute("nao-existe", DecisionAction.APPROVE)
