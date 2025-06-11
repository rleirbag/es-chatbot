#!/bin/bash

set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting Uvicorn server on port ${PORT:-8000}..."
exec uvicorn app.app:app --host 0.0.0.0 --port ${PORT:-8000#!/bin/bash

# Para o script se qualquer comando falhar
set -e

echo "--- Iniciando o script de entrada (entrypoint.sh) ---"

# 1. Verifica e loga a variável de ambiente PORT
if [ -z "$PORT" ]; then
  echo "AVISO: A variável de ambiente PORT não foi definida. Usando a porta padrão 8000."
  # Define a porta padrão caso a variável não exista
  PORT=8000
else
  echo "INFO: A variável de ambiente PORT foi encontrada. Usando a porta: $PORT"
fi

# 2. Executa as migrações do Alembic
echo "INFO: Executando as migrações do banco de dados..."
alembic upgrade head
echo "INFO: Migrações do banco de dados concluídas."

# 3. Inicia o servidor Uvicorn na porta definida
echo "INFO: Iniciando o servidor Uvicorn em http://0.0.0.0:$PORT"
exec uvicorn app.app:app --host 0.0.0.0 --port "$PORT"
}