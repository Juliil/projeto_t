"""Modelos do módulo Contabilidade Connect.

Slice 1: receita avulsa (completude do faturamento) e sinalização de
necessidade contábil. As entidades do marketplace (Contador, Manifestação,
Vínculo, Chat, Auditoria) entram no slice 2.
"""
from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, Text, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB

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


class Contador(Base):
    """Perfil do contador (1:1 com um usuario tipo='contador')."""
    __tablename__ = "contadores"
    id = Column(BigInteger, primary_key=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True)
    crc = Column(Text, nullable=False)
    uf_crc = Column(Text, nullable=False)
    status_crc = Column(Text, nullable=False, default="pendente")  # pendente | ativo | invalido
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())


class ManifestacaoInteresse(Base):
    __tablename__ = "manifestacoes_interesse"
    id = Column(BigInteger, primary_key=True)
    sinalizacao_id = Column(BigInteger, ForeignKey("sinalizacoes_contabeis.id", ondelete="CASCADE"), nullable=False)
    contador_id = Column(BigInteger, ForeignKey("contadores.id", ondelete="CASCADE"), nullable=False)
    mensagem_inicial = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="pendente")  # pendente | aceita | recusada
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())


class VinculoContabil(Base):
    __tablename__ = "vinculos_contabeis"
    id = Column(BigInteger, primary_key=True)
    estudio_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    contador_id = Column(BigInteger, ForeignKey("contadores.id", ondelete="CASCADE"), nullable=False)
    escopo_dados = Column(JSONB, nullable=False, default=list)  # ex.: ["faturamento","estoque"]
    status = Column(Text, nullable=False, default="ativo")  # ativo | encerrado
    aceito_em = Column(TIMESTAMP(timezone=True), server_default=func.now())
    encerrado_em = Column(TIMESTAMP(timezone=True), nullable=True)


class MensagemChat(Base):
    __tablename__ = "mensagens_chat"
    id = Column(BigInteger, primary_key=True)
    vinculo_id = Column(BigInteger, ForeignKey("vinculos_contabeis.id", ondelete="CASCADE"), nullable=False)
    autor = Column(Text, nullable=False)  # estudio | contador
    corpo = Column(Text, nullable=False)
    contexto_anexado = Column(JSONB, nullable=True)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())


class AcessoAuditoria(Base):
    __tablename__ = "acessos_auditoria"
    id = Column(BigInteger, primary_key=True)
    vinculo_id = Column(BigInteger, ForeignKey("vinculos_contabeis.id", ondelete="CASCADE"), nullable=False)
    contador_id = Column(BigInteger, ForeignKey("contadores.id", ondelete="CASCADE"), nullable=False)
    recurso_acessado = Column(Text, nullable=False)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())
