"""Testes do Contabilidade Connect — slice 1 (saúde + receita avulsa + sinalização)."""
from datetime import date


def test_saude_vazia(client, auth_headers):
    r = client.get("/api/contabilidade/saude", headers=auth_headers)
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["faturamento_12m"] == 0.0
    assert b["teto_mei"] == 81000.0
    assert b["sinalizacao_status"] == "sem_sinalizacao"
    assert b["gatilhos"] == []


def test_receita_avulsa_entra_na_saude(client, auth_headers):
    r = client.post(
        "/api/contabilidade/receitas",
        json={"descricao": "Trabalho no dinheiro", "valor": 5000, "data": date.today().isoformat()},
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text

    saude = client.get("/api/contabilidade/saude", headers=auth_headers).json()
    assert saude["faturamento_12m"] == 5000.0
    assert saude["fonte_avulsa"] == 5000.0


def test_orcamento_aceito_entra_na_saude(client, auth_headers):
    # cria material e orçamento, aceita -> entra no faturamento 12m
    mid = client.post("/api/materiais", json={"nome": "X", "estoque": 100}, headers=auth_headers).json()["id"]
    o = client.post(
        "/api/precificacao/salvar",
        json={"titulo": "Job", "itens": [{"material_id": mid, "quantidade": 1}], "horas": 10, "valor_hora": 100, "margem_pct": 0},
        headers=auth_headers,
    ).json()
    client.patch(f"/api/precificacao/orcamentos/{o['id']}/status", json={"status": "aceito"}, headers=auth_headers)

    saude = client.get("/api/contabilidade/saude", headers=auth_headers).json()
    assert saude["fonte_orcamentos"] > 0
    assert saude["faturamento_12m"] == saude["fonte_orcamentos"] + saude["fonte_avulsa"]


def test_gatilho_teto_dispara(client, auth_headers):
    # 75% de 81000 = 60750
    client.post("/api/contabilidade/receitas",
                json={"descricao": "Faturamento alto", "valor": 65000, "data": date.today().isoformat()},
                headers=auth_headers)
    saude = client.get("/api/contabilidade/saude", headers=auth_headers).json()
    assert "teto" in saude["gatilhos"]
    assert saude["pct_teto"] >= 0.75


def test_sinalizar_contador(client, auth_headers):
    r = client.post("/api/contabilidade/sinalizar", json={"origem": "manual", "gatilho": "manual"}, headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["status"] == "procurando"
    # idempotente: segunda chamada não duplica
    r2 = client.post("/api/contabilidade/sinalizar", json={"origem": "manual", "gatilho": "manual"}, headers=auth_headers)
    assert r2.json()["id"] == r.json()["id"]

    saude = client.get("/api/contabilidade/saude", headers=auth_headers).json()
    assert saude["sinalizacao_status"] == "procurando"
