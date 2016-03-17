"""empty message

Revision ID: fcbd433f6cf2
Revises: 1b607b3e5311
Create Date: 2016-03-17 16:25:41.319704

"""

# revision identifiers, used by Alembic.
revision = 'fcbd433f6cf2'
down_revision = '1b607b3e5311'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ski_area', sa.Column('state_abbr', sa.Text(), nullable=True))
    op.create_foreign_key(None, 'ski_area', 'state', ['state_abbr'], ['abbr'])
    op.drop_column('ski_area', 'state')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('idx_trail_path', 'trail', ['path'], unique=False)
    op.add_column('ski_area', sa.Column('state', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'ski_area', type_='foreignkey')
    op.create_index('idx_ski_area_boundary', 'ski_area', ['boundary'], unique=False)
    op.drop_column('ski_area', 'state_abbr')
    op.create_index('idx_lift_path', 'lift', ['path'], unique=False)
    op.create_table('spatial_ref_sys',
    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('srid', name=u'spatial_ref_sys_pkey')
    )
    ### end Alembic commands ###
