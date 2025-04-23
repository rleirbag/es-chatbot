# Chatbot API

API desenvolvida com FastAPI para um chatbot.

## Pré-requisitos

- Python 3.13 ou superior
- pip (gerenciador de pacotes Python)

## Instalação do Poetry

### macOS / Linux
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Windows (PowerShell)
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### Verificando a instalação
```bash
poetry --version
```

## Configuração do Projeto

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd chatbot-api
```

2. Instale as dependências usando o Poetry:
```bash
poetry install
```

3. Ative o ambiente virtual:
```bash
poetry shell
```

## Executando o Projeto

1. Certifique-se de que o ambiente virtual está ativado:
```bash
poetry shell
```

2. Execute o servidor de desenvolvimento:
```bash
uvicorn app.main:app --reload
```

O servidor estará disponível em `http://localhost:8000`

## Documentação da API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`


## Comandos Úteis

- Instalar uma nova dependência:
```bash
poetry add [nome-do-pacote]
```

- Atualizar dependências:
```bash
poetry update
```

- Executar testes:
```bash
task test
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
