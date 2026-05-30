from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Usuario
from ...security import get_current_user
from .engine import FiscalError, simular_entrada
from .models import FiscalNCM
from .schemas import NCMOut, SimularEntradaIn, SimularEntradaOut

router = APIRouter(prefix="/api/fiscal", tags=["fiscal"])


@router.get("/ncm", response_model=list[NCMOut])
def listar_ncm(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return db.query(FiscalNCM).order_by(FiscalNCM.codigo).all()


@router.post("/simular-entrada", response_model=SimularEntradaOut)
def simular_entrada_zfm(
    dados: SimularEntradaIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Simula a entrada de mercadoria na ZFM e calcula a desoneração de ICMS
    (ou IBS/CBS, conforme vigência) que reduz o custo de aquisição."""
    if dados.regime and dados.regime not in ("ICMS", "IBS_CBS"):
        raise HTTPException(status_code=400, detail="regime deve ser 'ICMS' ou 'IBS_CBS'")
    try:
        resultado = simular_entrada(
            db, ncm_codigo=dados.ncm, valor=dados.valor, origem=dados.origem,
            data_ref=dados.data_ref, regime=dados.regime,
        )
    except FiscalError as e:
        raise HTTPException(status_code=422, detail=str(e))
    # Decimais viram float na serialização do schema
    return SimularEntradaOut(**asdict(resultado))
