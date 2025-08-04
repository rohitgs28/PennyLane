"""add roles to users

Revision ID: e29f5e4afb0c
Revises: 563fb19341ab
Create Date: 2025-08-04 03:23:11.501109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e29f5e4afb0c'
down_revision = '563fb19341ab'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("roles", sa.ARRAY(sa.String()), server_default='{}'))
def downgrade():
    op.drop_column("users", "roles")