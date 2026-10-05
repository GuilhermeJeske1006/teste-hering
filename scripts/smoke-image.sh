#!/usr/bin/env bash
# Smoke test da imagem do monolito antes de publicar (ADR 0015).
# Sobe o contêiner e confere: HEALTHCHECK "healthy", /api/health, a SPA servida, o modo sombra,
# usuário não-root e nenhuma chave da Anthropic gravada na imagem.
# Uso: scripts/smoke-image.sh <imagem> [porta-local]
set -euo pipefail

image="${1:?uso: scripts/smoke-image.sh <imagem> [porta-local]}"
port="${2:-18000}"
base="http://127.0.0.1:$port"

ok() { printf '\033[1;32m✓ %s\033[0m\n' "$1"; }
fail() { printf '\033[1;31m✗ %s\033[0m\n' "$1" >&2; exit 1; }

if docker image inspect --format '{{json .Config.Env}}' "$image" | grep -q 'ANTHROPIC_API_KEY'; then
  fail "a imagem tem ANTHROPIC_API_KEY no ambiente; a chave só entra em tempo de execução"
fi
ok "nenhuma chave da Anthropic na imagem"

cid="$(docker run -d -p "127.0.0.1:$port:8000" "$image")"
cleanup() {
  status=$?
  if [ "$status" -ne 0 ]; then
    echo "--- logs do contêiner"
    docker logs "$cid" 2>&1 | tail -50 || true
  fi
  docker rm -f "$cid" >/dev/null 2>&1 || true
}
trap cleanup EXIT

health=""
for _ in $(seq 1 60); do
  health="$(docker inspect --format '{{.State.Health.Status}}' "$cid")"
  [ "$health" = "healthy" ] && break
  [ "$(docker inspect --format '{{.State.Running}}' "$cid")" = "true" ] || fail "o contêiner parou"
  sleep 1
done
[ "$health" = "healthy" ] || fail "HEALTHCHECK não ficou healthy em 60 s (status: $health)"
ok "HEALTHCHECK healthy"

curl -fsS "$base/api/health" | grep -q '"status":"ok"' || fail "/api/health não respondeu ok"
ok "/api/health"

curl -fsS "$base/" | grep -qi '<div id="root">' || fail "a SPA não foi servida em /"
ok "SPA servida em /"

curl -fsS "$base/api/summary" | grep -q '"shadow_mode":true' || fail "o resumo não está em modo sombra"
ok "modo sombra ativo"

[ "$(docker exec "$cid" id -u)" != "0" ] || fail "o processo roda como root"
ok "usuário não-root ($(docker exec "$cid" id -u))"
