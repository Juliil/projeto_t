"""contabilidade connect — receitas avulsas + sinalizações (v1.1 slice 1)

Revision ID: 0007_contabilidade_saude
Revises: 0006_estoque_ledger
Create Date: 2026-05-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007_contabilidade_saude"
down_revision: Union[str, None] = "0006_estoque_ledger"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "receitas",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("origem", sa.Text(), nullable=False, server_default="avulso"),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_receitas_usuario", "receitas", ["usuario_id", "data"])

    op.create_table(
        "sinalizacoes_contabeis",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("origem", sa.Text(), nullable=False, server_default="manual"),
        sa.Column("gatilho", sa.Text(), nullable=False, server_default="manual"),
        sa.Column("status", sa.Text(), nullable=False, server_default="procurando"),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_sinalizacoes_usuario", "sinalizacoes_contabeis", ["usuario_id", "status"])


def downgrade() -> None:
    op.drop_index("idx_sinalizacoes_usuario", table_name="sinalizacoes_contabeis")
    op.drop_table("sinalizacoes_contabeis")
    op.drop_index("idx_receitas_usuario", table_name="receitas")
    op.drop_table("receitas")
