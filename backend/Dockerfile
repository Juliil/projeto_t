FROM python:3.12-slim

WORKDIR /code

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Deps de produção (imagem enxuta; deps de teste instaladas sob demanda)
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Migrations (Alembic é o dono do schema), código e testes
COPY alembic.ini pytest.ini ./
COPY alembic ./alembic
COPY app ./app
COPY tests ./tests
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

EXPOSE 8000
# Aplica migrations e sobe a API
CMD ["./entrypoint.sh"]
