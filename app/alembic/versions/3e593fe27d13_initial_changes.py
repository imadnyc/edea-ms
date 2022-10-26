"""initial changes

Revision ID: 3e593fe27d13
Revises: 
Create Date: 2022-10-26 17:47:38.652981

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '3e593fe27d13'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('projects')
    op.drop_table('jobqueue')
    op.drop_table('measurement_columns')
    op.drop_table('measurement_entries')
    op.drop_table('testruns')
    op.drop_table('sysconfig')
    op.drop_table('forcing_conditions')
    op.drop_table('specifications')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('specifications',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('project', sa.INTEGER(), nullable=True),
    sa.Column('name', sa.TEXT(), nullable=False),
    sa.Column('unit', sa.TEXT(), nullable=False),
    sa.Column('minimum', sa.FLOAT(), nullable=False),
    sa.Column('typical', sa.FLOAT(), nullable=False),
    sa.Column('maximum', sa.FLOAT(), nullable=False),
    sa.ForeignKeyConstraint(['project'], ['projects.id'], name='fk_specifications_projects_id_project'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('forcing_conditions',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('sequence_number', sa.INTEGER(), nullable=False),
    sa.Column('column', sa.INTEGER(), nullable=True),
    sa.Column('numeric_value', sa.FLOAT(), nullable=False),
    sa.Column('string_value', sa.TEXT(), nullable=False),
    sa.Column('testrun', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['column'], ['measurement_columns.id'], name='fk_forcing_conditions_measurement_columns_id_column'),
    sa.ForeignKeyConstraint(['testrun'], ['testruns.id'], name='fk_forcing_conditions_testruns_id_testrun'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sysconfig',
    sa.Column('key', sa.TEXT(), nullable=False),
    sa.Column('value', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('key')
    )
    op.create_table('testruns',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('short_code', sa.TEXT(), nullable=False),
    sa.Column('dut_id', sa.TEXT(), nullable=False),
    sa.Column('machine_hostname', sa.TEXT(), nullable=False),
    sa.Column('user_name', sa.TEXT(), nullable=False),
    sa.Column('test_name', sa.TEXT(), nullable=False),
    sa.Column('project', sa.INTEGER(), nullable=True),
    sa.Column('metadata', sqlite.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['project'], ['projects.id'], name='fk_testruns_projects_id_project'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('short_code')
    )
    op.create_table('measurement_entries',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('sequence_number', sa.INTEGER(), nullable=False),
    sa.Column('testrun', sa.INTEGER(), nullable=False),
    sa.Column('column', sa.INTEGER(), nullable=False),
    sa.Column('numeric_value', sa.FLOAT(), nullable=True),
    sa.Column('string_value', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('flags', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['column'], ['measurement_columns.id'], name='fk_measurement_entries_measurement_columns_id_column'),
    sa.ForeignKeyConstraint(['testrun'], ['testruns.id'], name='fk_measurement_entries_testruns_id_testrun'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('measurement_columns',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.TEXT(), nullable=False),
    sa.Column('project', sa.INTEGER(), nullable=True),
    sa.Column('spec', sa.INTEGER(), nullable=True),
    sa.Column('data_source', sa.TEXT(), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('user_note', sa.TEXT(), nullable=True),
    sa.Column('measurement_unit', sa.TEXT(), nullable=True),
    sa.Column('flags', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['project'], ['projects.id'], name='fk_measurement_columns_projects_id_project'),
    sa.ForeignKeyConstraint(['spec'], ['specifications.id'], name='fk_measurement_columns_specifications_id_spec'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('jobqueue',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('state', sa.INTEGER(), nullable=True),
    sa.Column('worker', sa.TEXT(), nullable=True),
    sa.Column('updated_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('function_call', sa.TEXT(), nullable=False),
    sa.Column('parameters', sqlite.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('projects',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('number', sa.TEXT(), nullable=False),
    sa.Column('name', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
