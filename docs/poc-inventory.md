# Inventário da PoC — Projeto T

> Documento da **Fase 0** (baseline). Registra o estado atual do repositório _antes_ de qualquer evolução para a distribuidora de insumos (ZFM). Atualizado em 2026-05-30.

## 1. Visão geral

**Projeto T** é uma PoC **B2C** de painel para tatuadores individuais: cada usuário gerencia seus próprios materiais, precifica trabalhos e participa de uma loja compartilhada (preço fixo + leilão) entre pares.

> ⚠️ A proposta da **distribuidora de insumos (Norte/ZFM)** é um **novo produto B2B** sobre a mesma base técnica — não substitui esta PoC. Ver [architecture.md](architecture.md).

## 2. Stack

| Camada | Tecnologia | Versão |
|---|---|---|
| Backend | FastAPI + SQLAlchemy 2.0 (ORM) | Python 3.12 |
| Auth | JWT (PyJWT HS256) + bcrypt | token 7 dias |
| Banco | PostgreSQL | 16-alpine |
| Driver | psycopg 3 (binary) | |
| Frontend | React 18 + Vite (CSS próprio) | |
| Orquestração | Docker Compose (db, backend, frontend) | |

## 3. Modelo de dados (atual)

Schema em [`db/init.sql`](../db/init.sql). Todas as entidades de negócio são **escopadas por `usuario_id`** (modelo B2C: N usuários independentes).

| Tabela | Papel | Observações |
|---|---|---|
| `usuarios` | Conta + perfil | `status` (pre_registro/ativo), `perfil` em JSONB; **sem campo de papel/role** |
| `materiais` | Insumos do tatuador | FK `usuario_id`; `custo_unitario`, `estoque`, `unidade` |
| `orcamentos` | Precificação salva | materiais + horas + margem → `preco_final`; itens em JSONB |
| `loja_anuncios` | Marketplace P2P | `tipo` fixo/leilão; `vendedor_id`, `comprador_id` |
| `loja_ofertas` | Lances de leilão | FK `anuncio_id` |

## 4. Endpoints (atual)

| Router | Prefixo | Rotas |
|---|---|---|
| `auth` | `/api/auth` | `POST /pre-registro`, `POST /login`, `GET /me` |
| `onboarding` | `/api/onboarding` | (perfil em feed) |
| `materials` | `/api/materiais` | `GET`, `POST`, `PUT /{id}`, `DELETE /{id}` |
| `pricing` | `/api/precificacao` | calcular + salvar orçamento |
| `store` | `/api/loja` | `GET`, `POST`, `POST /{id}/oferta`, `POST /{id}/comprar` |
| (raiz) | `/`, `/api/config` | health + nome da empresa |

## 5. O que funciona

- ✅ Fluxo completo de auth (pré-registro → onboarding → login → `me`)
- ✅ CRUD de materiais (escopado por usuário, protegido por JWT)
- ✅ Precificação (cálculo + persistência)
- ✅ Loja P2P (anúncio fixo/leilão, oferta, compra)
- ✅ Frontend: login dividido, onboarding, loading, dashboard, **menu lateral recolhível** (feat. recém-mergeada)
- ✅ Sobe inteiro com `docker compose up --build` no engine WSL2

## 6. Lacunas / dívidas técnicas (relevantes para a evolução)

| Lacuna | Impacto na evolução |
|---|---|
| **Sem migrations** — schema em `init.sql` (só roda em volume vazio) + `Base.metadata.create_all()` no boot | 🔴 Bloqueador: toda fase muda o modelo. Resolvido na Fase 0 com **Alembic**. |
| **Sem testes** | 🔴 Doc exige "fase = PR com testes". Resolvido na Fase 0 (pytest). |
| **Sem CI** | 🟠 Necessário para "um PR por fase". |
| **Sem papéis/roles** | 🟠 B2B exige distinguir `distribuidora_admin` × `cliente_estudio`. |
| **Tenancy por usuário** | 🟠 Distribuidora é 1 organização + N clientes, não N usuários isolados. |
| **Nada fiscal** (NCM, ICMS, SUFRAMA, NF-e) | 🟡 Todo o núcleo da Fase 1 é novo. |
| `JWT_SECRET` default em código | 🟡 Endurecer antes de produção. |
| CORS fixo em `localhost:5173` | 🟡 Parametrizar por ambiente. |

## 7. Como rodar (referência)

```bash
cp .env.example .env
docker compose up --build
# Frontend  http://localhost:5173
# API/docs  http://localhost:8000/docs
```
