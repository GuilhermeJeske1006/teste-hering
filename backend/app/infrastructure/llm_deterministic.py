"""Adaptador determinístico do LLM: sem rede, padrão quando não há `ANTHROPIC_API_KEY` (ADR 0006).

Ele lê só as mensagens recebidas, como um LLM faria, e responde por regras de palavra-chave:
- mensagens com `<mensagem>` viram o JSON do agente de sinais;
- conversas com `<contexto>` recebem uma resposta do copiloto montada a partir das exceções do contexto.
Nunca calcula números de alocação: só repete o que já está no texto.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass

from app.application.ports import Message

MESSAGE_RE = re.compile(r"<mensagem>\s*(.*?)\s*</mensagem>", re.S)
STORE_LINE_RE = re.compile(r"^- (\S+) \| (.+)$", re.M)
SKU_LINE_RE = re.compile(r"^- (\S+) \| (.+?) \| tamanhos: (.+)$", re.M)
HINT_RE = re.compile(r"Loja informada pelo usuário: (\S+)")
PCT_RE = re.compile(r"(\d{1,3}(?:[.,]\d+)?)\s*%")
EXCEPTION_RE = re.compile(
    r"^- \[(?P<id>[0-9a-f]+)\] (?P<sev>\S+) · (?P<status>\S+) · (?P<title>.+?) \| "
    r"Recomendação: (?P<rec>.+?) \| Fatos: (?P<facts>.*)$", re.M)

TYPE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("stock_mismatch", ("estoque", "zerado", "negativo", "sistema esta errado", "nao bate")),
    ("size_curve", ("tamanho", "so sai", "parado", "grade", "numeracao")),
    ("lost_sales", ("perd", "procurando", "falta", "acabou", "ruptura")),
    ("local_event", ("evento", "festa", "feira", "festival", "feriado", "show", "fenarreco", "oktoberfest",
                     "marejada")),
)
KNOWN_EVENTS = ("Oktoberfest", "Fenarreco", "Marejada", "Black Friday", "Natal", "Carnaval", "Páscoa",
                "Dia das Mães", "Dia dos Pais", "Dia dos Namorados")
PENDING_WORDS = ("depend", "decis", "pendente", "aberta", "fila", "prioridade", "primeiro", "urgente", "resumo",
                 "semana", "fazer")
SEVERITY_ORDER = {"crítica": 0, "alta": 1, "média": 2, "baixa": 3}
MAX_SENTENCES = 6
MIN_WORD = 4


def _norm(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", plain.lower())


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", _norm(text)) if len(w) >= MIN_WORD}


@dataclass(frozen=True, slots=True)
class _ContextException:
    id: str
    severity: str
    status: str
    title: str
    recommendation: str
    facts: str


class DeterministicLLMClient:
    """LLM de mentira, previsível e offline, para demonstração, CI e testes."""

    def complete(self, messages: Sequence[Message], *, max_tokens: int) -> str:
        if not messages:
            raise ValueError("a conversa precisa de pelo menos uma mensagem")
        system = "\n".join(m.content for m in messages if m.role == "system")
        signal_msg = next((m.content for m in messages if m.role == "user" and MESSAGE_RE.search(m.content)), None)
        if signal_msg is not None:
            return self._interpret(system, signal_msg)
        question = next((m.content for m in reversed(messages) if m.role == "user"), messages[-1].content)
        if "<contexto>" in system:
            return self._copilot(system, question)
        return "Estou no modo determinístico, sem LLM. Pergunte sobre as exceções da semana para eu ajudar."

    # ---------------- agente de sinais ----------------

    def _interpret(self, system: str, user: str) -> str:
        match = MESSAGE_RE.search(user)
        text = match.group(1) if match else user
        norm = _norm(text)
        hint = HINT_RE.search(user)
        store = hint.group(1) if hint else self._find_store(system, text)
        signal_type = next((t for t, words in TYPE_KEYWORDS if any(w in norm for w in words)), "other")
        event = next((e for e in KNOWN_EVENTS if _norm(e) in norm), None)
        adjustments = self._adjustments(system, text)
        confidence = min(0.95, 0.5 + (0.2 if store else 0) + (0.15 if signal_type != "other" else 0)
                         + (0.1 if adjustments else 0))
        reason = f"Interpretação por palavras-chave (modo sem LLM): tipo {signal_type}"
        reason += f", loja {store}." if store else ", loja não identificada."
        return json.dumps({"store": store, "type": signal_type, "event": event, "adjustments": adjustments,
                           "confidence": round(confidence, 2), "requires_human": False, "reason": reason},
                          ensure_ascii=False)

    @staticmethod
    def _find_store(system: str, text: str) -> str | None:
        norm = _norm(text)
        stores = STORE_LINE_RE.findall(system.split("Produtos válidos:")[0])
        for store_id, name in sorted(stores, key=lambda s: -len(s[1])):
            if _norm(name) in norm or re.search(rf"\b{re.escape(store_id)}\b", text):
                return str(store_id)
        return None

    @staticmethod
    def _adjustments(system: str, text: str) -> list[dict[str, object]]:
        pcts = [float(p.replace(",", ".")) for p in PCT_RE.findall(text)]
        if not pcts:
            return []
        norm, words = _norm(text), _words(text)
        best: tuple[int, str, list[str]] | None = None
        for sku_id, name, sizes in SKU_LINE_RE.findall(system):
            score = len(words & _words(name))
            if score >= 2 and (best is None or score > best[0]):
                best = (score, sku_id, [s.strip() for s in sizes.split(",")])
        scope = "all"
        if best and "tudo" not in norm:
            mentioned = [s for s in best[2] if re.search(rf"(?<![A-Za-z0-9]){re.escape(s)}(?![A-Za-z0-9])", text)]
            scope = f"{best[1]}:{mentioned[0]}" if len(mentioned) == 1 else best[1]
        return [{"scope": scope, "pct": pcts[0]}]

    # ---------------- copiloto ----------------

    def _copilot(self, system: str, question: str) -> str:
        exceptions = [_ContextException(m["id"], m["sev"], m["status"], m["title"], m["rec"], m["facts"])
                      for m in EXCEPTION_RE.finditer(system)]
        if not exceptions:
            return "Não encontrei exceções no contexto da mesa para responder."
        open_items = sorted((e for e in exceptions if e.status == "aberta"),
                            key=lambda e: SEVERITY_ORDER.get(e.severity, len(SEVERITY_ORDER)))
        q_words = _words(question)
        scored = sorted(((len(q_words & _words(f"{e.title} {e.recommendation} {e.facts}")), i, e)
                         for i, e in enumerate(exceptions)), key=lambda s: (-s[0], s[1]))
        if any(w in _norm(question) for w in PENDING_WORDS) or not scored or scored[0][0] == 0:
            return self._pending_answer(open_items, exceptions)
        best = scored[0][2]
        sentences = [
            f"Sobre [{best.id}] {best.title}: a recomendação é {best.recommendation[0].lower()}"
            f"{best.recommendation[1:]}.",
            f"Os números que sustentam isso: {best.facts}.",
            f"A exceção está {best.status} e tem severidade {best.severity}.",
            "A decisão é do planejador: o sistema está em modo sombra e não executa nada sozinho.",
        ]
        return " ".join(sentences[:MAX_SENTENCES])

    @staticmethod
    def _pending_answer(open_items: list[_ContextException], all_items: list[_ContextException]) -> str:
        if not open_items:
            return (f"Todas as {len(all_items)} exceções da semana já foram decididas. Nada depende de você agora; "
                    "o sistema segue em modo sombra e não executa nada.")
        first, rest = open_items[0], open_items[1:3]
        sentences = [
            f"Há {len(open_items)} exceções abertas que dependem de você.",
            f"A mais urgente é [{first.id}] {first.title} (severidade {first.severity}): "
            f"{first.recommendation[0].lower()}{first.recommendation[1:]}.",
        ]
        if rest:
            sentences.append("Na sequência vêm " + " e ".join(f"[{e.id}] {e.title}" for e in rest) + ".")
        sentences.append("A decisão é do planejador: o sistema está em modo sombra e não executa nada.")
        return " ".join(sentences[:MAX_SENTENCES])
