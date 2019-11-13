"""empty message

Revision ID: 97d96594a937
Revises: 
Create Date: 2019-11-13 09:50:03.175299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97d96594a937'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invoices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('month', sa.Enum('MONTH_1_2', 'MONTH_3_4', 'MONTH_5_6', 'MONTH_7_8', 'MONTH_9_10', 'MONTH_11_12', name='month'), nullable=True),
    sa.Column('number', sa.String(), nullable=True),
    sa.Column('note', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('prizes',
    sa.Column('type', sa.Enum('SPECIAL_TOP_AWARD', 'TOP_AWARD', 'FIRST_AWARD', 'SECOND_AWARD', 'THIRD_AWARD', 'FOURTH_AWARD', 'FIFTH_AWARD', 'SIXTH_AWARD', 'SPECIAL_SIXTH_AWARD', name='prizetype'), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('month', sa.Enum('MONTH_1_2', 'MONTH_3_4', 'MONTH_5_6', 'MONTH_7_8', 'MONTH_9_10', 'MONTH_11_12', name='month'), nullable=False),
    sa.Column('number', sa.String(), nullable=True),
    sa.Column('prize', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('type', 'year', 'month')
    )
    op.create_table('users',
    sa.Column('sub', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('sub')
    )
    op.create_table('invoice_matches',
    sa.Column('invoice_id', sa.Integer(), nullable=False),
    sa.Column('prize_type', sa.Enum('SPECIAL_TOP_AWARD', 'TOP_AWARD', 'FIRST_AWARD', 'SECOND_AWARD', 'THIRD_AWARD', 'FOURTH_AWARD', 'FIFTH_AWARD', 'SIXTH_AWARD', 'SPECIAL_SIXTH_AWARD', name='prizetype'), nullable=True),
    sa.Column('prize_year', sa.Integer(), nullable=True),
    sa.Column('prize_month', sa.Enum('MONTH_1_2', 'MONTH_3_4', 'MONTH_5_6', 'MONTH_7_8', 'MONTH_9_10', 'MONTH_11_12', name='month'), nullable=True),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
    sa.ForeignKeyConstraint(['prize_type', 'prize_year', 'prize_month'], ['prizes.type', 'prizes.year', 'prizes.month'], ),
    sa.PrimaryKeyConstraint('invoice_id')
    )
    op.create_table('user_invoice',
    sa.Column('user_sub', sa.String(), nullable=False),
    sa.Column('invoice_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
    sa.ForeignKeyConstraint(['user_sub'], ['users.sub'], ),
    sa.PrimaryKeyConstraint('user_sub', 'invoice_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_invoice')
    op.drop_table('invoice_matches')
    op.drop_table('users')
    op.drop_table('prizes')
    op.drop_table('invoices')
    # ### end Alembic commands ###
