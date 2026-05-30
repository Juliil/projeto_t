# Arquitetura — Estado atual e estado-alvo

> Documento da **Fase 0**. Define como a **distribuidora de insumos (ZFM)** coexiste com a PoC **Projeto T (B2C)** na mesma base, e o caminho de evolução. Premissas fiscais ver [proposta](../proposta-distribuidora-insumos-faseamento.md) e **validar com contador antes de produção**.

## 1. Decisão estratégica

A distribuidora B2B é um **novo módulo/produto sobre a mesma stack**, não uma reescrita. Projeto T (B2C) continua vivo. Isso exige **separação de domínios** clara desde já.

```
Projeto T (B2C)                Distribuidora (B2B)
─────────────────              ────────────────────
tatuador individual            1 distribuidora + N estúdios clientes
materiais / precificação       SKU / estoque multi-local / compras
loja P2P (leilão)              motor fiscal ZFM / NF-e / portal B2B
```

## 2. Separação de domínios (alvo)

Backend organizado por **bounded context**, compartilhando só infra (db, auth, config):

```
backend/app/
├── core/            # infra compartilhada: db, config, security/JWT
├── b2c/             # domínio Projeto T (move-se: materials, pricing, store, onboarding)
│   ├── models.py  routers/  schemas.py
└── distrib/         # domínio distribuidora (NOVO, cresce por fase)
    ├── fiscal/      # FASE 1 — motor fiscal isolado, parametrizável, versionado por vigência
    ├── catalogo/    # FASE 2 — SKU, NCM, canal
    ├── estoque/     # FASE 2 — multi-local
    ├── compras/     # FASE 2 — reposição, AP/AR
    ├── portal/      # FASE 3 — B2B self-service
    └── inteligencia/# FASE 4 — previsão, ABC, CRM
```

> A migração da estrutura atual (`app/routers/*` plano) para `b2c/` é **incremental** e pode ser feita junto da Fase 2, para não inflar a Fase 0. A Fase 0 só prepara fundação (migrations + testes), **sem mudança funcional**.

## 3. Tenancy e papéis (alvo)

- Introduzir `usuarios.role` (`tatuador` | `distribuidora_admin` | `cliente_estudio`) — **migration futura**, não na Fase 0.
- Entidades B2B pertencem à **organização distribuidora**, não a um usuário. Clientes (estúdios) referenciam a org.
- Validação **SUFRAMA** do cliente vive no domínio `distrib` (Fase 1/3).

## 4. Ownership do schema — decisão da Fase 0

**Problema:** hoje três mecanismos criam tabelas → `db/init.sql` (1º boot), `Base.metadata.create_all()` no startup, e (novo) Alembic.

**Decisão:** **Alembic passa a ser o dono único.**
- `Base.metadata.create_all()` removido do startup ([main.py](../backend/app/main.py)).
- `db/init.sql` deixa de criar tabelas (aposentado; mantido só como histórico/seed opcional).
- Container backend roda `alembic upgrade head` antes do uvicorn.
- Migration baseline `0001` reproduz o schema atual da PoC.

```
Fresh env : alembic upgrade head  → cria tudo
Env existente: alembic stamp head  → marca baseline sem recriar
```

## 5. Motor fiscal — princípios (Fase 1, registrados desde já)

- **Isolado** em `distrib/fiscal/`, **parametrizável** e **versionado por vigência** (tabelas/seed em banco), **nunca hardcoded**.
- Cada parâmetro tributário marcado com `# FISCAL: validar com contador`.
- Suportar **coexistência ICMS ↔ IBS/CBS** (transição LC 214/2025), selecionável por data de vigência.
- **NF-e**: integrar emissor terceiro (Focus NFe / NFe.io) em sandbox; **não** implementar emissor próprio.
- Modelar ciclo de **internamento SUFRAMA** (SIMNAC → PIN → TCIF), prazo de comprovação e **risco de estorno**.

## 6. Testes (Fase 0)

- `pytest` + cliente HTTP (Starlette `TestClient`).
- DB de teste em Postgres (`projetot_test`) — modelos usam `JSONB`/`Numeric`, então SQLite não serve.
- Override de `get_db` + rollback por teste.
- Cobertura mínima inicial: health, fluxo de auth, CRUD de materiais autenticado. Cada fase seguinte adiciona seus testes (regra: **fase = PR com testes**).

## 7. Não-objetivos (reforço da proposta)

- Não emitir NF-e próprio; não reescrever a PoC; não tratar regra fiscal como definitiva sem validação contábil; não adicionar serviços pesados que quebrem o caráter *asset-light*.
