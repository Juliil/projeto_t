from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
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
    material = Material(usuario_id=usuario.id, **dados.model_dump())
    db.add(material)
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
    for k, v in dados.model_dump().items():
        setattr(material, k, v)
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
