"""Easter eggs

Revision ID: b84bb10fb8de
Revises: 515dc3f52c6d
Create Date: 2022-09-20 00:23:53.160168

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "b84bb10fb8de"
down_revision = "515dc3f52c6d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "easter_eggs",
        sa.Column("easter_egg_id", sa.Integer(), nullable=False),
        sa.Column("match", sa.Text(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("exact", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("startswith", sa.Boolean(), server_default="1", nullable=False),
        sa.PrimaryKeyConstraint("easter_egg_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("easter_eggs")
    # ### end Alembic commands ###