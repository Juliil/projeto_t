from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import LojaAnuncio, LojaOferta, Material, Usuario
from ..schemas import AnuncioIn, AnuncioOut, OfertaIn
from ..security import get_current_user

router = APIRouter(prefix="/api/loja", tags=["loja"])


def _preco_atual(anuncio: LojaAnuncio, db: Session) -> tuple[float, int]:
    base = float(anuncio.preco)
    agg = (
        db.query(func.max(LojaOferta.valor), func.count(LojaOferta.id))
        .filter(LojaOferta.anuncio_id == anuncio.id)
        .first()
    )
    maior, total = agg if agg else (None, 0)
    if anuncio.tipo == "leilao" and maior is not None:
        base = float(maior)
    return base, int(total or 0)


def _montar(anuncio: LojaAnuncio, db: Session, usuario: Usuario) -> AnuncioOut:
    preco_atual, total = _preco_atual(anuncio, db)
    vendedor = db.get(Usuario, anuncio.vendedor_id)
    return AnuncioOut(
        id=anuncio.id,
        titulo=anuncio.titulo,
        descricao=anuncio.descricao,
        tipo=anuncio.tipo,
        preco=float(anuncio.preco),
        preco_atual=preco_atual,
        status=anuncio.status,
        vendedor=vendedor.nome if vendedor else "—",
        sou_dono=anuncio.vendedor_id == usuario.id,
        total_ofertas=total,
        criado_em=anuncio.criado_em,
    )


@router.get("", response_model=list[AnuncioOut])
def listar(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    anuncios = (
        db.query(LojaAnuncio)
        .filter(LojaAnuncio.status == "ativo")
        .order_by(LojaAnuncio.criado_em.desc())
        .all()
    )
    return [_montar(a, db, usuario) for a in anuncios]


@router.post("", response_model=AnuncioOut, status_code=201)
def criar(dados: AnuncioIn, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    if dados.tipo not in ("fixo", "leilao"):
        raise HTTPException(status_code=400, detail="Tipo deve ser 'fixo' ou 'leilao'")
    if dados.material_id is not None:
        material = db.get(Material, dados.material_id)
        if not material or material.usuario_id != usuario.id:
            raise HTTPException(status_code=404, detail="Material inválido")
    anuncio = LojaAnuncio(
        vendedor_id=usuario.id,
        material_id=dados.material_id,
        titulo=dados.titulo,
        descricao=dados.descricao,
        tipo=dados.tipo,
        preco=dados.preco,
        status="ativo",
    )
    db.add(anuncio)
    db.commit()
    db.refresh(anuncio)
    return _montar(anuncio, db, usuario)


@router.post("/{anuncio_id}/oferta", response_model=AnuncioOut)
def ofertar(
    anuncio_id: int,
    dados: OfertaIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    anuncio = db.get(LojaAnuncio, anuncio_id)
    if not anuncio or anuncio.status != "ativo":
        raise HTTPException(status_code=404, detail="Anúncio indisponível")
    if anuncio.tipo != "leilao":
        raise HTTPException(status_code=400, detail="Este anúncio é de preço fixo")
    if anuncio.vendedor_id == usuario.id:
        raise HTTPException(status_code=400, detail="Você não pode ofertar no próprio anúncio")
    preco_atual, _ = _preco_atual(anuncio, db)
    if dados.valor <= preco_atual:
        raise HTTPException(status_code=400, detail=f"A oferta deve ser maior que R$ {preco_atual:.2f}")
    db.add(LojaOferta(anuncio_id=anuncio.id, usuario_id=usuario.id, valor=dados.valor))
    db.commit()
    return _montar(anuncio, db, usuario)


@router.post("/{anuncio_id}/comprar", response_model=AnuncioOut)
def comprar(anuncio_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    anuncio = db.get(LojaAnuncio, anuncio_id)
    if not anuncio or anuncio.status != "ativo":
        raise HTTPException(status_code=404, detail="Anúncio indisponível")
    if anuncio.tipo != "fixo":
        raise HTTPException(status_code=400, detail="Anúncio de leilão: faça uma oferta")
    if anuncio.vendedor_id == usuario.id:
        raise HTTPException(status_code=400, detail="Você não pode comprar o próprio anúncio")
    anuncio.status = "vendido"
    anuncio.comprador_id = usuario.id
    db.commit()
    db.refresh(anuncio)
    return _montar(anuncio, db, usuario)
