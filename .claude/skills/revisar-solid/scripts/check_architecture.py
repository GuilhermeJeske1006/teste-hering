#!/usr/bin/env python3
"""Verificação estática das fronteiras hexagonais e de sinais de violação SOLID no backend.

Erros (fazem o script sair com código 1):
  - domain/ importando framework, I/O ou camadas externas;
  - application/ importando infrastructure/, api/ ou frameworks;
  - api/ importando infrastructure/ diretamente (deve usar container);
  - classes concretas de infrastructure instanciadas fora de container.py;
  - literal numérico de regra de negócio em domain/rules/ (os limites vêm de Policies).
Avisos:
  - classe com mais de 150 linhas ou mais de 10 métodos públicos (sinal de violar o S);
  - função com mais de 40 linhas;
  - if/elif encadeado sobre "rule"/"kind"/"type" no motor (sinal de violar o O).

Uso: python check_architecture.py [backend/app]
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

FORBIDDEN = {
    "domain": {"fastapi", "pydantic", "httpx", "sqlite3", "requests", "starlette", "uvicorn",
               "app.infrastructure", "app.api", "app.application", "app.container"},
    "application": {"fastapi", "httpx", "sqlite3", "requests", "starlette", "uvicorn",
                    "app.infrastructure", "app.api", "app.container"},
    "api": {"app.infrastructure", "sqlite3", "httpx"},
}
ALLOWED_NUMBERS = {0, 1, -1, 2, 100}


def imports(tree: ast.AST) -> list[tuple[str, int]]:
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out += [(a.name, n.lineno) for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module:
            mod = n.module if n.level == 0 else "app." + n.module
            out.append((mod, n.lineno))
    return out


def main(root: Path) -> int:
    errors: list[str] = []
    warns: list[str] = []
    infra_classes: set[str] = set()
    for f in (root / "infrastructure").rglob("*.py") if (root / "infrastructure").exists() else []:
        for n in ast.walk(ast.parse(f.read_text())):
            if isinstance(n, ast.ClassDef):
                infra_classes.add(n.name)
    for f in sorted(root.rglob("*.py")):
        rel = f.relative_to(root)
        layer = rel.parts[0] if len(rel.parts) > 1 else rel.stem
        tree = ast.parse(f.read_text(), filename=str(f))
        for mod, line in imports(tree):
            for bad in FORBIDDEN.get(layer, ()):
                if mod == bad or mod.startswith(bad + "."):
                    errors.append(f"{rel}:{line}: camada '{layer}' não pode importar '{mod}'")
        if layer != "infrastructure" and rel.name != "container.py":
            for n in ast.walk(tree):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in infra_classes:
                    errors.append(f"{rel}:{n.lineno}: '{n.func.id}' (infraestrutura) instanciado fora de container.py")
        if rel.parts[:2] == ("domain", "rules"):
            for n in ast.walk(tree):
                if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool) \
                        and n.value not in ALLOWED_NUMBERS:
                    errors.append(f"{rel}:{n.lineno}: literal numérico {n.value!r} em regra (use Policies)")
        for n in ast.walk(tree):
            if isinstance(n, ast.ClassDef):
                size = (n.end_lineno or n.lineno) - n.lineno
                pub = [b for b in n.body if isinstance(b, ast.FunctionDef) and not b.name.startswith("_")]
                if size > 150 or len(pub) > 10:
                    warns.append(f"{rel}:{n.lineno}: classe {n.name} grande ({size} linhas, {len(pub)} métodos públicos)")
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                size = (n.end_lineno or n.lineno) - n.lineno
                if size > 40:
                    warns.append(f"{rel}:{n.lineno}: função {n.name} com {size} linhas")
            if isinstance(n, ast.If) and layer in ("domain", "application"):
                chain, cur = 0, n
                while isinstance(cur, ast.If):
                    t = ast.dump(cur.test)
                    if any(k in t for k in ("'rule'", "'kind'", "'type'", "attr='rule'", "attr='kind'")):
                        chain += 1
                    cur = cur.orelse[0] if len(cur.orelse) == 1 and isinstance(cur.orelse[0], ast.If) else None
                if chain >= 3:
                    warns.append(f"{rel}:{n.lineno}: if/elif sobre tipo/regra ({chain} ramos): prefira polimorfismo")
    print("# Verificação de arquitetura\n")
    print(f"**Resultado:** {'APROVADO' if not errors else f'REPROVADO ({len(errors)} erro(s))'}\n")
    for e in errors:
        print(f"- ERRO {e}")
    for w in sorted(set(warns)):
        print(f"- aviso {w}")
    if not errors and not warns:
        print("- Nenhum problema encontrado.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "backend/app")))
