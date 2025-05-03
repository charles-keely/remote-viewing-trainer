"""init

Revision ID: initial
Create Date: 2023-06-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create targets table
    op.create_table('targets',
        sa.Column('target_id', sa.String(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('caption', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('target_id')
    )

    # Create sessions table
    op.create_table('sessions',
        sa.Column('session_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('target_id', sa.String(), nullable=False),
        sa.Column('user_notes', sa.String(), nullable=False),
        sa.Column('sketch_path', sa.String(), nullable=True),
        sa.Column('stage_durations', sa.JSON(), nullable=False),
        sa.Column('rubric', sa.JSON(), nullable=False),
        sa.Column('total_score', sa.Float(), nullable=False),
        sa.Column('aols', sa.JSON(), nullable=False),
        sa.Column('ts', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['target_id'], ['targets.target_id'], ),
        sa.PrimaryKeyConstraint('session_id')
    )


def downgrade():
    op.drop_table('sessions')
    op.drop_table('targets') 