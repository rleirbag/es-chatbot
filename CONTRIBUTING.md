# Guia de Contribuição

## Estrutura do Projeto

O projeto segue uma arquitetura em camadas bem definida, utilizando FastAPI como framework web e SQLAlchemy como ORM. Abaixo está a estrutura detalhada:

```
app/
├── config/                 # Configurações do projeto
│   ├── database.py        # Configuração do banco de dados e funções CRUD
│   └── settings.py        # Configurações gerais (variáveis de ambiente)
├── models/                # Modelos SQLAlchemy
│   └── user.py           # Modelo de usuário
├── schemas/              # Schemas Pydantic
│   ├── error.py         # Schema de erro
│   └── user.py          # Schemas de usuário
├── services/            # Lógica de negócio
│   └── users/          # Serviços relacionados a usuários
│       └── create_user_use_case.py  # Caso de uso de criação de usuário
└── router.py           # Rotas da API
```

## Gerenciamento de Sessão do Banco de Dados

O projeto utiliza SQLAlchemy para gerenciar as sessões do banco de dados. A configuração principal está em `app/config/database.py`:

1. **Configuração da Conexão**:
   ```python
   engine = create_engine(Settings().DATABASE_URL)
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   ```

2. **Gerenciamento de Sessão**:
   - A sessão é injetada via FastAPI usando `Depends`
   - O decorator `@commit` é usado para gerenciar transações
   - A sessão é configurada para não fazer commit automático (`autocommit=False`)

3. **Fluxo de Transação**:
   ```python
   @commit
   def execute(db: Session, ...):
       # Operações no banco
       # O decorator @commit faz o commit automaticamente
   ```

## Como Criar um CRUD

Para criar um novo CRUD, siga os passos abaixo:

1. **Criar o Modelo**:
   ```python
   # app/models/seu_modelo.py
   from app.config.database import Base
   from sqlalchemy import Column, Integer, String

   class SeuModelo(Base):
       __tablename__ = "seu_modelo"
       id = Column(Integer, primary_key=True)
       nome = Column(String)
   ```

2. **Criar os Schemas**:
   ```python
   # app/schemas/seu_modelo.py
   from pydantic import BaseModel

   class SeuModeloCreate(BaseModel):
       nome: str

   class SeuModeloResponse(BaseModel):
       id: int
       nome: str
   ```

3. **Criar o Caso de Uso**:
   ```python
   # app/services/seu_modelo/create_seu_modelo_use_case.py
   from app.config.database import commit, create
   from app.models.seu_modelo import SeuModelo
   from app.schemas.seu_modelo import SeuModeloCreate

   class CreateSeuModeloUseCase:
       @staticmethod
       @commit
       def execute(db: Session, data: SeuModeloCreate):
           modelo = SeuModelo(**data.model_dump())
           return create(db, modelo)
   ```

4. **Criar a Rota**:
   ```python
   # app/router.py
   from fastapi import APIRouter, Depends
   from app.services.seu_modelo.create_seu_modelo_use_case import CreateSeuModeloUseCase

   router = APIRouter()

   @router.post("/seu-modelo")
   def create_seu_modelo(
       data: SeuModeloCreate,
       db: Session = Depends(get_db)
   ):
       return CreateSeuModeloUseCase.execute(db, data)
   ```

## Funções CRUD Disponíveis

O projeto já possui funções CRUD genéricas em `app/config/database.py`:

1. **Create**:
   ```python
   def create(session: Session, model: SqlAlchemyModel) -> Tuple[Optional[SqlAlchemyModel], Optional[Error]]
   ```

2. **Read**:
   ```python
   def get_by_attribute(session: Session, model: Type[SqlAlchemyModel], attribute_name: str, attribute_value: Any) -> Tuple[Optional[SqlAlchemyModel], Optional[Error]]
   ```

3. **Update**:
   ```python
   def update(session: Session, model: Type[SqlAlchemyModel], id: int, **kwargs) -> Optional[Error]
   ```

4. **Delete**:
   ```python
   def delete(session: Session, model: Type[SqlAlchemyModel], id: int) -> Optional[Error]
   ```

## Tratamento de Erros

O projeto possui um sistema robusto de tratamento de erros:

1. **Schema de Erro**:
   ```python
   class Error(BaseModel):
       error_code: int
       error_message: str
   ```

2. **Função de Tratamento**:
   ```python
   def handle_db_error(session: Session, model: Type[SqlAlchemyModel], exception: Exception) -> Error
   ```

## Boas Práticas

1. **Sempre use o decorator @commit** para operações que modificam o banco
2. **Trate erros adequadamente** usando o sistema de Error
3. **Use schemas Pydantic** para validação de dados
4. **Mantenha a separação de responsabilidades** entre modelos, schemas e casos de uso
5. **Documente suas funções** usando docstrings

## Exemplo Completo

Aqui está um exemplo completo de como criar um CRUD para uma entidade "Produto":

1. **Modelo**:
   ```python
   # app/models/produto.py
   from app.config.database import Base
   from sqlalchemy import Column, Integer, String, Float

   class Produto(Base):
       __tablename__ = "produtos"
       id = Column(Integer, primary_key=True)
       nome = Column(String)
       preco = Column(Float)
   ```

2. **Schemas**:
   ```python
   # app/schemas/produto.py
   from pydantic import BaseModel

   class ProdutoCreate(BaseModel):
       nome: str
       preco: float

   class ProdutoResponse(BaseModel):
       id: int
       nome: str
       preco: float
   ```

3. **Caso de Uso**:
   ```python
   # app/services/produtos/create_produto_use_case.py
   from app.config.database import commit, create
   from app.models.produto import Produto
   from app.schemas.produto import ProdutoCreate

   class CreateProdutoUseCase:
       @staticmethod
       @commit
       def execute(db: Session, data: ProdutoCreate):
           produto = Produto(**data.model_dump())
           return create(db, produto)
   ```

4. **Rota**:
   ```python
   # app/router.py
   @router.post("/produtos")
   def create_produto(
       data: ProdutoCreate,
       db: Session = Depends(get_db)
   ):
       return CreateProdutoUseCase.execute(db, data)
   ```

## Migrations

O projeto usa Alembic para gerenciar migrações do banco de dados:

1. **Criar uma nova migration**:
   ```bash
   alembic revision --autogenerate -m "descrição da migration"
   ```

2. **Aplicar migrations**:
   ```bash
   alembic upgrade head
   ```

3. **Reverter migrations**:
   ```bash
   alembic downgrade -1
   ``` 