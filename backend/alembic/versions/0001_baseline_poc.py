"""baseline — schema da PoC (Projeto T)

Reproduz exatamente o schema de db/init.sql, agora sob controle do Alembic.
Em ambiente existente, use `alembic stamp head` (não recria as tabelas).

Revision ID: 0001_baseline_poc
Revises:
Create Date: 2026-05-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_baseline_poc"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("senha_hash", sa.Text(), nullable=False),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="pre_registro"),
        sa.Column("perfil", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "materiais",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("categoria", sa.Text(), nullable=True),
        sa.Column("unidade", sa.Text(), nullable=False, server_default="un"),
        sa.Column("custo_unitario", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("estoque", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_materiais_usuario", "materiais", ["usuario_id"])

    op.create_table(
        "orcamentos",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("titulo", sa.Text(), nullable=False),
        sa.Column("horas", sa.Numeric(8, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("valor_hora", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("margem_pct", sa.Numeric(6, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("custo_materiais", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("custo_mao_obra", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("preco_final", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("itens", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_orcamentos_usuario", "orcamentos", ["usuario_id"])

    op.create_table(
        "loja_anuncios",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("vendedor_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("material_id", sa.BigInteger(), sa.ForeignKey("materiais.id", ondelete="SET NULL"), nullable=True),
        sa.Column("titulo", sa.Text(), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("tipo", sa.Text(), nullable=False, server_default="fixo"),
        sa.Column("preco", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.Text(), nullable=False, server_default="ativo"),
        sa.Column("comprador_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_anuncios_status", "loja_anuncios", ["status"])

    op.create_table(
        "loja_ofertas",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("anuncio_id", sa.BigInteger(), sa.ForeignKey("loja_anuncios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_ofertas_anuncio", "loja_ofertas", ["anuncio_id"])


def downgrade() -> None:
    op.drop_table("loja_ofertas")
    op.drop_table("loja_anuncios")
    op.drop_table("orcamentos")
    op.drop_table("materiais")
    op.drop_table("usuarios")
