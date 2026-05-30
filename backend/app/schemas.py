from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth / Usuário ----------
class PreRegistro(BaseModel):
    email: EmailStr
    senha: str
    nome: str


class LoginIn(BaseModel):
    email: EmailStr
    senha: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    status: str


class OnboardingIn(BaseModel):
    perfil: dict[str, Any]


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    nome: str
    status: str
    perfil: dict[str, Any]


# ---------- Materiais ----------
class MaterialIn(BaseModel):
    nome: str
    categoria: Optional[str] = None
    unidade: str = "un"
    custo_unitario: float = 0
    estoque: float = 0
    estoque_minimo: float = 0


class MaterialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    categoria: Optional[str]
    unidade: str
    custo_unitario: float
    estoque: float
    estoque_minimo: float


# ---------- Precificação ----------
class ItemOrcamento(BaseModel):
    material_id: int
    quantidade: float


class CalcularIn(BaseModel):
    titulo: str = "Orçamento"
    itens: list[ItemOrcamento] = []
    horas: float = 0
    valor_hora: float = 0
    margem_pct: float = 0


class ItemCalculado(BaseModel):
    material_id: int
    nome: str
    quantidade: float
    custo_unitario: float
    subtotal: float


class OrcamentoOut(BaseModel):
    titulo: str
    itens: list[ItemCalculado]
    custo_materiais: float
    custo_mao_obra: float
    margem_pct: float
    preco_final: float


class OrcamentoSalvoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    preco_final: float
    status: str
    criado_em: datetime


class OrcamentoDetalheOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    status: str
    horas: float
    valor_hora: float
    margem_pct: float
    custo_materiais: float
    custo_mao_obra: float
    preco_final: float
    itens: list[dict[str, Any]]
    aceito_em: Optional[datetime] = None
    agendado_em: Optional[date] = None
    criado_em: datetime


class StatusOrcamentoIn(BaseModel):
    status: str  # pendente | aceito | reprovado


class AgendaIn(BaseModel):
    data: Optional[date] = None  # null remove o agendamento


# ---------- Estoque (ledger) ----------
class MovimentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    material_id: Optional[int]
    material_nome: str
    tipo: str
    quantidade: float
    saldo_apos: float
    origem: str
    orcamento_id: Optional[int]
    criado_em: datetime


# ---------- Loja ----------
class AnuncioIn(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    tipo: str = "fixo"  # fixo | leilao
    preco: float = 0
    material_id: Optional[int] = None


class OfertaIn(BaseModel):
    valor: float


class AnuncioOut(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    tipo: str
    preco: float
    preco_atual: float
    status: str
    vendedor: str
    sou_dono: bool
    total_ofertas: int
    criado_em: datetime
