from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..estoque import aplicar_movimento
from ..models import Material, Usuario
from ..schemas import MaterialIn, MaterialOut
from ..security import get_current_user

router = APIRouter(prefix="/api/materiais", tags=["materiais"])


@router.get("", response_model=list[MaterialOut])
def listar(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return (
        db.query(Material)
        .filter(Material.usuario_id == usuario.id)
        .order_by(Material.criado_em.desc())
        .all()
    )


@router.post("", response_model=MaterialOut, status_code=201)
def criar(dados: MaterialIn, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    dump = dados.model_dump()
    estoque_inicial = dump.pop("estoque", 0) or 0
    material = Material(usuario_id=usuario.id, estoque=0, **dump)
    db.add(material)
    db.flush()  # garante material.id para o ledger
    if estoque_inicial:
        aplicar_movimento(db, usuario.id, material, estoque_inicial, origem="cadastro", tipo="entrada")
    db.commit()
    db.refresh(material)
    return material


@router.put("/{material_id}", response_model=MaterialOut)
def atualizar(
    material_id: int,
    dados: MaterialIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    material = db.get(Material, material_id)
    if not material or material.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    dump = dados.model_dump()
    novo_estoque = dump.pop("estoque", float(material.estoque))
    for k, v in dump.items():
        setattr(material, k, v)
    # ajuste manual de estoque vira movimentação (entrada/saída pelo sinal)
    delta = round(float(novo_estoque) - float(material.estoque), 2)
    if delta:
        aplicar_movimento(db, usuario.id, material, delta, origem="edicao_material")
    db.commit()
    db.refresh(material)
    return material


@router.delete("/{material_id}", status_code=204)
def remover(material_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    material = db.get(Material, material_id)
    if not material or material.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    db.delete(material)
    db.commit()
