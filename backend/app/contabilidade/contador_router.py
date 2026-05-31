"""Portal do contador — mural anonimizado, interesse, dados consentidos, chat.

Antes do aceite do estúdio, o contador só vê resumo agregado e anonimizado
(sem PII/CNPJ/razão social). Após o aceite, vê apenas o escopo consentido,
com trilha de auditoria.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import LIMITE_MEI_ANUAL
from ..db import get_db
from ..models import Usuario
from ..security import get_current_user
from .models import (
    AcessoAuditoria, Contador, ManifestacaoInteresse, MensagemChat,
    SinalizacaoContabil, VinculoContabil,
)
from .schemas import (
    ContadorOut, InteresseIn, LeadOut, MensagemIn, MensagemOut, VinculoContadorOut,
)
from .service import calcular_saude, faixa_faturamento, pacote_dados

router = APIRouter(prefix="/api/contador", tags=["contador"])


def get_current_contador(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)) -> Contador:
    if usuario.tipo != "contador":
        raise HTTPException(status_code=403, detail="Acesso restrito a contadores")
    contador = db.query(Contador).filter(Contador.usuario_id == usuario.id).first()
    if not contador:
        raise HTTPException(status_code=404, detail="Perfil de contador não encontrado")
    return contador


@router.get("/me", response_model=ContadorOut)
def me(db: Session = Depends(get_db), contador: Contador = Depends(get_current_contador)):
    u = db.get(Usuario, contador.usuario_id)
    return ContadorOut(id=contador.id, nome=u.nome, crc=contador.crc, uf_crc=contador.uf_crc, status_crc=contador.status_crc)


@router.get("/leads", response_model=list[LeadOut])
def leads(db: Session = Depends(get_db), contador: Contador = Depends(get_current_contador)):
    sinais = (
        db.query(SinalizacaoContabil)
        .filter(SinalizacaoContabil.status.in_(["procurando", "interesse_manifestado"]))
        .order_by(SinalizacaoContabil.criado_em.desc())
        .all()
    )
    out = []
    for s in sinais:
        estudio = db.get(Usuario, s.usuario_id)
        if not estudio:
            continue
        saude = calcular_saude(db, estudio.id, LIMITE_MEI_ANUAL)
        regiao = (estudio.perfil or {}).get("cidade") or "—"
        ja = db.query(ManifestacaoInteresse).filter(
            ManifestacaoInteresse.sinalizacao_id == s.id,
            ManifestacaoInteresse.contador_id == contador.id,
        ).first() is not None
        out.append(LeadOut(
            sinalizacao_id=s.id,
            faixa_faturamento=faixa_faturamento(saude.faturamento_12m),
            regiao=regiao, segmento="Tatuagem", gatilho=s.gatilho,
            pct_teto=saude.pct_teto, criado_em=s.criado_em, ja_manifestei=ja,
        ))
    return out


@router.post("/leads/{sinalizacao_id}/interesse", status_code=201)
def manifestar_interesse(
    sinalizacao_id: int, dados: InteresseIn,
    db: Session = Depends(get_db), contador: Contador = Depends(get_current_contador),
):
    s = db.get(SinalizacaoContabil, sinalizacao_id)
    if not s or s.status not in ("procurando", "interesse_manifestado"):
        raise HTTPException(status_code=404, detail="Lead indisponível")
    existe = db.query(ManifestacaoInteresse).filter(
        ManifestacaoInteresse.sinalizacao_id == s.id,
        ManifestacaoInteresse.contador_id == contador.id,
    ).first()
    if existe:
        return {"ok": True, "ja_manifestado": True}
    db.add(ManifestacaoInteresse(sinalizacao_id=s.id, contador_id=contador.id, mensagem_inicial=dados.mensagem))
    s.status = "interesse_manifestado"
    db.commit()
    return {"ok": True}


def _vinculos_ativos(db: Session, contador_id: int):
    return (
        db.query(VinculoContabil)
        .filter(VinculoContabil.contador_id == contador_id, VinculoContabil.status == "ativo")
        .order_by(VinculoContabil.aceito_em.desc())
        .all()
    )


@router.get("/vinculos", response_model=list[VinculoContadorOut])
def vinculos(db: Session = Depends(get_db), contador: Contador = Depends(get_current_contador)):
    out = []
    for v in _vinculos_ativos(db, contador.id):
        estudio = db.get(Usuario, v.estudio_id)
        out.append(VinculoContadorOut(
            id=v.id, estudio_nome=estudio.nome if estudio else "Estúdio",
            escopo_dados=v.escopo_dados, status=v.status, aceito_em=v.aceito_em,
        ))
    return out


def _get_vinculo_do_contador(db: Session, vinculo_id: int, contador: Contador) -> VinculoContabil:
    v = db.get(VinculoContabil, vinculo_id)
    if not v or v.contador_id != contador.id or v.status != "ativo":
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    return v


@router.get("/vinculos/{vinculo_id}/dados")
def dados_consentidos(vinculo_id: int, db: Session = Depends(get_db), contador: Contador = Depends(get_current_contador)):
    v = _get_vinculo_do_contador(db, vinculo_id, contador)
    estudio = db.get(Usuario, v.estudio_id)
    pacote = pacote_dados(db, estudio, v.escopo_dados, LIMITE_MEI_ANUAL)
    # trilha de auditoria de todo acesso a dado do estúdio
    db.add(AcessoAuditoria(vinculo_id=v.id, contador_id=contador.id, recurso_acessado="pacote_dados"))
    db.commit()
    return {"estudio_nome": estudio.nome, "escopo": v.escopo_dados, "dados": pacote}


@router.get("/vinculos/{vinculo_id}/mensagens", response_model=list[MensagemOut])
def listar_mensagens(vinculo_id: int, db: Session = Depends(get_db), contador: Contador = Depends(get_current_contador)):
    v = _get_vinculo_do_contador(db, vinculo_id, contador)
    return (
        db.query(MensagemChat).filter(MensagemChat.vinculo_id == v.id)
        .order_by(MensagemChat.criado_em.asc()).all()
    )


@router.post("/vinculos/{vinculo_id}/mensagens", response_model=MensagemOut, status_code=201)
def enviar_mensagem(vinculo_id: int, dados: MensagemIn, db: Session = Depends(get_db), contador: Contador = Depends(get_current_contador)):
    v = _get_vinculo_do_contador(db, vinculo_id, contador)
    msg = MensagemChat(vinculo_id=v.id, autor="contador", corpo=dados.corpo)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
