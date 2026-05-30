"""Testes do motor fiscal ZFM (Fase 1)."""
from datetime import date

import pytest

from app.distrib.fiscal.models import FiscalNCM, FiscalRegra


@pytest.fixture
def seed_fiscal(db_session):
    """Semeia NCMs e regras na transação do teste (flush, não commit)."""
    db_session.add_all([
        FiscalNCM(codigo="9018.32.19", descricao="Agulhas", elegivel_zfm=True, excluido_beneficio=False),
        FiscalNCM(codigo="0000.00.00", descricao="Excluído", elegivel_zfm=True, excluido_beneficio=True),
    ])
    db_session.add_all([
        FiscalRegra(
            regime="ICMS", operacao="entrada_zfm", origem="nacional", uf="AM",
            aliquota=0.18, aplica_desoneracao=True, base_legal="Convênio ICM 65/88",
            vigencia_inicio=date(1988, 3, 1), vigencia_fim=None,
        ),
        FiscalRegra(
            regime="IBS_CBS", operacao="entrada_zfm", origem="nacional", uf="AM",
            aliquota=0.0, aplica_desoneracao=True, base_legal="LC 214/2025",
            vigencia_inicio=date(2027, 1, 1), vigencia_fim=None,
        ),
    ])
    db_session.flush()


def test_fiscal_exige_auth(client):
    assert client.get("/api/fiscal/ncm").status_code in (401, 403)


def test_listar_ncm(client, auth_headers, seed_fiscal):
    r = client.get("/api/fiscal/ncm", headers=auth_headers)
    assert r.status_code == 200
    codigos = {n["codigo"] for n in r.json()}
    assert {"9018.32.19", "0000.00.00"} <= codigos


def test_simular_entrada_icms_desonera_18pct(client, auth_headers, seed_fiscal):
    r = client.post(
        "/api/fiscal/simular-entrada",
        json={"ncm": "9018.32.19", "valor": 1000, "origem": "nacional", "data_ref": "2026-05-30"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["elegivel"] is True
    assert b["regime"] == "ICMS"
    assert b["valor_desonerado"] == 180.0
    assert b["custo_liquido"] == 820.0


def test_simular_entrada_transicao_ibs_cbs(client, auth_headers, seed_fiscal):
    # Em 2027 a regra de vigência mais recente é IBS/CBS (0%)
    r = client.post(
        "/api/fiscal/simular-entrada",
        json={"ncm": "9018.32.19", "valor": 1000, "data_ref": "2027-06-01"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["regime"] == "IBS_CBS"
    assert b["valor_desonerado"] == 0.0
    assert b["custo_liquido"] == 1000.0


def test_simular_entrada_ncm_excluido(client, auth_headers, seed_fiscal):
    r = client.post(
        "/api/fiscal/simular-entrada",
        json={"ncm": "0000.00.00", "valor": 500},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["elegivel"] is False
    assert b["custo_liquido"] == 500.0


def test_simular_entrada_ncm_inexistente(client, auth_headers, seed_fiscal):
    r = client.post(
        "/api/fiscal/simular-entrada",
        json={"ncm": "9999.99.99", "valor": 100},
        headers=auth_headers,
    )
    assert r.status_code == 422
