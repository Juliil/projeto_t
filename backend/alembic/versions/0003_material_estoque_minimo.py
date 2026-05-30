"""materiais: campo estoque_minimo (alerta de reposição — v1)

Revision ID: 0003_material_estoque_minimo
Revises: 0002_motor_fiscal_zfm
Create Date: 2026-05-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_material_estoque_minimo"
down_revision: Union[str, None] = "0002_motor_fiscal_zfm"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "materiais",
        sa.Column("estoque_minimo", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
    )


def downgrade() -> None:
    op.drop_column("materiais", "estoque_minimo")
