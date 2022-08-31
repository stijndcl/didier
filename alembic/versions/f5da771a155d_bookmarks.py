"""Bookmarks

Revision ID: f5da771a155d
Revises: 38b7c29f10ee
Create Date: 2022-08-30 01:08:54.323883

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f5da771a155d"
down_revision = "38b7c29f10ee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "bookmarks",
        sa.Column("bookmark_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("jump_url", sa.Text(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("bookmark_id"),
        sa.UniqueConstraint("user_id", "label"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("bookmarks")
    # ### end Alembic commands ###
