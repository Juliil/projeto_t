"""Modelos do motor fiscal ZFM.

As alíquotas e enquadramentos são PARÂMETROS (linhas em banco), versionados
por vigência — nunca lógica fixa. Tudo aqui é premissa de modelagem.
# FISCAL: validar com contador antes de produção.
"""
from sqlalchemy import (
    BigInteger, Boolean, Column, Date, Numeric, Text, TIMESTAMP, func,
)

from ...db import Base


class FiscalNCM(Base):
    """Cadastro de NCM com flags de elegibilidade ao benefício ZFM."""
    __tablename__ = "fiscal_ncm"

    id = Column(BigInteger, primary_key=True)
    codigo = Column(Text, nullable=False, unique=True)        # ex.: "9018.32.19"
    descricao = Column(Text, nullable=False)
    elegivel_zfm = Column(Boolean, nullable=False, default=True)
    excluido_beneficio = Column(Boolean, nullable=False, default=False)  # exceções explícitas
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())


class FiscalRegra(Base):
    """Regra tributária versionada por vigência.

    Uma operação (ex.: entrada na ZFM) pode ter regras coexistindo em regimes
    diferentes (ICMS x IBS/CBS); o engine resolve pela data e/ou regime pedido.
    """
    __tablename__ = "fiscal_regra"

    id = Column(BigInteger, primary_key=True)
    regime = Column(Text, nullable=False)        # ICMS | IBS_CBS
    operacao = Column(Text, nullable=False)      # entrada_zfm | revenda_interna_am
    origem = Column(Text, nullable=False, default="nacional")  # nacional | importado | ambos
    uf = Column(Text, nullable=False, default="AM")
    aliquota = Column(Numeric(7, 4), nullable=False, default=0)   # 0.1800 = 18%
    aplica_desoneracao = Column(Boolean, nullable=False, default=True)
    base_legal = Column(Text, nullable=False)    # ex.: "Convênio ICM 65/88"
    vigencia_inicio = Column(Date, nullable=False)
    vigencia_fim = Column(Date, nullable=True)   # null = vigente
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())
