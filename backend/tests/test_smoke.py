"""Smoke tests da PoC — cobertura mínima do que já existe (Fase 0)."""


def test_root_health(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "empresa" in body


def test_config_publica(client):
    r = client.get("/api/config")
    assert r.status_code == 200
    assert "empresa_nome" in r.json()


def test_fluxo_auth(client):
    # pré-registro
    r = client.post(
        "/api/auth/pre-registro",
        json={"email": "ana@studio.dev", "senha": "segredo1", "nome": "Ana"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "pre_registro"

    # e-mail duplicado
    r2 = client.post(
        "/api/auth/pre-registro",
        json={"email": "ana@studio.dev", "senha": "segredo1", "nome": "Ana"},
    )
    assert r2.status_code == 409

    # login + me
    r3 = client.post("/api/auth/login", json={"email": "ana@studio.dev", "senha": "segredo1"})
    assert r3.status_code == 200
    token = r3.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ana@studio.dev"


def test_login_senha_errada(client):
    client.post(
        "/api/auth/pre-registro",
        json={"email": "bob@studio.dev", "senha": "certa123", "nome": "Bob"},
    )
    r = client.post("/api/auth/login", json={"email": "bob@studio.dev", "senha": "errada"})
    assert r.status_code == 401


def test_materiais_exige_auth(client):
    r = client.get("/api/materiais")
    assert r.status_code in (401, 403)


def test_materiais_crud(client, auth_headers):
    # cria
    novo = {"nome": "Agulha 1203RL", "categoria": "agulhas", "unidade": "un",
            "custo_unitario": 2.5, "estoque": 100}
    r = client.post("/api/materiais", json=novo, headers=auth_headers)
    assert r.status_code == 201, r.text
    mat_id = r.json()["id"]

    # lista
    r = client.get("/api/materiais", headers=auth_headers)
    assert r.status_code == 200
    assert any(m["id"] == mat_id for m in r.json())

    # atualiza
    novo["custo_unitario"] = 3.0
    r = client.put(f"/api/materiais/{mat_id}", json=novo, headers=auth_headers)
    assert r.status_code == 200
    assert float(r.json()["custo_unitario"]) == 3.0

    # remove
    r = client.delete(f"/api/materiais/{mat_id}", headers=auth_headers)
    assert r.status_code == 204
