"""Fixtures de teste.

Os modelos usam JSONB/Numeric (Postgres-only), então testamos contra um
banco Postgres real (`projetot_test`), criado automaticamente no mesmo
servidor do DATABASE_URL. Cada teste roda numa transação revertida ao final.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL
from app.db import Base, get_db
from app.main import app
from app import models  # noqa: F401  (registra tabelas no metadata)

_base_url = make_url(DATABASE_URL)
TEST_DB = "projetot_test"
TEST_URL = _base_url.set(database=TEST_DB)
ADMIN_URL = _base_url.set(database="postgres")


@pytest.fixture(scope="session")
def engine():
    # Cria o banco de teste se não existir (CREATE DATABASE exige autocommit)
    admin = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        existe = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": TEST_DB}
        ).scalar()
        if not existe:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB}"'))
    admin.dispose()

    eng = create_engine(TEST_URL, pool_pre_ping=True)
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    trans = connection.begin()
    Session = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Registra um usuário e devolve o header Authorization Bearer."""
    r = client.post(
        "/api/auth/pre-registro",
        json={"email": "teste@projetot.dev", "senha": "senha123", "nome": "Teste"},
    )
    assert r.status_code == 201, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
