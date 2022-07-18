"""Add dad jokes

Revision ID: 581ae6511b98
Revises: 632b69cdadde
Create Date: 2022-07-15 23:37:08.147611

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "581ae6511b98"
down_revision = "632b69cdadde"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "dad_jokes",
        sa.Column("dad_joke_id", sa.Integer(), nullable=False),
        sa.Column("joke", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("dad_joke_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("dad_jokes")
    # ### end Alembic commands ###