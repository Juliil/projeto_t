from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from datetime import datetime, timezone

from ..config import LIMITE_MEI_ANUAL
from ..db import get_db
from ..models import Usuario
from ..security import get_current_user
from .models import (
    Contador, ManifestacaoInteresse, MensagemChat, Receita, SinalizacaoContabil, VinculoContabil,
)
from .schemas import (
    AceitarIn, ManifestacaoEstudioOut, MensagemIn, MensagemOut, ReceitaIn, ReceitaOut,
    SaudeOut, SinalizacaoOut, SinalizarIn, VinculoEstudioOut,
)
from .service import ESCOPOS_DISPONIVEIS, calcular_saude

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


# ---------- Marketplace (lado do estúdio) ----------
def _contador_nome(db: Session, contador: Contador) -> str:
    u = db.get(Usuario, contador.usuario_id)
    return u.nome if u else "Contador"


def _vinculo_ativo(db: Session, estudio_id: int) -> VinculoContabil | None:
    return (
        db.query(VinculoContabil)
        .filter(VinculoContabil.estudio_id == estudio_id, VinculoContabil.status == "ativo")
        .order_by(VinculoContabil.aceito_em.desc())
        .first()
    )


@router.get("/interesses", response_model=list[ManifestacaoEstudioOut])
def interesses(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    ativa = _sinalizacao_ativa(db, usuario.id)
    if not ativa:
        return []
    manifs = (
        db.query(ManifestacaoInteresse)
        .filter(ManifestacaoInteresse.sinalizacao_id == ativa.id)
        .order_by(ManifestacaoInteresse.criado_em.desc())
        .all()
    )
    out = []
    for m in manifs:
        c = db.get(Contador, m.contador_id)
        out.append(ManifestacaoEstudioOut(
            id=m.id, contador_nome=_contador_nome(db, c) if c else "Contador",
            crc=c.crc if c else "", uf_crc=c.uf_crc if c else "", status_crc=c.status_crc if c else "",
            mensagem_inicial=m.mensagem_inicial, status=m.status, criado_em=m.criado_em,
        ))
    return out


@router.post("/interesses/{manifestacao_id}/aceitar", response_model=VinculoEstudioOut)
def aceitar(manifestacao_id: int, dados: AceitarIn, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    m = db.get(ManifestacaoInteresse, manifestacao_id)
    sin = db.get(SinalizacaoContabil, m.sinalizacao_id) if m else None
    if not m or not sin or sin.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Manifestação não encontrada")
    if _vinculo_ativo(db, usuario.id):
        raise HTTPException(status_code=409, detail="Você já tem um contador vinculado")

    escopo = [e for e in dados.escopo if e in ESCOPOS_DISPONIVEIS]
    vinculo = VinculoContabil(estudio_id=usuario.id, contador_id=m.contador_id, escopo_dados=escopo, status="ativo")
    db.add(vinculo)
    m.status = "aceita"
    # recusa educada automática aos demais interessados
    for outra in db.query(ManifestacaoInteresse).filter(
        ManifestacaoInteresse.sinalizacao_id == sin.id, ManifestacaoInteresse.id != m.id
    ):
        outra.status = "recusada"
    sin.status = "vinculado"
    db.commit()
    db.refresh(vinculo)
    c = db.get(Contador, vinculo.contador_id)
    return VinculoEstudioOut(
        id=vinculo.id, contador_nome=_contador_nome(db, c), crc=c.crc, uf_crc=c.uf_crc,
        escopo_dados=vinculo.escopo_dados, status=vinculo.status, aceito_em=vinculo.aceito_em,
    )


@router.get("/vinculo", response_model=VinculoEstudioOut | None)
def vinculo(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    v = _vinculo_ativo(db, usuario.id)
    if not v:
        return None
    c = db.get(Contador, v.contador_id)
    return VinculoEstudioOut(
        id=v.id, contador_nome=_contador_nome(db, c), crc=c.crc, uf_crc=c.uf_crc,
        escopo_dados=v.escopo_dados, status=v.status, aceito_em=v.aceito_em,
    )


@router.post("/vinculo/encerrar", status_code=204)
def encerrar_vinculo(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    v = _vinculo_ativo(db, usuario.id)
    if not v:
        raise HTTPException(status_code=404, detail="Sem vínculo ativo")
    v.status = "encerrado"
    v.encerrado_em = datetime.now(timezone.utc)
    db.commit()


def _mensagens_do_vinculo(db: Session, vinculo_id: int):
    return (
        db.query(MensagemChat)
        .filter(MensagemChat.vinculo_id == vinculo_id)
        .order_by(MensagemChat.criado_em.asc())
        .all()
    )


@router.get("/vinculo/mensagens", response_model=list[MensagemOut])
def listar_mensagens(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    v = _vinculo_ativo(db, usuario.id)
    return _mensagens_do_vinculo(db, v.id) if v else []


@router.post("/vinculo/mensagens", response_model=MensagemOut, status_code=201)
def enviar_mensagem(dados: MensagemIn, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    v = _vinculo_ativo(db, usuario.id)
    if not v:
        raise HTTPException(status_code=404, detail="Sem vínculo ativo")
    msg = MensagemChat(vinculo_id=v.id, autor="estudio", corpo=dados.corpo)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
