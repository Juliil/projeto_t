"""orcamentos: status (pendente/aceito/reprovado) — correlação com estoque (v1)

Revision ID: 0004_orcamento_status
Revises: 0003_material_estoque_minimo
Create Date: 2026-05-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_orcamento_status"
down_revision: Union[str, None] = "0003_material_estoque_minimo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "orcamentos",
        sa.Column("status", sa.Text(), nullable=False, server_default="pendente"),
    )


def downgrade() -> None:
    op.drop_column("orcamentos", "status")
