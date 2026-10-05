"""História: o FastAPI serve a API e o build do React no mesmo processo (ADR 0002)."""
from fastapi.testclient import TestClient


def test_raiz_serve_o_index_do_react_quando_abro_o_navegador(client: TestClient) -> None:
    """Dado o build do frontend, quando abro /, então recebo o index.html."""
    res = client.get("/")
    assert res.status_code == 200 and "Mesa de Alocação" in res.text


def test_rota_do_front_cai_no_index_quando_spa_navega(client: TestClient) -> None:
    """Dado uma rota do React, quando abro direto, então recebo o index.html (fallback de SPA)."""
    assert "id=root" in client.get("/plano/CB-PT").text


def test_assets_sao_servidos_quando_o_navegador_pede(client: TestClient) -> None:
    """Dado o build, quando peço um asset e um arquivo da raiz, então recebo o arquivo."""
    assert client.get("/assets/app.js").text == "console.log('ok')"
    assert client.get("/favicon.svg").status_code == 200


def test_rota_de_api_inexistente_da_404_em_json_quando_chamada(client: TestClient) -> None:
    """Dado uma rota /api que não existe, quando chamo, então recebo 404 no formato de erro."""
    res = client.get("/api/nao-existe")
    assert res.status_code == 404 and res.json()["error"]["code"] == "not_found"


def test_caminho_fora_do_build_nao_vaza_arquivos_quando_tenta_subir_diretorio(client: TestClient) -> None:
    """Dado uma tentativa de path traversal, quando peço, então recebo só o index.html."""
    res = client.get("/..%2F..%2Fpyproject.toml")
    assert "[project]" not in res.text
