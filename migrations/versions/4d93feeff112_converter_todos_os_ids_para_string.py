"""converter todos os ids para string

Revision ID: 4d93feeff112
Revises: 51ced48f7839
Create Date: 2024-03-27 11:11:11.111111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d93feeff112'
down_revision: Union[str, None] = '51ced48f7839'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Primeiro remove a sequência do id
    op.execute('ALTER TABLE users ALTER COLUMN id DROP DEFAULT')
    op.execute('DROP SEQUENCE IF EXISTS users_id_seq')
    
    # Remove as foreign keys existentes
    op.drop_constraint('documents_user_id_fkey', 'documents', type_='foreignkey')
    op.drop_constraint('chat_histories_user_id_fkey', 'chat_histories', type_='foreignkey')
    
    # Altera o tipo da coluna id na tabela users
    op.execute('ALTER TABLE users ALTER COLUMN id TYPE VARCHAR USING id::text')
    
    # Altera o tipo da coluna user_id na tabela documents
    op.execute('ALTER TABLE documents ALTER COLUMN user_id TYPE VARCHAR USING user_id::text')
    
    # Altera o tipo da coluna user_id na tabela chat_histories
    op.execute('ALTER TABLE chat_histories ALTER COLUMN user_id TYPE VARCHAR USING user_id::text')
    
    # Recria as foreign keys com os novos tipos
    op.create_foreign_key('documents_user_id_fkey', 
        'documents', 'users',
        ['user_id'], ['id'])
    op.create_foreign_key('chat_histories_user_id_fkey', 
        'chat_histories', 'users',
        ['user_id'], ['id'])


def downgrade() -> None:
    # Remove as foreign keys
    op.drop_constraint('documents_user_id_fkey', 'documents', type_='foreignkey')
    op.drop_constraint('chat_histories_user_id_fkey', 'chat_histories', type_='foreignkey')
    
    # Cria a sequência novamente
    op.execute('CREATE SEQUENCE users_id_seq')
    
    # Reverte o tipo da coluna user_id na tabela documents
    op.execute('ALTER TABLE documents ALTER COLUMN user_id TYPE INTEGER USING user_id::integer')
    
    # Reverte o tipo da coluna user_id na tabela chat_histories
    op.execute('ALTER TABLE chat_histories ALTER COLUMN user_id TYPE INTEGER USING user_id::integer')
    
    # Reverte o tipo da coluna id na tabela users
    op.execute('ALTER TABLE users ALTER COLUMN id TYPE INTEGER USING id::integer')
    op.execute('ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval(\'users_id_seq\')')
    
    # Recria as foreign keys com os tipos originais
    op.create_foreign_key('documents_user_id_fkey', 
        'documents', 'users',
        ['user_id'], ['id'])
    op.create_foreign_key('chat_histories_user_id_fkey', 
        'chat_histories', 'users',
        ['user_id'], ['id'])
