"""Testes do ledger de estoque (estoque_movimentos)."""


def _criar_material(client, headers, estoque=50):
    r = client.post(
        "/api/materiais",
        json={"nome": "Agulha", "categoria": "Agulhas", "unidade": "un",
              "custo_unitario": 2, "estoque": estoque, "estoque_minimo": 5},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_movimento_no_cadastro(client, auth_headers):
    mid = _criar_material(client, auth_headers, estoque=50)
    movs = client.get("/api/estoque/movimentos", headers=auth_headers).json()
    entrada = [m for m in movs if m["material_id"] == mid and m["origem"] == "cadastro"]
    assert len(entrada) == 1
    assert entrada[0]["tipo"] == "entrada"
    assert entrada[0]["quantidade"] == 50.0
    assert entrada[0]["saldo_apos"] == 50.0


def test_consumo_ao_aceitar_orcamento(client, auth_headers):
    mid = _criar_material(client, auth_headers, estoque=50)
    o = client.post(
        "/api/precificacao/salvar",
        json={"titulo": "T", "itens": [{"material_id": mid, "quantidade": 10}],
              "horas": 0, "valor_hora": 0, "margem_pct": 0},
        headers=auth_headers,
    ).json()
    oid = o["id"]

    det = client.patch(f"/api/precificacao/orcamentos/{oid}/status",
                       json={"status": "aceito"}, headers=auth_headers).json()
    assert det["aceito_em"] is not None  # carimbo de quando foi consumido

    # estoque caiu para 40
    mat = next(m for m in client.get("/api/materiais", headers=auth_headers).json() if m["id"] == mid)
    assert mat["estoque"] == 40.0

    # saída de -10 vinculada ao orçamento
    movs = client.get(f"/api/estoque/movimentos?material_id={mid}", headers=auth_headers).json()
    saidas = [m for m in movs if m["tipo"] == "saida"]
    assert any(m["quantidade"] == -10.0 and m["origem"] == "orcamento" and m["orcamento_id"] == oid for m in saidas)


def test_devolucao_ao_reprovar(client, auth_headers):
    mid = _criar_material(client, auth_headers, estoque=50)
    o = client.post(
        "/api/precificacao/salvar",
        json={"titulo": "T", "itens": [{"material_id": mid, "quantidade": 10}],
              "horas": 0, "valor_hora": 0, "margem_pct": 0},
        headers=auth_headers,
    ).json()
    oid = o["id"]
    client.patch(f"/api/precificacao/orcamentos/{oid}/status", json={"status": "aceito"}, headers=auth_headers)
    client.patch(f"/api/precificacao/orcamentos/{oid}/status", json={"status": "reprovado"}, headers=auth_headers)

    mat = next(m for m in client.get("/api/materiais", headers=auth_headers).json() if m["id"] == mid)
    assert mat["estoque"] == 50.0  # devolvido

    resumo = client.get("/api/estoque/resumo", headers=auth_headers).json()
    linha = next(x for x in resumo if x["material_id"] == mid)
    assert linha["entradas"] == 60.0  # 50 cadastro + 10 devolução
    assert linha["saidas"] == 10.0    # consumo ao aceitar
