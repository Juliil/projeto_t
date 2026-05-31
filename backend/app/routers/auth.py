from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..contabilidade.models import Contador
from ..db import get_db
from ..models import Usuario
from ..schemas import LoginIn, PreRegistro, TokenOut, UsuarioOut
from ..security import criar_token, get_current_user, hash_senha, verifica_senha

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _validar_crc_simulado(crc: str) -> str:
    """Validação SIMULADA de CRC (PoC). Aceita qualquer CRC não-vazio como ativo.
    # FISCAL/COMPLIANCE: trocar por integração real com CFC/CRC antes de produção."""
    return "ativo" if crc and crc.strip() else "invalido"


@router.post("/pre-registro", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def pre_registro(dados: PreRegistro, db: Session = Depends(get_db)):
    existe = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if existe:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    if dados.tipo not in ("estudio", "contador"):
        raise HTTPException(status_code=400, detail="tipo deve ser 'estudio' ou 'contador'")

    eh_contador = dados.tipo == "contador"
    if eh_contador and not (dados.crc and dados.crc.strip()):
        raise HTTPException(status_code=400, detail="CRC é obrigatório para contador")

    usuario = Usuario(
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        nome=dados.nome,
        tipo=dados.tipo,
        # contador não passa pelo onboarding do tatuador → já entra ativo
        status="ativo" if eh_contador else "pre_registro",
        perfil={},
    )
    db.add(usuario)
    db.flush()

    if eh_contador:
        db.add(Contador(
            usuario_id=usuario.id,
            crc=dados.crc.strip(),
            uf_crc=(dados.uf_crc or "").strip().upper(),
            status_crc=_validar_crc_simulado(dados.crc),
        ))

    db.commit()
    db.refresh(usuario)
    return TokenOut(access_token=criar_token(usuario.id), status=usuario.status, tipo=usuario.tipo)


@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not usuario or not verifica_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    return TokenOut(access_token=criar_token(usuario.id), status=usuario.status, tipo=usuario.tipo)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario
