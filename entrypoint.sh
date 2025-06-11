#!/bin/bash

# Para o script se qualquer comando falhar
set -e

# Executa as migrações do Alembic
echo "Running database migrations..."
alembic upgrade head

# Executa o comando principal da aplicação (passado como argumentos para este script)
# O 'exec "$@"' substitui o processo do shell pelo processo da aplicação,
# o que é uma boa prática para o Docker.
exec "$@"