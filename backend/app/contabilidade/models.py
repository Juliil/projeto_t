"""Modelos do módulo Contabilidade Connect.

Slice 1: receita avulsa (completude do faturamento) e sinalização de
necessidade contábil. As entidades do marketplace (Contador, Manifestação,
Vínculo, Chat, Auditoria) entram no slice 2.
"""
from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, Text, TIMESTAMP, func

from ..db import Base


class Receita(Base):
    """Faturamento que não veio de orçamento (ex.: trabalho no dinheiro).

    Garante que a projeção do teto do MEI reflita a receita real, não só
    os orçamentos aceitos no app.
    """
    __tablename__ = "receitas"
    id = Column(BigInteger, primary_key=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    descricao = Column(Text, nullable=False)
    valor = Column(Numeric(12, 2), nullable=False, default=0)
    data = Column(Date, nullable=False)
    origem = Column(Text, nullable=False, default="avulso")  # avulso
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())


class SinalizacaoContabil(Base):
    """Sinal de que o estúdio precisa de contador (manual ou por gatilho)."""
    __tablename__ = "sinalizacoes_contabeis"
    id = Column(BigInteger, primary_key=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    origem = Column(Text, nullable=False, default="manual")   # manual | automatica
    gatilho = Column(Text, nullable=False, default="manual")  # teto | funcionario | ir | manual
    # sem_sinalizacao | procurando | interesse_manifestado | vinculado | encerrado
    status = Column(Text, nullable=False, default="procurando")
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())
