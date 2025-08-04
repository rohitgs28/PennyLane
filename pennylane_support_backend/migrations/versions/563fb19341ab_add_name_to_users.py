"""add name to users

Revision ID: 563fb19341ab
Revises: 1edbb56c4e7d
Create Date: 2025-08-04 03:13:47.505860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '563fb19341ab'
down_revision = '1edbb56c4e7d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("name", sa.String(length=120)))

def downgrade():
    op.drop_column("users", "name")
