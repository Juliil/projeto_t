from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import EMPRESA_NOME
from .db import Base, engine
from .routers import auth, materials, onboarding, pricing, store


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Garante o schema (idempotente; o init.sql já cria no 1º boot do Postgres)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Projeto T API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(materials.router)
app.include_router(pricing.router)
app.include_router(store.router)


@app.get("/")
def raiz():
    return {"app": "Projeto T", "empresa": EMPRESA_NOME, "status": "ok"}


@app.get("/api/config")
def config_publica():
    return {"empresa_nome": EMPRESA_NOME}
