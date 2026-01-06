"""add universidad_info table with pgvector

Revision ID: 2a3b4c5d6e7f
Revises: 71f476299e00
Create Date: 2025-01-06 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = '2a3b4c5d6e7f'
down_revision: Union[str, None] = '71f476299e00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.create_table(
        'universidad_info',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, 
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('universidad_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo', sa.String(50), nullable=False),
        sa.Column('titulo', sa.String(255), nullable=False),
        sa.Column('contenido', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(768), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['universidad_id'], ['universidads.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_universidad_info_universidad_id', 'universidad_info', ['universidad_id'])
    op.create_index('ix_universidad_info_tipo', 'universidad_info', ['tipo'])

def downgrade() -> None:
    op.drop_index('ix_universidad_info_tipo', table_name='universidad_info')
    op.drop_index('ix_universidad_info_universidad_id', table_name='universidad_info')
    op.drop_table('universidad_info')
