# Chatbot API

API desenvolvida com FastAPI para um chatbot.

## Pré-requisitos

- Python 3.13 ou superior
- [uv](https://github.com/astral-sh/uv) (gerenciador de dependências e ambientes Python)

## Instalação do uv

### macOS / Linux
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### Verificando a instalação
```bash
uv --version
```

## Configuração do Projeto

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd chatbot-api
```

2. Instale as dependências usando o uv:
```bash
uv venv
uv pip install -r <(uv pip compile pyproject.toml)
```

> Recomenda-se usar `uv venv` para criar um ambiente virtual isolado automaticamente.

3. Ative o ambiente virtual:
- **macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows:**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

## Executando o Projeto

1. Certifique-se de que o ambiente virtual está ativado:
```bash
source .venv/bin/activate # ou .venv\Scripts\Activate.ps1 no Windows
```

2. Execute o servidor de desenvolvimento:
```bash
fastapi dev app/app.py
```

O servidor estará disponível em `http://localhost:8000`

## Documentação da API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`


## Gerenciamento de Migrações com Alembic

O projeto utiliza o Alembic para gerenciar as migrações do banco de dados. Aqui está um guia detalhado de como usar:

### Configuração Inicial

1. Certifique-se de que o arquivo `.env` está configurado corretamente com a URL do banco de dados:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatbot_db
```

2. Verifique se o banco de dados está criado e acessível:
```bash
psql -U postgres -d chatbot_db
```

### Comandos do Alembic

1. **Criar uma nova migração**:
```bash
alembic revision --autogenerate -m "descrição da migração"
```
Este comando irá gerar automaticamente uma nova migração baseada nas alterações detectadas nos modelos SQLAlchemy.

2. **Aplicar todas as migrações pendentes**:
```bash
alembic upgrade head
```
Este comando aplicará todas as migrações que ainda não foram executadas.

3. **Reverter a última migração**:
```bash
alembic downgrade -1
```
Este comando reverte a última migração aplicada.

4. **Reverter todas as migrações**:
```bash
alembic downgrade base
```
Este comando reverte todas as migrações, voltando ao estado inicial.

5. **Verificar o histórico de migrações**:
```bash
alembic history
```
Este comando mostra o histórico de todas as migrações.

6. **Verificar o estado atual**:
```bash
alembic current
```
Este comando mostra a versão atual do banco de dados.

### Boas Práticas

1. **Nomenclatura de Migrações**:
   - Use nomes descritivos para as migrações
   - Exemplo: `alembic revision --autogenerate -m "add_user_table"`

2. **Revisão de Migrações**:
   - Sempre revise o conteúdo das migrações geradas automaticamente
   - As migrações são armazenadas em `migrations/versions/`

3. **Backup**:
   - Faça backup do banco de dados antes de aplicar migrações em produção
   - Use `pg_dump` para PostgreSQL:
   ```bash
   pg_dump -U postgres chatbot_db > backup.sql
   ```

4. **Ambiente de Desenvolvimento**:
   - Teste as migrações em um ambiente de desenvolvimento antes de aplicá-las em produção
   - Use `alembic downgrade` para testar a reversão das migrações

### Solução de Problemas

1. **Erro de Conexão**:
   - Verifique se o PostgreSQL está rodando
   - Confirme se as credenciais no `.env` estão corretas
   - Teste a conexão com `psql`

2. **Erro em Migrações**:
   - Se uma migração falhar, use `alembic downgrade` para reverter
   - Verifique os logs para identificar o problema
   - Corrija o problema e gere uma nova migração

3. **Conflitos de Migração**:
   - Se houver conflitos, resolva-os manualmente
   - Use `alembic merge` para combinar migrações conflitantes


## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
