"""Erros de domínio. São mapeados para HTTP só em `api/errors.py`."""
from __future__ import annotations


class DomainError(Exception):
    """Base dos erros de domínio; a mensagem é em pt-BR e voltada ao usuário."""

    code = "domain_error"


class ExceptionNotFound(DomainError):
    """A exceção pedida não existe no plano corrente."""

    code = "exception_not_found"


class AlreadyDecided(DomainError):
    """A exceção já foi aprovada ou rejeitada."""

    code = "already_decided"


class NotDecided(DomainError):
    """Não há decisão para desfazer."""

    code = "not_decided"


class ReasonRequired(DomainError):
    """Rejeitar exige um dos motivos aceitos."""

    code = "reason_required"


class SkuNotFound(DomainError):
    """O produto pedido não existe."""

    code = "sku_not_found"
