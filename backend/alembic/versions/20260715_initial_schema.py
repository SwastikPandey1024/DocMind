"""Initial schema for OCR document chat system

Revision ID: 20260715_initial
Revises: 
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260715_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=500), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table(
        'documents',
        sa.Column('document_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(length=500), nullable=False),
        sa.Column('file_path', sa.String(length=1000), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'),
        sa.Column('total_pages', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('document_id')
    )
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)
    op.create_index(op.f('ix_documents_status'), 'documents', ['status'], unique=False)

    op.create_table(
        'ocr_text',
        sa.Column('text_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('clean_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('text_id')
    )
    op.create_index(op.f('ix_ocr_text_document_id'), 'ocr_text', ['document_id'], unique=False)

    op.create_table(
        'embedding_metadata',
        sa.Column('embedding_key', sa.String(length=255), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('dimension', sa.Integer(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('embedding_key')
    )
    op.create_index(op.f('ix_embedding_metadata_model_name'), 'embedding_metadata', ['model_name'], unique=False)

    op.create_table(
        'chunks',
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding_key', sa.String(length=255), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['embedding_key'], ['embedding_metadata.embedding_key']),
        sa.PrimaryKeyConstraint('chunk_id')
    )
    op.create_index(op.f('ix_chunks_document_id'), 'chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_chunks_chunk_index'), 'chunks', ['chunk_index'], unique=False)
    op.create_index(op.f('ix_chunks_embedding_key'), 'chunks', ['embedding_key'], unique=False)

    op.create_table(
        'chat_history',
        sa.Column('chat_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('chat_id')
    )
    op.create_index(op.f('ix_chat_history_user_id'), 'chat_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_chat_history_document_id'), 'chat_history', ['document_id'], unique=False)
    op.create_index(op.f('ix_chat_history_created_at'), 'chat_history', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_chat_history_created_at'), table_name='chat_history')
    op.drop_index(op.f('ix_chat_history_document_id'), table_name='chat_history')
    op.drop_index(op.f('ix_chat_history_user_id'), table_name='chat_history')
    op.drop_index(op.f('ix_chunks_embedding_key'), table_name='chunks')
    op.drop_index(op.f('ix_chunks_chunk_index'), table_name='chunks')
    op.drop_index(op.f('ix_chunks_document_id'), table_name='chunks')
    op.drop_index(op.f('ix_embedding_metadata_model_name'), table_name='embedding_metadata')
    op.drop_index(op.f('ix_ocr_text_document_id'), table_name='ocr_text')
    op.drop_index(op.f('ix_documents_status'), table_name='documents')
    op.drop_index(op.f('ix_documents_user_id'), table_name='documents')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('chat_history')
    op.drop_table('chunks')
    op.drop_table('embedding_metadata')
    op.drop_table('ocr_text')
    op.drop_table('documents')
    op.drop_table('users')
