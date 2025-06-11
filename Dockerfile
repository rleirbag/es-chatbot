# --- Estágio 1: Builder ---
# Usa uma imagem "slim" que é menor que a padrão.
FROM python:3.13-slim as builder
WORKDIR /app

# Instala 'uv' para gerenciamento de dependências mais rápido
RUN pip install uv

# Copia os arquivos de metadados necessários para o build
COPY pyproject.toml README.md ./

# Instala a versão CPU-only do PyTorch para reduzir o tamanho
RUN pip install torch --no-cache-dir --index-url https://download.pytorch.org/whl/cpu
# Instala o restante das dependências
RUN uv pip install --system --no-cache .
# Limpa o cache para garantir uma imagem final menor
RUN rm -rf /root/.cache/pip

# Copia o restante da aplicação
COPY . .

# --- Estágio 2: Final ---
# Começa de novo com a mesma imagem base limpa
FROM python:3.13-slim
WORKDIR /app

# 1. Cria um usuário não-root por segurança
RUN useradd --create-home appuser

# 2. Copia os arquivos da aplicação e dependências (ainda como root)
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/app ./app
COPY --from=builder /app/alembic.ini .
COPY --from=builder /app/migrations ./migrations

# 3. Troca para o usuário não-root
USER appuser

# Expõe a porta para o Railway
EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && fastapi dev app/app.py"]
