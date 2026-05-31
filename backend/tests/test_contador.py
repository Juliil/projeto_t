"""Testes do portal do contador e do fluxo de matchmaking (v1.1 slice 2)."""


def _registra(client, email, tipo="estudio", crc=None):
    body = {"email": email, "senha": "senha123", "nome": "Fulano", "tipo": tipo}
    if crc:
        body["crc"] = crc
        body["uf_crc"] = "AM"
    r = client.post("/api/auth/pre-registro", json=body)
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}, r.json()


def test_cadastro_contador_crc_simulado(client):
    h, tok = _registra(client, "cont@x.dev", tipo="contador", crc="AM-012345/O")
    assert tok["tipo"] == "contador"
    assert tok["status"] == "ativo"  # contador não passa pelo onboarding
    me = client.get("/api/contador/me", headers=h).json()
    assert me["status_crc"] == "ativo"  # validação simulada
    assert me["crc"] == "AM-012345/O"


def test_contador_sem_crc_falha(client):
    r = client.post("/api/auth/pre-registro",
                    json={"email": "c2@x.dev", "senha": "x", "nome": "C", "tipo": "contador"})
    assert r.status_code == 400


def test_estudio_nao_acessa_portal_contador(client, auth_headers):
    assert client.get("/api/contador/leads", headers=auth_headers).status_code == 403


def test_fluxo_matchmaking_completo(client, auth_headers):
    # estúdio sinaliza necessidade
    client.post("/api/contabilidade/sinalizar", json={}, headers=auth_headers)

    # contador entra e vê o lead anonimizado
    hc, _ = _registra(client, "cont3@x.dev", tipo="contador", crc="AM-1/O")
    leads = client.get("/api/contador/leads", headers=hc).json()
    assert len(leads) >= 1
    lead = leads[0]
    assert "faixa_faturamento" in lead and "regiao" in lead
    assert "nome" not in lead and "email" not in lead  # anonimizado
    sid = lead["sinalizacao_id"]

    # manifesta interesse
    r = client.post(f"/api/contador/leads/{sid}/interesse", json={"mensagem": "Posso ajudar na virada ME"}, headers=hc)
    assert r.status_code == 201

    # estúdio vê o interesse com a mensagem inicial
    inter = client.get("/api/contabilidade/interesses", headers=auth_headers).json()
    assert len(inter) == 1
    assert inter[0]["mensagem_inicial"] == "Posso ajudar na virada ME"
    mid = inter[0]["id"]

    # estúdio aceita liberando escopo granular (sem regime_fiscal)
    v = client.post(f"/api/contabilidade/interesses/{mid}/aceitar",
                    json={"escopo": ["faturamento", "estoque"]}, headers=auth_headers).json()
    assert v["escopo_dados"] == ["faturamento", "estoque"]

    # contador vê o vínculo e o pacote de dados CONSENTIDO
    vincs = client.get("/api/contador/vinculos", headers=hc).json()
    assert len(vincs) == 1
    vid = vincs[0]["id"]
    pacote = client.get(f"/api/contador/vinculos/{vid}/dados", headers=hc).json()
    assert "faturamento" in pacote["dados"]
    assert "estoque" in pacote["dados"]
    assert "regime_fiscal" not in pacote["dados"]  # não consentido → não vaza

    # chat com contexto: contador escreve, estúdio lê
    client.post(f"/api/contador/vinculos/{vid}/mensagens", json={"corpo": "Olá, vamos começar?"}, headers=hc)
    msgs = client.get("/api/contabilidade/vinculo/mensagens", headers=auth_headers).json()
    assert any(m["autor"] == "contador" and m["corpo"] == "Olá, vamos começar?" for m in msgs)
