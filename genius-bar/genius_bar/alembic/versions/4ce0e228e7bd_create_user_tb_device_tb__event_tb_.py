"""create user_tb, device_tb, event_tb

Revision ID: 4ce0e228e7bd
Revises: 
Create Date: 2016-01-13 17:41:51.518966

"""

# revision identifiers, used by Alembic.
revision = '4ce0e228e7bd'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'genius_user',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('user_name', sa.Unicode(16), nullable=False, unique=True),
        sa.Column('slack_user_id', sa.Unicode(16), nullable=False, unique=True),
        mysql_engine='InnoDB'
    )

    op.create_table(
        'genius_device',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('device_name', sa.Unicode(16), nullable=False, unique=True),
        sa.Column('os_version', sa.Unicode(16)),
        sa.Column('description', sa.Unicode(32)),
        sa.Column('holder_id', sa.Integer, sa.ForeignKey('genius_user.id', 
            onupdate='CASCADE', ondelete='CASCADE'), server_default='0'),
        sa.Column('delete', sa.Boolean, server_default='0', nullable=False),
        sa.Column('remarks', sa.Unicode(32)),
        mysql_engine='InnoDB'
    )
    op.create_table(
        'genius_event',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('device_id', sa.Integer, sa.ForeignKey('genius_device.id', 
            onupdate='CASCADE', ondelete='CASCADE')),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('genius_user.id', 
            onupdate='CASCADE', ondelete='CASCADE')),
        sa.Column('event_time', sa.DateTime),
        sa.Column('event_type', sa.Unicode(16), nullable=False),
        mysql_engine='InnoDB'
    )


def downgrade():
    pass
