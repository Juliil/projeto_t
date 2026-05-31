from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import LIMITE_MEI_ANUAL
from ..db import get_db
from ..models import Usuario
from ..security import get_current_user
from .models import Receita, SinalizacaoContabil
from .schemas import ReceitaIn, ReceitaOut, SaudeOut, SinalizacaoOut, SinalizarIn
from .service import calcular_saude

router = APIRouter(prefix="/api/contabilidade", tags=["contabilidade"])


def _sinalizacao_ativa(db: Session, usuario_id: int) -> SinalizacaoContabil | None:
    return (
        db.query(SinalizacaoContabil)
        .filter(SinalizacaoContabil.usuario_id == usuario_id, SinalizacaoContabil.status != "encerrado")
        .order_by(SinalizacaoContabil.criado_em.desc())
        .first()
    )


@router.get("/saude", response_model=SaudeOut)
def saude(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    s = calcular_saude(db, usuario.id, LIMITE_MEI_ANUAL)
    ativa = _sinalizacao_ativa(db, usuario.id)
    return SaudeOut(
        faturamento_12m=s.faturamento_12m, teto_mei=s.teto_mei, pct_teto=s.pct_teto,
        restante=s.restante, media_mensal=s.media_mensal, meses_ate_teto=s.meses_ate_teto,
        projecao_estouro=s.projecao_estouro, gatilhos=s.gatilhos,
        fonte_orcamentos=s.fonte_orcamentos, fonte_avulsa=s.fonte_avulsa,
        sinalizacao_status=ativa.status if ativa else "sem_sinalizacao",
    )


@router.get("/receitas", response_model=list[ReceitaOut])
def listar_receitas(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return (
        db.query(Receita)
        .filter(Receita.usuario_id == usuario.id)
        .order_by(Receita.data.desc())
        .all()
    )


@router.post("/receitas", response_model=ReceitaOut, status_code=201)
def criar_receita(dados: ReceitaIn, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    r = Receita(usuario_id=usuario.id, descricao=dados.descricao, valor=dados.valor, data=dados.data, origem="avulso")
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/receitas/{receita_id}", status_code=204)
def remover_receita(receita_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    r = db.get(Receita, receita_id)
    if not r or r.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    db.delete(r)
    db.commit()


@router.post("/sinalizar", response_model=SinalizacaoOut, status_code=201)
def sinalizar(dados: SinalizarIn, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    """Estúdio sinaliza necessidade de contador (entra no mural, anonimizado — slice 2)."""
    ativa = _sinalizacao_ativa(db, usuario.id)
    if ativa and ativa.status in ("procurando", "interesse_manifestado"):
        return ativa  # já está procurando
    s = SinalizacaoContabil(usuario_id=usuario.id, origem=dados.origem, gatilho=dados.gatilho, status="procurando")
    db.add(s)
    db.commit()
    db.refresh(s)
    return s
