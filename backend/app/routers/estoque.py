from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import EstoqueMovimento, Usuario
from ..schemas import MovimentoOut
from ..security import get_current_user

router = APIRouter(prefix="/api/estoque", tags=["estoque"])


@router.get("/movimentos", response_model=list[MovimentoOut])
def movimentos(
    material_id: Optional[int] = None,
    limite: int = 200,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Ledger de movimentações (série temporal) do usuário, mais recentes primeiro."""
    q = db.query(EstoqueMovimento).filter(EstoqueMovimento.usuario_id == usuario.id)
    if material_id is not None:
        q = q.filter(EstoqueMovimento.material_id == material_id)
    return q.order_by(EstoqueMovimento.criado_em.desc()).limit(min(limite, 500)).all()


@router.get("/resumo")
def resumo(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    """Agregado por material: entradas, saídas, nº de movimentos e último movimento.

    Semente da camada de analytics (consumo, giro, reposição)."""
    rows = (
        db.query(
            EstoqueMovimento.material_id,
            EstoqueMovimento.material_nome,
            func.sum(case((EstoqueMovimento.quantidade > 0, EstoqueMovimento.quantidade), else_=0)).label("entradas"),
            func.sum(case((EstoqueMovimento.quantidade < 0, -EstoqueMovimento.quantidade), else_=0)).label("saidas"),
            func.count(EstoqueMovimento.id).label("movimentos"),
            func.max(EstoqueMovimento.criado_em).label("ultimo_movimento"),
        )
        .filter(EstoqueMovimento.usuario_id == usuario.id)
        .group_by(EstoqueMovimento.material_id, EstoqueMovimento.material_nome)
        .order_by(func.sum(case((EstoqueMovimento.quantidade < 0, -EstoqueMovimento.quantidade), else_=0)).desc())
        .all()
    )
    return [
        {
            "material_id": r.material_id,
            "material_nome": r.material_nome,
            "entradas": float(r.entradas or 0),
            "saidas": float(r.saidas or 0),
            "movimentos": int(r.movimentos),
            "ultimo_movimento": r.ultimo_movimento,
        }
        for r in rows
    ]
