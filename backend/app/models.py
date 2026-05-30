from sqlalchemy import (
    BigInteger, Column, ForeignKey, Numeric, String, Text, TIMESTAMP, func,
)
from sqlalchemy.dialects.postgresql import JSONB

from .db import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(BigInteger, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    senha_hash = Column(Text, nullable=False)
    nome = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="pre_registro")
    perfil = Column(JSONB, nullable=False, default=dict)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Material(Base):
    __tablename__ = "materiais"
    id = Column(BigInteger, primary_key=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome = Column(Text, nullable=False)
    categoria = Column(Text)
    unidade = Column(Text, nullable=False, default="un")
    custo_unitario = Column(Numeric(12, 2), nullable=False, default=0)
    estoque = Column(Numeric(12, 2), nullable=False, default=0)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Orcamento(Base):
    __tablename__ = "orcamentos"
    id = Column(BigInteger, primary_key=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    titulo = Column(Text, nullable=False)
    horas = Column(Numeric(8, 2), nullable=False, default=0)
    valor_hora = Column(Numeric(12, 2), nullable=False, default=0)
    margem_pct = Column(Numeric(6, 2), nullable=False, default=0)
    custo_materiais = Column(Numeric(12, 2), nullable=False, default=0)
    custo_mao_obra = Column(Numeric(12, 2), nullable=False, default=0)
    preco_final = Column(Numeric(12, 2), nullable=False, default=0)
    itens = Column(JSONB, nullable=False, default=list)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())


class LojaAnuncio(Base):
    __tablename__ = "loja_anuncios"
    id = Column(BigInteger, primary_key=True)
    vendedor_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(BigInteger, ForeignKey("materiais.id", ondelete="SET NULL"))
    titulo = Column(Text, nullable=False)
    descricao = Column(Text)
    tipo = Column(Text, nullable=False, default="fixo")  # fixo | leilao
    preco = Column(Numeric(12, 2), nullable=False, default=0)
    status = Column(Text, nullable=False, default="ativo")  # ativo | vendido
    comprador_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="SET NULL"))
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())


class LojaOferta(Base):
    __tablename__ = "loja_ofertas"
    id = Column(BigInteger, primary_key=True)
    anuncio_id = Column(BigInteger, ForeignKey("loja_anuncios.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now())


# --- Domínio distribuidora (B2B) ---
# Importado aqui para registrar as tabelas no Base.metadata (Alembic/testes).
from .distrib.fiscal import models as _fiscal_models  # noqa: E402,F401
