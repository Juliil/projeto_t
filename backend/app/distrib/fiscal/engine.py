"""Motor de cálculo fiscal da entrada na ZFM.

Resolve a regra aplicável (parametrizada, versionada por vigência) e calcula
a desoneração que reduz o custo de aquisição — o principal driver de margem.

# FISCAL: alíquotas/enquadramentos são premissas; validar com contador.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import FiscalNCM, FiscalRegra

CENTAVOS = Decimal("0.01")
DISCLAIMER = (
    "Cálculo baseado em parâmetros configuráveis (premissa de modelagem). "
    "Validar enquadramento, alíquota e CFOP/CST com contador antes de operar."
)


class FiscalError(Exception):
    """Erro de negócio do motor fiscal (NCM ausente, sem regra vigente, etc.)."""


@dataclass
class ResultadoEntrada:
    ncm: str
    descricao_ncm: str
    origem: str
    data_referencia: date
    elegivel: bool
    regime: Optional[str]
    base_legal: Optional[str]
    aliquota: Decimal
    valor_bruto: Decimal
    valor_desonerado: Decimal       # quanto de imposto foi desonerado (desconto)
    custo_liquido: Decimal          # valor_bruto - desonerado
    vigencia_inicio: Optional[date]
    vigencia_fim: Optional[date]
    observacao: str
    disclaimer: str = DISCLAIMER


def _q(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def _resolver_regra(
    db: Session, operacao: str, origem: str, data_ref: date, regime: Optional[str], uf: str = "AM"
) -> Optional[FiscalRegra]:
    q = (
        db.query(FiscalRegra)
        .filter(FiscalRegra.operacao == operacao)
        .filter(FiscalRegra.uf == uf)
        .filter(FiscalRegra.origem.in_([origem, "ambos"]))
        .filter(FiscalRegra.vigencia_inicio <= data_ref)
        .filter(or_(FiscalRegra.vigencia_fim.is_(None), FiscalRegra.vigencia_fim >= data_ref))
    )
    if regime:
        q = q.filter(FiscalRegra.regime == regime)
    # Em coexistência (ICMS x IBS/CBS), sem regime explícito, vale a regra de
    # vigência mais recente aplicável à data.
    return q.order_by(FiscalRegra.vigencia_inicio.desc()).first()


def simular_entrada(
    db: Session,
    ncm_codigo: str,
    valor: float | Decimal,
    origem: str = "nacional",
    data_ref: Optional[date] = None,
    regime: Optional[str] = None,
) -> ResultadoEntrada:
    data_ref = data_ref or date.today()
    valor_bruto = _q(Decimal(str(valor)))

    ncm = db.query(FiscalNCM).filter(FiscalNCM.codigo == ncm_codigo).first()
    if ncm is None:
        raise FiscalError(f"NCM {ncm_codigo} não cadastrado.")

    if not ncm.elegivel_zfm or ncm.excluido_beneficio:
        return ResultadoEntrada(
            ncm=ncm.codigo, descricao_ncm=ncm.descricao, origem=origem,
            data_referencia=data_ref, elegivel=False, regime=None, base_legal=None,
            aliquota=Decimal("0"), valor_bruto=valor_bruto, valor_desonerado=Decimal("0.00"),
            custo_liquido=valor_bruto, vigencia_inicio=None, vigencia_fim=None,
            observacao="NCM sem direito ao benefício ZFM — custo integral.",
        )

    regra = _resolver_regra(db, "entrada_zfm", origem, data_ref, regime)
    if regra is None:
        raise FiscalError(
            f"Sem regra fiscal vigente para entrada_zfm/{origem} em {data_ref.isoformat()}"
            + (f" no regime {regime}." if regime else ".")
        )

    valor_imposto = _q(valor_bruto * regra.aliquota)
    desonerado = valor_imposto if regra.aplica_desoneracao else Decimal("0.00")
    custo_liquido = _q(valor_bruto - desonerado)

    obs = (
        f"{regra.regime}: alíquota {regra.aliquota:.2%} "
        + ("desonerada como desconto na aquisição." if regra.aplica_desoneracao
           else "informativa (sem desoneração).")
    )
    return ResultadoEntrada(
        ncm=ncm.codigo, descricao_ncm=ncm.descricao, origem=origem,
        data_referencia=data_ref, elegivel=True, regime=regra.regime,
        base_legal=regra.base_legal, aliquota=regra.aliquota, valor_bruto=valor_bruto,
        valor_desonerado=desonerado, custo_liquido=custo_liquido,
        vigencia_inicio=regra.vigencia_inicio, vigencia_fim=regra.vigencia_fim,
        observacao=obs,
    )
