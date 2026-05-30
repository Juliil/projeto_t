import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://projetot:projetot@localhost:5432/projetot",
)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-trocar")
JWT_ALG = "HS256"
JWT_EXPIRA_HORAS = 24 * 7  # 7 dias
EMPRESA_NOME = os.getenv("EMPRESA_NOME", "Projeto T")
