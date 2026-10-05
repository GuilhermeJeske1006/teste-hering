#!/usr/bin/env bash
# Roda todas as etapas de qualidade e grava reports/tests.md. Não aborta na primeira falha.
set -u
ROOT="$(pwd)"
mkdir -p reports
REPORT="$ROOT/reports/tests.md"
FAILED=0
declare -a ROWS

step() {
  local name="$1"; shift
  local log="$ROOT/reports/test-$name.log"
  local t0=$(date +%s)
  if (cd "$ROOT" && "$@") >"$log" 2>&1; then
    ROWS+=("| $name | ok | $(( $(date +%s) - t0 ))s | |")
  else
    FAILED=1
    local first
    first=$(grep -m1 -E "FAILED|Error|error|✗|×|FAIL" "$log" | head -c 180 | tr '|' '/')
    ROWS+=("| $name | **falhou** | $(( $(date +%s) - t0 ))s | ${first:-ver reports/test-$name.log} |")
  fi
  echo "[$name] concluído"
}

PY="${PYTHON:-python}"
step lint-py    $PY -m ruff check backend
step types-py   $PY -m mypy --strict backend/app/domain backend/app/application
step unit-py    bash -c "cd backend && $PY -m pytest tests/unit -q --cov=app.domain --cov=app.application --cov-report=term-missing --cov-fail-under=90"
step feature-py bash -c "cd backend && $PY -m pytest tests/feature -q --cov=app --cov-report=term-missing --cov-fail-under=80"
step unit-js    npm --prefix frontend run test -- --run --coverage
step lint-js    npm --prefix frontend run lint
step build-js   npm --prefix frontend run build

{
  echo "# Relatório de testes"
  echo
  if [ $FAILED -eq 0 ]; then echo "**Resultado:** APROVADO"; else echo "**Resultado:** REPROVADO"; fi
  echo
  echo "| Etapa | Status | Tempo | Primeira falha |"
  echo "|---|---|---|---|"
  printf '%s\n' "${ROWS[@]}"
  echo
  echo "Logs completos: \`reports/test-<etapa>.log\`"
} > "$REPORT"
cat "$REPORT"
exit $FAILED
