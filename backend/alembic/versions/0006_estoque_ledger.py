"""ledger de estoque (estoque_movimentos) + orcamentos.aceito_em

Série temporal de movimentações para a camada de analytics (data-driven).

Revision ID: 0006_estoque_ledger
Revises: 0005_orcamento_agenda
Create Date: 2026-05-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006_estoque_ledger"
down_revision: Union[str, None] = "0005_orcamento_agenda"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orcamentos", sa.Column("aceito_em", sa.TIMESTAMP(timezone=True), nullable=True))

    op.create_table(
        "estoque_movimentos",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("material_id", sa.BigInteger(), sa.ForeignKey("materiais.id", ondelete="SET NULL"), nullable=True),
        sa.Column("material_nome", sa.Text(), nullable=False),
        sa.Column("tipo", sa.Text(), nullable=False),
        sa.Column("quantidade", sa.Numeric(12, 2), nullable=False),
        sa.Column("saldo_apos", sa.Numeric(12, 2), nullable=False),
        sa.Column("origem", sa.Text(), nullable=False),
        sa.Column("orcamento_id", sa.BigInteger(), sa.ForeignKey("orcamentos.id", ondelete="SET NULL"), nullable=True),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_estoque_mov_usuario", "estoque_movimentos", ["usuario_id", "criado_em"])
    op.create_index("idx_estoque_mov_material", "estoque_movimentos", ["material_id"])


def downgrade() -> None:
    op.drop_index("idx_estoque_mov_material", table_name="estoque_movimentos")
    op.drop_index("idx_estoque_mov_usuario", table_name="estoque_movimentos")
    op.drop_table("estoque_movimentos")
    op.drop_column("orcamentos", "aceito_em")
