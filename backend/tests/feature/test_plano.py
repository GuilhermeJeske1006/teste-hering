"""História: como planejador, consulto o plano por loja de um produto."""
from fastapi.testclient import TestClient


def test_plano_mostra_envio_para_proprias_e_sugestao_para_franquias_quando_abro_cb_pt(client: TestClient) -> None:
    """Dado a camiseta preta, quando abro o plano, então lojas próprias recebem envio e franquias sugestão."""
    body = client.get("/api/plan", params={"sku": "CB-PT"}).json()
    assert body["sku"] == "CB-PT" and body["sizes"] == ["PP", "P", "M", "G", "GG"]
    modes = {r["store_id"]: r["execution_mode"] for r in body["rows"]}
    assert len(modes) == 8
    assert modes["JOI"] == "ship" and modes["BNU-S"] == "ship" and modes["BC"] == "ship"
    assert modes["BRQ"] == "order_suggestion" and modes["GAS"] == "order_suggestion"


def test_celula_traz_movimentos_do_motor_quando_ha_transferencia(client: TestClient) -> None:
    """Dado a ruptura de CB-PT M, quando abro o plano, então BRQ cede 22 e JOI recebe 13."""
    rows = {r["store_id"]: r for r in client.get("/api/plan", params={"sku": "CB-PT"}).json()["rows"]}
    brq_m = next(c for c in rows["BRQ"]["cells"] if c["size"] == "M")
    joi_m = next(c for c in rows["JOI"]["cells"] if c["size"] == "M")
    assert brq_m["transfer_out"] == 22 and joi_m["transfer_in"] == 13
    assert set(joi_m) == {"size", "stock", "forecast_horizon", "target", "dc_allocated", "transfer_in",
                          "transfer_out", "excess", "status"}
    assert rows["BRQ"]["total_movement"] < 0


def test_sku_inexistente_da_404_quando_peco_o_plano(client: TestClient) -> None:
    """Dado um produto que não existe, quando peço o plano, então recebo 404 sku_not_found."""
    res = client.get("/api/plan", params={"sku": "XX-00"})
    assert res.status_code == 404 and res.json()["error"]["code"] == "sku_not_found"
    assert res.json()["error"]["message"]


def test_catalogo_lista_produtos_e_lojas_quando_consulto(client: TestClient) -> None:
    """Dado o seed, quando listo produtos e lojas, então vejo 6 produtos e 8 lojas com modo de execução."""
    skus = client.get("/api/skus").json()
    assert len(skus) == 6
    vm = next(s for s in skus if s["id"] == "VM-FL")
    assert vm["is_launch"] is True and vm["sizes"] == ["PP", "P", "M", "G", "GG"]
    stores = client.get("/api/stores").json()
    assert len(stores) == 8
    assert {"id": "JOI", "name": "Joinville Garten", "ownership": "own", "execution_mode": "ship"} in stores


def test_politicas_tem_rotulo_e_unidade_quando_consulto(client: TestClient) -> None:
    """Dado as políticas do seed, quando listo, então cada uma tem chave, rótulo, descrição, valor e unidade."""
    policies = {p["key"]: p for p in client.get("/api/policies").json()}
    assert policies["signal_max_auto_adjust_pct"]["value"] == 20
    assert policies["auto_execution_max_value_brl"]["unit"] == "R$"
    assert all(p["label"] and p["description"] for p in policies.values())
