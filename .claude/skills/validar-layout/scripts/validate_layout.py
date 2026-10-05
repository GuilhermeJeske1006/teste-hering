#!/usr/bin/env python3
"""Validação automática de layout da Mesa de Alocação com Playwright.

Para cada viewport (390, 768 e 1280 px) e cada tema (claro e escuro), o script verifica:
  1. ausência de rolagem horizontal no documento;
  2. elementos visíveis vazando a largura da tela (exceto dentro de contêineres com overflow-x);
  3. presença e visibilidade dos data-testid obrigatórios;
  4. contraste mínimo de texto (WCAG AA 4.5:1; 3:1 para texto >= 18,66 px bold ou 24 px);
  5. alvos de toque >= 32x32 px em telas <= 768 px;
  6. erros de console e requisições com falha da própria origem (fontes de terceiros são ignoradas);
  7. o grid de duas colunas em >= 980 px e uma coluna abaixo disso.

Gera capturas e relatório em <out>/ e sai com código 1 se houver falhas.

Uso:
  python validate_layout.py --url http://localhost:8000 [--out reports/layout] [--skip-testids]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORTS = [(390, 844), (768, 1024), (1280, 800)]
SCHEMES = ["light", "dark"]
REQUIRED_TESTIDS = [
    "kpi-total", "kpi-within-policy", "kpi-open-exceptions", "shadow-mode-tag",
    "tab-exceptions", "tab-plan", "tab-signals", "tab-policies", "tab-audit",
    "exception-card", "copilot-input", "btn-ask",
]

JS_CHECKS = r"""
() => {
  const vw = document.documentElement.clientWidth;
  const res = {docOverflow: document.documentElement.scrollWidth - vw, overflowing: [], contrast: [], smallTargets: []};
  const inScroller = el => { for (let p = el.parentElement; p; p = p.parentElement) {
      const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll' || o === 'hidden') return true; } return false; };
  const visible = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && cs.opacity !== '0'; };
  const label = el => (el.dataset.testid ? `[data-testid=${el.dataset.testid}]` : el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : ''));
  for (const el of document.body.querySelectorAll('*')) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.right > vw + 1 && !inScroller(el)) res.overflowing.push({el: label(el), right: Math.round(r.right), vw});
  }
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return {r:p[0], g:p[1], b:p[2], a: p.length > 3 ? p[3] : 1}; };
  const lum = ({r,g,b}) => { const f = v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); }; return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b); };
  const bgOf = el => { for (let p = el; p; p = p.parentElement) { const c = parse(getComputedStyle(p).backgroundColor); if (c && c.a > 0.5) return c; } return {r:255,g:255,b:255,a:1}; };
  const textEls = [...document.body.querySelectorAll('*')].filter(el => visible(el) && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1));
  for (const el of textEls.slice(0, 600)) {
    const cs = getComputedStyle(el); const fg = parse(cs.color); if (!fg) continue; const bg = bgOf(el);
    const L1 = lum(fg), L2 = lum(bg); const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700;
    const min = (size >= 24 || (bold && size >= 18.66)) ? 3 : 4.5;
    if (ratio < min) res.contrast.push({el: label(el), text: el.textContent.trim().slice(0, 40), ratio: Math.round(ratio*100)/100, min});
  }
  if (vw <= 768) for (const el of document.querySelectorAll('button, a[href], select, input, textarea, [role=tab]')) {
    if (!visible(el)) continue; const r = el.getBoundingClientRect();
    if (r.width < 32 || r.height < 32) res.smallTargets.push({el: label(el), w: Math.round(r.width), h: Math.round(r.height)});
  }
  const main = document.querySelector('[data-layout=main]');
  res.columns = main ? getComputedStyle(main).gridTemplateColumns.split(' ').filter(Boolean).length : null;
  return res;
}
"""


def run(url: str, out: Path, skip_testids: bool) -> int:
    out.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    report: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for (w, h) in VIEWPORTS:
            for scheme in SCHEMES:
                ctx = browser.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
                page = ctx.new_page()
                console_errors: list[str] = []
                failed_requests: list[str] = []
                origin = "/".join(url.split("/")[:3])
                same = lambda u: u.startswith(origin) or u.startswith("/")
                page.on("console", lambda m: console_errors.append(m.text)
                        if m.type == "error" and same((m.location or {}).get("url", origin)) else None)
                page.on("requestfailed", lambda r: failed_requests.append(r.url) if same(r.url) else None)
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(400)
                tag = f"{w}px-{scheme}"
                page.screenshot(path=str(out / f"{tag}.png"), full_page=True)
                r = page.evaluate(JS_CHECKS)
                r["viewport"], r["scheme"] = tag, scheme
                r["console_errors"], r["failed_requests"] = console_errors, failed_requests
                missing = []
                if not skip_testids:
                    for tid in REQUIRED_TESTIDS:
                        loc = page.locator(f"[data-testid={tid}]").first
                        if loc.count() == 0 or not loc.is_visible():
                            missing.append(tid)
                r["missing_testids"] = missing
                if r["docOverflow"] > 1:
                    failures.append(f"{tag}: rolagem horizontal de {r['docOverflow']}px")
                for o in r["overflowing"][:5]:
                    failures.append(f"{tag}: {o['el']} vaza a tela (right={o['right']} > {o['vw']})")
                for c in r["contrast"][:5]:
                    failures.append(f"{tag}: contraste {c['ratio']} < {c['min']} em {c['el']} \"{c['text']}\"")
                for s in r["smallTargets"][:5]:
                    failures.append(f"{tag}: alvo de toque pequeno {s['el']} ({s['w']}x{s['h']})")
                for m in missing:
                    failures.append(f"{tag}: data-testid ausente ou invisível: {m}")
                for e in console_errors[:3]:
                    failures.append(f"{tag}: erro de console: {e[:160]}")
                for fr in failed_requests[:3]:
                    failures.append(f"{tag}: requisição falhou: {fr}")
                if r["columns"] is not None:
                    expected = 2 if w >= 980 else 1
                    if r["columns"] != expected:
                        failures.append(f"{tag}: layout com {r['columns']} coluna(s); esperado {expected}")
                elif not skip_testids:
                    failures.append(f"{tag}: elemento [data-layout=main] não encontrado")
                report.append(r)
                ctx.close()
        browser.close()
    (out / "layout.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    md = ["# Relatório de layout", "", f"URL: {url}", "",
          f"**Resultado:** {'APROVADO' if not failures else f'REPROVADO ({len(failures)} problema(s))'}", ""]
    md += [f"- {f}" for f in failures] or ["- Nenhum problema encontrado."]
    md += ["", "Capturas: " + ", ".join(f"`{r['viewport']}.png`" for r in report)]
    (out / "layout.md").write_text("\n".join(md))
    print("\n".join(md))
    return 1 if failures else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--out", default="reports/layout")
    ap.add_argument("--skip-testids", action="store_true", help="só checagens genéricas (smoke)")
    a = ap.parse_args()
    sys.exit(run(a.url, Path(a.out), a.skip_testids))
