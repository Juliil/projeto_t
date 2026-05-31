"""contabilidade connect — marketplace contador↔estúdio (v1.1 slice 2)

usuarios.tipo + contadores, manifestações, vínculos, chat e auditoria.

Revision ID: 0008_contabilidade_marketplace
Revises: 0007_contabilidade_saude
Create Date: 2026-05-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0008_contabilidade_marketplace"
down_revision: Union[str, None] = "0007_contabilidade_saude"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("tipo", sa.Text(), nullable=False, server_default="estudio"))

    op.create_table(
        "contadores",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("crc", sa.Text(), nullable=False),
        sa.Column("uf_crc", sa.Text(), nullable=False),
        sa.Column("status_crc", sa.Text(), nullable=False, server_default="pendente"),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "manifestacoes_interesse",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("sinalizacao_id", sa.BigInteger(), sa.ForeignKey("sinalizacoes_contabeis.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contador_id", sa.BigInteger(), sa.ForeignKey("contadores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mensagem_inicial", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="pendente"),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_manifest_sinalizacao", "manifestacoes_interesse", ["sinalizacao_id"])

    op.create_table(
        "vinculos_contabeis",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("estudio_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contador_id", sa.BigInteger(), sa.ForeignKey("contadores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("escopo_dados", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("status", sa.Text(), nullable=False, server_default="ativo"),
        sa.Column("aceito_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("encerrado_em", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("idx_vinculo_estudio", "vinculos_contabeis", ["estudio_id", "status"])
    op.create_index("idx_vinculo_contador", "vinculos_contabeis", ["contador_id", "status"])

    op.create_table(
        "mensagens_chat",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("vinculo_id", sa.BigInteger(), sa.ForeignKey("vinculos_contabeis.id", ondelete="CASCADE"), nullable=False),
        sa.Column("autor", sa.Text(), nullable=False),
        sa.Column("corpo", sa.Text(), nullable=False),
        sa.Column("contexto_anexado", postgresql.JSONB(), nullable=True),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_chat_vinculo", "mensagens_chat", ["vinculo_id", "criado_em"])

    op.create_table(
        "acessos_auditoria",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("vinculo_id", sa.BigInteger(), sa.ForeignKey("vinculos_contabeis.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contador_id", sa.BigInteger(), sa.ForeignKey("contadores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recurso_acessado", sa.Text(), nullable=False),
        sa.Column("criado_em", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("acessos_auditoria")
    op.drop_index("idx_chat_vinculo", table_name="mensagens_chat")
    op.drop_table("mensagens_chat")
    op.drop_index("idx_vinculo_contador", table_name="vinculos_contabeis")
    op.drop_index("idx_vinculo_estudio", table_name="vinculos_contabeis")
    op.drop_table("vinculos_contabeis")
    op.drop_index("idx_manifest_sinalizacao", table_name="manifestacoes_interesse")
    op.drop_table("manifestacoes_interesse")
    op.drop_table("contadores")
    op.drop_column("usuarios", "tipo")
