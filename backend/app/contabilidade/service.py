"""Saúde contábil — sinal derivado do dado (não auto-declarado).

Calcula faturamento dos últimos 12 meses (orçamentos aceitos + receitas
avulsas), compara com o teto do MEI e projeta quando o teto será atingido.
# FISCAL: teto e limiares são premissas; validar com contador.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Orcamento
from .models import Receita

# Limiar do gatilho de teto (parametrizável). # FISCAL: validar com contador.
LIMIAR_GATILHO_TETO = 0.75


@dataclass
class SaudeContabil:
    faturamento_12m: float
    teto_mei: float
    pct_teto: float
    restante: float
    media_mensal: float
    meses_ate_teto: Optional[float]
    projecao_estouro: Optional[date]
    gatilhos: list[str] = field(default_factory=list)
    fonte_orcamentos: float = 0.0
    fonte_avulsa: float = 0.0


def calcular_saude(db: Session, usuario_id: int, teto_mei: float) -> SaudeContabil:
    hoje = date.today()
    corte = hoje - timedelta(days=365)

    fat_orc = float(
        db.query(func.coalesce(func.sum(Orcamento.preco_final), 0))
        .filter(
            Orcamento.usuario_id == usuario_id,
            Orcamento.status == "aceito",
            func.coalesce(Orcamento.aceito_em, Orcamento.criado_em) >= corte,
        )
        .scalar() or 0
    )
    fat_avulso = float(
        db.query(func.coalesce(func.sum(Receita.valor), 0))
        .filter(Receita.usuario_id == usuario_id, Receita.data >= corte)
        .scalar() or 0
    )

    fat = round(fat_orc + fat_avulso, 2)
    pct = (fat / teto_mei) if teto_mei else 0.0
    restante = round(teto_mei - fat, 2)
    media = round(fat / 12, 2)
    meses = round(restante / media, 1) if media > 0 and restante > 0 else None
    projecao = (hoje + timedelta(days=int(meses * 30))) if meses else None

    gatilhos = []
    if pct >= LIMIAR_GATILHO_TETO:
        gatilhos.append("teto")

    return SaudeContabil(
        faturamento_12m=fat, teto_mei=teto_mei, pct_teto=round(pct, 4),
        restante=restante, media_mensal=media, meses_ate_teto=meses,
        projecao_estouro=projecao, gatilhos=gatilhos,
        fonte_orcamentos=round(fat_orc, 2), fonte_avulsa=round(fat_avulso, 2),
    )
