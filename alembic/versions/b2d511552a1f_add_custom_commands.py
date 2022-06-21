"""Add custom commands

Revision ID: b2d511552a1f
Revises: 4ec79dd5b191
Create Date: 2022-06-21 22:10:05.590846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2d511552a1f'
down_revision = '4ec79dd5b191'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('custom_commands',
    sa.Column('command_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('indexed_name', sa.Text(), nullable=False),
    sa.Column('response', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('command_id'),
    sa.UniqueConstraint('name')
    )
    with op.batch_alter_table('custom_commands', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_custom_commands_indexed_name'), ['indexed_name'], unique=False)

    op.create_table('custom_command_aliases',
    sa.Column('alias_id', sa.Integer(), nullable=False),
    sa.Column('alias', sa.Text(), nullable=False),
    sa.Column('indexed_alias', sa.Text(), nullable=False),
    sa.Column('command_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['command_id'], ['custom_commands.command_id'], ),
    sa.PrimaryKeyConstraint('alias_id'),
    sa.UniqueConstraint('alias')
    )
    with op.batch_alter_table('custom_command_aliases', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_custom_command_aliases_indexed_alias'), ['indexed_alias'], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('custom_command_aliases', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_custom_command_aliases_indexed_alias'))

    op.drop_table('custom_command_aliases')
    with op.batch_alter_table('custom_commands', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_custom_commands_indexed_name'))

    op.drop_table('custom_commands')
    # ### end Alembic commands ###