"""Add OCR details and chunk tokens

Revision ID: 20260716_ocr_details
Revises: 20260715_initial
Create Date: 2026-07-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260716_ocr_details'
down_revision = '20260715_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add fields to documents for OCR processing
    op.add_column('documents', sa.Column('file_size', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('checksum_sha256', sa.String(length=64), nullable=True))
    
    # Add fields to ocr_text for block details
    op.add_column('ocr_text', sa.Column('block_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('ocr_text', sa.Column('blocks_json', sa.JSON(), nullable=True))
    op.add_column('ocr_text', sa.Column('detected_language', sa.String(length=10), nullable=True, server_default='en'))
    
    # Add token count to chunks
    op.add_column('chunks', sa.Column('token_count', sa.Integer(), nullable=True))
    op.add_column('chunks', sa.Column('start_char', sa.Integer(), nullable=True))
    op.add_column('chunks', sa.Column('end_char', sa.Integer(), nullable=True))
    
    # Create unique index on document checksum per user
    op.create_index('ix_documents_user_checksum', 'documents', ['user_id', 'checksum_sha256'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_documents_user_checksum', table_name='documents')
    op.drop_column('chunks', 'end_char')
    op.drop_column('chunks', 'start_char')
    op.drop_column('chunks', 'token_count')
    op.drop_column('ocr_text', 'detected_language')
    op.drop_column('ocr_text', 'blocks_json')
    op.drop_column('ocr_text', 'block_count')
    op.drop_column('documents', 'checksum_sha256')
    op.drop_column('documents', 'file_size')
