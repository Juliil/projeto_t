from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NCMOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo: str
    descricao: str
    elegivel_zfm: bool
    excluido_beneficio: bool


class SimularEntradaIn(BaseModel):
    ncm: str = Field(..., examples=["9018.32.19"])
    valor: float = Field(..., gt=0, examples=[1000.0])
    origem: str = Field("nacional", examples=["nacional", "importado"])
    data_ref: Optional[date] = Field(None, description="Data da operação (default: hoje)")
    regime: Optional[str] = Field(None, examples=["ICMS", "IBS_CBS"])


class SimularEntradaOut(BaseModel):
    ncm: str
    descricao_ncm: str
    origem: str
    data_referencia: date
    elegivel: bool
    regime: Optional[str]
    base_legal: Optional[str]
    aliquota: float
    valor_bruto: float
    valor_desonerado: float
    custo_liquido: float
    vigencia_inicio: Optional[date]
    vigencia_fim: Optional[date]
    observacao: str
    disclaimer: str
