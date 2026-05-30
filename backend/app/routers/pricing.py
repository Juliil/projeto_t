from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Material, Orcamento, Usuario
from ..schemas import (
    CalcularIn, OrcamentoDetalheOut, OrcamentoOut, OrcamentoSalvoOut, StatusOrcamentoIn,
)
from ..security import get_current_user

router = APIRouter(prefix="/api/precificacao", tags=["precificacao"])

STATUS_VALIDOS = ("pendente", "aceito", "reprovado")


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


def _consumo(itens: list[dict]) -> dict[int, float]:
    """Soma a quantidade por material a partir dos itens calculados."""
    agg: dict[int, float] = {}
    for it in itens or []:
        mid = it.get("material_id")
        if mid is None:
            continue
        agg[int(mid)] = agg.get(int(mid), 0.0) + float(it.get("quantidade", 0) or 0)
    return agg


def _reconciliar_estoque(db: Session, usuario: Usuario, antigo: dict[int, float], novo: dict[int, float]) -> None:
    """Aplica (novo - antigo) como baixa no estoque. Delta negativo devolve."""
    for mid in set(antigo) | set(novo):
        delta = novo.get(mid, 0.0) - antigo.get(mid, 0.0)
        if delta == 0:
            continue
        material = db.get(Material, mid)
        if not material or material.usuario_id != usuario.id:
            continue  # material removido/alheio: não mexe no estoque
        material.estoque = round(float(material.estoque) - delta, 2)


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
        status="pendente",
        itens=r["itens"],
    )
    db.add(orc)
    db.commit()
    db.refresh(orc)
    return orc


@router.get("/orcamentos", response_model=list[OrcamentoDetalheOut])
def listar(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return (
        db.query(Orcamento)
        .filter(Orcamento.usuario_id == usuario.id)
        .order_by(Orcamento.criado_em.desc())
        .all()
    )


def _get_orc(orc_id: int, db: Session, usuario: Usuario) -> Orcamento:
    orc = db.get(Orcamento, orc_id)
    if not orc or orc.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return orc


@router.patch("/orcamentos/{orc_id}/status", response_model=OrcamentoDetalheOut)
def alterar_status(
    orc_id: int,
    dados: StatusOrcamentoIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if dados.status not in STATUS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"status deve ser um de {STATUS_VALIDOS}")
    orc = _get_orc(orc_id, db, usuario)
    antigo = _consumo(orc.itens) if orc.status == "aceito" else {}
    novo = _consumo(orc.itens) if dados.status == "aceito" else {}
    _reconciliar_estoque(db, usuario, antigo, novo)
    orc.status = dados.status
    db.commit()
    db.refresh(orc)
    return orc


@router.put("/orcamentos/{orc_id}", response_model=OrcamentoDetalheOut)
def atualizar(
    orc_id: int,
    dados: CalcularIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    orc = _get_orc(orc_id, db, usuario)
    r = _calcular(dados, db, usuario)
    # Se já está aceito, ajusta o estoque pela diferença de consumo.
    if orc.status == "aceito":
        _reconciliar_estoque(db, usuario, _consumo(orc.itens), _consumo(r["itens"]))
    orc.titulo = r["titulo"]
    orc.horas = dados.horas
    orc.valor_hora = dados.valor_hora
    orc.margem_pct = dados.margem_pct
    orc.custo_materiais = r["custo_materiais"]
    orc.custo_mao_obra = r["custo_mao_obra"]
    orc.preco_final = r["preco_final"]
    orc.itens = r["itens"]
    db.commit()
    db.refresh(orc)
    return orc
