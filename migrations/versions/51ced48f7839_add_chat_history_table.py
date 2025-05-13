"""add chat history table

Revision ID: 51ced48f7839
Revises: 918426f880fa
Create Date: 2025-05-13 00:41:05.708889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51ced48f7839'
down_revision: Union[str, None] = '918426f880fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Primeiro removemos a foreign key existente
    op.drop_constraint('documents_user_id_fkey', 'documents', type_='foreignkey')
    
    # Depois alteramos os tipos de ID para String
    op.alter_column('users', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('users_id_seq'::regclass)"))
    
    op.alter_column('documents', 'user_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
    
    # Recriamos a foreign key do documents com o novo tipo
    op.create_foreign_key(
        'documents_user_id_fkey',
        'documents', 'users',
        ['user_id'], ['id']
    )
    
    # Por fim, criamos a tabela chat_histories
    op.create_table('chat_histories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_histories_id'), 'chat_histories', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Primeiro removemos a tabela chat_histories
    op.drop_index(op.f('ix_chat_histories_id'), table_name='chat_histories')
    op.drop_table('chat_histories')
    
    # Removemos a foreign key do documents
    op.drop_constraint('documents_user_id_fkey', 'documents', type_='foreignkey')
    
    # Revertemos os tipos de ID para Integer
    op.alter_column('documents', 'user_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)
               
    op.alter_column('users', 'id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('users_id_seq'::regclass)"))
               
    # Recriamos a foreign key do documents com o tipo antigo
    op.create_foreign_key(
        'documents_user_id_fkey',
        'documents', 'users',
        ['user_id'], ['id']
    )
