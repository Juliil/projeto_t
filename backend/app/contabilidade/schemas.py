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


# ---------- Marketplace (contador ↔ estúdio) ----------
class ContadorOut(BaseModel):
    id: int
    nome: str
    crc: str
    uf_crc: str
    status_crc: str


class LeadOut(BaseModel):
    sinalizacao_id: int
    faixa_faturamento: str
    regiao: str
    segmento: str
    gatilho: str
    pct_teto: float
    criado_em: datetime
    ja_manifestei: bool


class InteresseIn(BaseModel):
    mensagem: str


class ManifestacaoEstudioOut(BaseModel):
    id: int
    contador_nome: str
    crc: str
    uf_crc: str
    status_crc: str
    mensagem_inicial: str
    status: str
    criado_em: datetime


class AceitarIn(BaseModel):
    escopo: list[str]


class VinculoEstudioOut(BaseModel):
    id: int
    contador_nome: str
    crc: str
    uf_crc: str
    escopo_dados: list[str]
    status: str
    aceito_em: datetime


class VinculoContadorOut(BaseModel):
    id: int
    estudio_nome: str
    escopo_dados: list[str]
    status: str
    aceito_em: datetime


class MensagemIn(BaseModel):
    corpo: str


class MensagemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    autor: str
    corpo: str
    criado_em: datetime
