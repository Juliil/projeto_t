from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReceitaIn(BaseModel):
    descricao: str
    valor: float = Field(..., gt=0)
    data: date


class ReceitaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    descricao: str
    valor: float
    data: date
    origem: str
    criado_em: datetime


class SaudeOut(BaseModel):
    faturamento_12m: float
    teto_mei: float
    pct_teto: float
    restante: float
    media_mensal: float
    meses_ate_teto: Optional[float]
    projecao_estouro: Optional[date]
    gatilhos: list[str]
    fonte_orcamentos: float
    fonte_avulsa: float
    sinalizacao_status: str  # sem_sinalizacao | procurando | ...


class SinalizarIn(BaseModel):
    origem: str = "manual"   # manual
    gatilho: str = "manual"  # manual | teto | funcionario | ir


class SinalizacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    origem: str
    gatilho: str
    status: str
    criado_em: datetime
