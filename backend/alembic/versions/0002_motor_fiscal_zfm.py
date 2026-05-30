"""motor fiscal ZFM — NCM + regras versionadas por vigência (Fase 1)

Cria as tabelas do motor fiscal e popula um seed inicial de premissas.
# FISCAL: alíquotas/enquadramentos do seed são ilustrativos; validar com contador.

Revision ID: 0002_motor_fiscal_zfm
Revises: 0001_baseline_poc
Create Date: 2026-05-30
"""
from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_motor_fiscal_zfm"
down_revision: Union[str, None] = "0001_baseline_poc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ncm = op.create_table(
        "fiscal_ncm",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("codigo", sa.Text(), nullable=False, unique=True),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("elegivel_zfm", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("excluido_beneficio", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    regra = op.create_table(
        "fiscal_regra",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("regime", sa.Text(), nullable=False),
        sa.Column("operacao", sa.Text(), nullable=False),
        sa.Column("origem", sa.Text(), nullable=False, server_default="nacional"),
        sa.Column("uf", sa.Text(), nullable=False, server_default="AM"),
        sa.Column("aliquota", sa.Numeric(7, 4), nullable=False, server_default=sa.text("0")),
        sa.Column("aplica_desoneracao", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("base_legal", sa.Text(), nullable=False),
        sa.Column("vigencia_inicio", sa.Date(), nullable=False),
        sa.Column("vigencia_fim", sa.Date(), nullable=True),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_fiscal_regra_lookup", "fiscal_regra", ["operacao", "uf", "origem", "regime"])

    # ---- Seed (premissas ilustrativas) ----
    op.bulk_insert(ncm, [
        {"codigo": "9018.32.19", "descricao": "Agulhas e cartuchos para tatuagem", "elegivel_zfm": True, "excluido_beneficio": False},
        {"codigo": "3215.90.00", "descricao": "Tintas para tatuagem", "elegivel_zfm": True, "excluido_beneficio": False},
        {"codigo": "3926.90.90", "descricao": "Biqueiras e descartáveis plásticos", "elegivel_zfm": True, "excluido_beneficio": False},
        {"codigo": "8543.70.99", "descricao": "Máquinas e fontes de tatuagem", "elegivel_zfm": True, "excluido_beneficio": False},
        {"codigo": "0000.00.00", "descricao": "Exemplo de item EXCLUÍDO do benefício", "elegivel_zfm": True, "excluido_beneficio": True},
    ])

    op.bulk_insert(regra, [
        {
            "regime": "ICMS", "operacao": "entrada_zfm", "origem": "nacional", "uf": "AM",
            "aliquota": 0.1800, "aplica_desoneracao": True,
            "base_legal": "Convênio ICM 65/88 (isenção ICMS na entrada da ZFM, computado como desconto)",
            "vigencia_inicio": date(1988, 3, 1), "vigencia_fim": None,
        },
        {
            # Ilustrativo: início da fase plena IBS/CBS para fins de demonstração da coexistência.
            "regime": "IBS_CBS", "operacao": "entrada_zfm", "origem": "nacional", "uf": "AM",
            "aliquota": 0.0000, "aplica_desoneracao": True,
            "base_legal": "LC 214/2025 (alíquota 0% IBS/CBS p/ habilitados ZFM)",
            "vigencia_inicio": date(2027, 1, 1), "vigencia_fim": None,
        },
    ])


def downgrade() -> None:
    op.drop_index("idx_fiscal_regra_lookup", table_name="fiscal_regra")
    op.drop_table("fiscal_regra")
    op.drop_table("fiscal_ncm")
