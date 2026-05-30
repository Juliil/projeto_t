# Projeto T — POC

Painel nichado para tatuadores: cadastro de materiais, precificação de trabalhos e uma loja compartilhada (preço fixo + leilão). Tudo em Docker, com Postgres interno.

> **Você está na Parte 1** — a fundação que sobe e roda: login + primeiro acesso, onboarding em feed, tela de loading *"estamos riscando"* e o painel principal (estilo 2026). Materiais, Precificação e Loja entram nas Partes 2–4 (o backend delas já está incluído).

## Stack

- **Backend**: FastAPI + SQLAlchemy + JWT
- **Banco**: PostgreSQL 16 (interno, schema em `db/init.sql`)
- **Frontend**: React 18 + Vite (CSS próprio, fontes Bricolage Grotesque + Schibsted Grotesk)
- **Orquestração**: Docker Compose

## Como rodar

```bash
cp .env.example .env        # opcional: ajuste segredos e EMPRESA_NOME
docker compose up --build
```

| Serviço   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:5173        |
| API       | http://localhost:8000        |
| API docs  | http://localhost:8000/docs   |
| Postgres  | localhost:5432               |

## Fluxo desta parte

1. Tela de **login dividida**: à esquerda o benchmark *Projeto T*, a frase de impacto e a máquina de tatuar em sketch; à direita as abas **Primeiro acesso** e **Login**.
2. **Primeiro acesso** → pré-cadastro (nome, e-mail, senha) → onboarding com perguntas em feed (estúdio, cidade, experiência, estilo, valor/hora, objetivo).
3. Loading **"estamos riscando"** → **"Bem-vindo a Projeto T"**.
4. **Painel principal** com sidebar, topo com símbolo/avatar e a Home com atalhos e indicadores.

## Estrutura

```
projeto-t/
├── docker-compose.yml
├── .env.example
├── db/init.sql              # schema do Postgres
├── backend/                 # FastAPI (auth, onboarding, materiais, precificação, loja)
│   └── app/
│       ├── main.py  config.py  db.py  models.py  schemas.py  security.py
│       └── routers/
└── frontend/                # React + Vite
    └── src/
        ├── App.jsx  main.jsx  api.js  styles.css
        ├── context/AuthContext.jsx
        ├── components/   (Sidebar, Loading, TattooMachine, Icons)
        └── pages/        (Login, Onboarding, Dashboard)
```

## Próximas partes

- **Parte 2** — Materiais (CRUD completo, base de custo)
- **Parte 3** — Precificação (materiais + horas + margem → preço sugerido, orçamentos salvos)
- **Parte 4** — Loja compartilhada (anunciar, comprar a preço fixo, dar lances no leilão)
