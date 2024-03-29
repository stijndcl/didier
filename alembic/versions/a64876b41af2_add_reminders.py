"""Add reminders

Revision ID: a64876b41af2
Revises: c1f9ee875616
Create Date: 2022-09-23 13:37:10.331840

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a64876b41af2"
down_revision = "c1f9ee875616"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "reminders",
        sa.Column("reminder_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("category", sa.Enum("LES", name="remindercategory"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("reminder_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("reminders")
    sa.Enum("LES", name="remindercategory").drop(op.get_bind())
    # ### end Alembic commands ###
