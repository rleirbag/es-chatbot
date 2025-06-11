# --- Estágio 1: Builder ---
FROM python:3.13-slim as builder
WORKDIR /app

RUN pip install uv

COPY pyproject.toml README.md ./

RUN uv pip install --system --no-cache .

# Copia o restante da aplicação
COPY . .

# --- Estágio 2: Final ---
FROM python:3.13-slim
WORKDIR /app

RUN useradd --create-home appuser

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/app ./app
COPY --from=builder /app/alembic.ini .
COPY --from=builder /app/migrations ./migrations
COPY --from=builder /app/entrypoint.sh .

RUN chmod +x ./entrypoint.sh

USER appuser

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 8000