"""Initial schema for streamlined app

Revision ID: 7bb33e468c43
Revises: 
Create Date: 2025-07-26 23:11:09.238063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bb33e468c43'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=False),
    sa.Column('role', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('interview_experience',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('company_name', sa.String(length=100), nullable=False),
    sa.Column('role', sa.String(length=100), nullable=False),
    sa.Column('experience_type', sa.String(length=50), nullable=False),
    sa.Column('batch_year', sa.Integer(), nullable=True),
    sa.Column('branch', sa.String(length=100), nullable=True),
    sa.Column('interview_date', sa.Date(), nullable=True),
    sa.Column('date_submitted', sa.DateTime(), nullable=False),
    sa.Column('experience_text', sa.Text(), nullable=False),
    sa.Column('rounds_details', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reset_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=120), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reset_token')
    op.drop_table('interview_experience')
    op.drop_table('user')
    # ### end Alembic commands ###
