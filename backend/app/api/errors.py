"""Mapeamento de erros para HTTP. Único lugar que traduz exceções de domínio em status (skill backend)."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.application.errors import LlmUnavailable, SignalUnparseable
from app.domain.errors import (
    AlreadyDecided,
    DomainError,
    ExceptionNotFound,
    NotDecided,
    ReasonRequired,
    SkuNotFound,
)

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    ExceptionNotFound: 404,
    SkuNotFound: 404,
    AlreadyDecided: 409,
    NotDecided: 409,
    ReasonRequired: 422,
    SignalUnparseable: 422,
    LlmUnavailable: 503,
}
HTTP_CODES = {404: ("not_found", "Recurso não encontrado."), 405: ("method_not_allowed", "Método não permitido.")}


def error_body(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


def _status_for(exc: DomainError) -> int:
    return next((status for kind, status in STATUS_BY_ERROR.items() if isinstance(exc, kind)), 400)


async def _domain_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    return JSONResponse(error_body(exc.code, str(exc)), status_code=_status_for(exc))


async def _validation_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    first = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(p) for p in first.get("loc", ()) if p not in ("body", "query"))
    detail = f" Verifique o campo '{field}'." if field else ""
    return JSONResponse(error_body("validation_error", f"Dados inválidos.{detail}"), status_code=422)


async def _http_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code, message = HTTP_CODES.get(exc.status_code, ("http_error", "Não foi possível atender o pedido."))
    return JSONResponse(error_body(code, message), status_code=exc.status_code)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
