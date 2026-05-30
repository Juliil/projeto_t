"""orcamentos: agendado_em (agenda — vincula orçamento ao dia do mês)

Revision ID: 0005_orcamento_agenda
Revises: 0004_orcamento_status
Create Date: 2026-05-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_orcamento_agenda"
down_revision: Union[str, None] = "0004_orcamento_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orcamentos", sa.Column("agendado_em", sa.Date(), nullable=True))
    op.create_index("idx_orcamentos_agenda", "orcamentos", ["usuario_id", "agendado_em"])


def downgrade() -> None:
    op.drop_index("idx_orcamentos_agenda", table_name="orcamentos")
    op.drop_column("orcamentos", "agendado_em")
