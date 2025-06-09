from sqlalchemy import create_engine, inspect
from app.config.settings import Settings

engine = create_engine(Settings().DATABASE_URL)
inspector = inspect(engine)

tables = inspector.get_table_names()
print('Tabelas no banco de dados:')
for table in tables:
    print(f'- {table}') 