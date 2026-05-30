from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Material, Orcamento, Usuario
from ..schemas import CalcularIn, OrcamentoOut, OrcamentoSalvoOut
from ..security import get_current_user

router = APIRouter(prefix="/api/precificacao", tags=["precificacao"])


def _calcular(dados: CalcularIn, db: Session, usuario: Usuario) -> dict:
    itens_calc = []
    custo_materiais = 0.0
    for item in dados.itens:
        material = db.get(Material, item.material_id)
        if not material or material.usuario_id != usuario.id:
            raise HTTPException(status_code=404, detail=f"Material {item.material_id} inválido")
        custo_unit = float(material.custo_unitario)
        subtotal = round(custo_unit * item.quantidade, 2)
        custo_materiais += subtotal
        itens_calc.append({
            "material_id": material.id,
            "nome": material.nome,
            "quantidade": item.quantidade,
            "custo_unitario": custo_unit,
            "subtotal": subtotal,
        })
    custo_materiais = round(custo_materiais, 2)
    custo_mao_obra = round(dados.horas * dados.valor_hora, 2)
    base = custo_materiais + custo_mao_obra
    preco_final = round(base * (1 + dados.margem_pct / 100.0), 2)
    return {
        "titulo": dados.titulo,
        "itens": itens_calc,
        "custo_materiais": custo_materiais,
        "custo_mao_obra": custo_mao_obra,
        "margem_pct": dados.margem_pct,
        "preco_final": preco_final,
    }


@router.post("/calcular", response_model=OrcamentoOut)
def calcular(dados: CalcularIn, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return _calcular(dados, db, usuario)


@router.post("/salvar", response_model=OrcamentoSalvoOut, status_code=201)
def salvar(dados: CalcularIn, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    r = _calcular(dados, db, usuario)
    orc = Orcamento(
        usuario_id=usuario.id,
        titulo=r["titulo"],
        horas=dados.horas,
        valor_hora=dados.valor_hora,
        margem_pct=dados.margem_pct,
        custo_materiais=r["custo_materiais"],
        custo_mao_obra=r["custo_mao_obra"],
        preco_final=r["preco_final"],
        itens=r["itens"],
    )
    db.add(orc)
    db.commit()
    db.refresh(orc)
    return orc


@router.get("/orcamentos", response_model=list[OrcamentoSalvoOut])
def listar(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return (
        db.query(Orcamento)
        .filter(Orcamento.usuario_id == usuario.id)
        .order_by(Orcamento.criado_em.desc())
        .all()
    )
