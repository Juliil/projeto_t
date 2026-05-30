from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Usuario
from ..schemas import OnboardingIn, UsuarioOut
from ..security import get_current_user

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

# Conjunto de perguntas do "feed in/out" do primeiro acesso.
PERGUNTAS = [
    {"id": "nome_estudio", "label": "Qual o nome do seu estúdio?", "tipo": "texto", "placeholder": "Ex: Black Ink Studio"},
    {"id": "cidade", "label": "Em qual cidade você atua?", "tipo": "texto", "placeholder": "Ex: Manaus"},
    {"id": "anos_experiencia", "label": "Quantos anos de experiência você tem?", "tipo": "numero", "placeholder": "Ex: 5"},
    {
        "id": "estilo_principal",
        "label": "Qual seu estilo principal?",
        "tipo": "opcao",
        "opcoes": ["Fineline", "Blackwork", "Realismo", "Old School", "Aquarela", "Geométrico", "Outro"],
    },
    {
        "id": "valor_hora",
        "label": "Quanto você cobra por hora hoje? (R$)",
        "tipo": "numero",
        "placeholder": "Ex: 150",
    },
    {
        "id": "objetivo",
        "label": "O que você mais quer organizar primeiro?",
        "tipo": "opcao",
        "opcoes": ["Precificação", "Controle de materiais", "Vender materiais", "Tudo isso"],
    },
]


@router.get("/perguntas")
def perguntas():
    return {"perguntas": PERGUNTAS}


@router.post("/concluir", response_model=UsuarioOut)
def concluir(
    dados: OnboardingIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    usuario.perfil = {**(usuario.perfil or {}), **dados.perfil}
    usuario.status = "ativo"
    db.commit()
    db.refresh(usuario)
    return usuario
