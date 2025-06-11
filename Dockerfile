# --- Estágio 1: Builder ---
FROM python:3.13-slim as builder
WORKDIR /app

# Instala 'uv' para gerenciamento de dependências mais rápido
RUN pip install uv

# Copia os arquivos de metadados necessários para o build
COPY pyproject.toml README.md ./

RUN pip install torch --no-cache-dir --index-url https://download.pytorch.org/whl/cpu

# 2. Instala o restante das dependências do projeto.
RUN uv pip install --system --no-cache .

# 3. Limpa o cache do pip para garantir uma imagem final menor.
RUN rm -rf /root/.cache/pip

# Copia o restante da aplicação
COPY . .

# --- Estágio 2: Final ---
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
COPY --from=builder /app/entrypoint.sh .

# 3. Altera a permissão do script (ainda como root)
RUN chmod +x ./entrypoint.sh

# 4. Troca para o usuário não-root
USER appuser

# 5. Define o script de entrada como o ponto de partida do container.
#    O script agora contém toda a lógica de inicialização.
ENTRYPOINT ["./entrypoint.sh"]

# A porta 8000 é exposta, mas o Railway usará a variável $PORT dinamicamente.
EXPOSE 8000
