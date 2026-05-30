from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Usuario
from ..schemas import LoginIn, PreRegistro, TokenOut, UsuarioOut
from ..security import criar_token, get_current_user, hash_senha, verifica_senha

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/pre-registro", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def pre_registro(dados: PreRegistro, db: Session = Depends(get_db)):
    existe = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if existe:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    usuario = Usuario(
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        nome=dados.nome,
        status="pre_registro",
        perfil={},
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return TokenOut(access_token=criar_token(usuario.id), status=usuario.status)


@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not usuario or not verifica_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    return TokenOut(access_token=criar_token(usuario.id), status=usuario.status)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario
