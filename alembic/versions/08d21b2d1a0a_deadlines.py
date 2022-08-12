"""Deadlines

Revision ID: 08d21b2d1a0a
Revises: 3962636f3a3d
Create Date: 2022-08-12 23:44:13.947011

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "08d21b2d1a0a"
down_revision = "3962636f3a3d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "deadlines",
        sa.Column("deadline_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["ufora_courses.course_id"],
        ),
        sa.PrimaryKeyConstraint("deadline_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("deadlines")
    # ### end Alembic commands ###
