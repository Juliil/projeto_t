"""Movimentação de estoque com registro em ledger (estoque_movimentos).

Centraliza toda alteração de saldo: aplica o delta no material E grava uma
linha imutável com carimbo de tempo, para alimentar analytics no futuro.
"""
from sqlalchemy.orm import Session

from .models import EstoqueMovimento, Material


def aplicar_movimento(
    db: Session,
    usuario_id: int,
    material: Material,
    delta: float,
    origem: str,
    orcamento_id: int | None = None,
    tipo: str | None = None,
) -> EstoqueMovimento | None:
    """Soma `delta` (assinado) ao estoque do material e registra a movimentação.

    delta > 0 = entrada, delta < 0 = saída. Retorna None se delta == 0.
    `tipo` pode ser forçado (ex.: 'ajuste'); senão é inferido pelo sinal.
    """
    delta = round(float(delta), 2)
    if delta == 0:
        return None
    material.estoque = round(float(material.estoque) + delta, 2)
    mov = EstoqueMovimento(
        usuario_id=usuario_id,
        material_id=material.id,
        material_nome=material.nome,
        tipo=tipo or ("entrada" if delta > 0 else "saida"),
        quantidade=delta,
        saldo_apos=material.estoque,
        origem=origem,
        orcamento_id=orcamento_id,
    )
    db.add(mov)
    return mov
