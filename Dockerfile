
FROM python:3.13-slim as builder
WORKDIR /app

RUN pip install uv

COPY pyproject.toml README.md ./

RUN pip install torch --no-cache-dir --index-url https://download.pytorch.org/whl/cpu
RUN uv pip install --system --no-cache .
RUN rm -rf /root/.cache/pip

COPY . .

FROM python:3.13-slim
WORKDIR /app

RUN useradd --create-home appuser

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/app ./app
COPY --from=builder /app/alembic.ini .
COPY --from=builder /app/migrations ./migrations

USER appuser

EXPOSE 8080

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
