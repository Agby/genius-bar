import sqlalchemy as sa
from datetime import datetime, timedelta  
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseMixin(object):

    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = sa.Column(sa.Integer, primary_key=True)
    event_time = sa.Column('event_time', sa.DateTime, nullable=False)

    @staticmethod
    def creat_time(mapper, connection, instance):
        now = datetime.utcnow()+timedelta(hours=8)
        instance.event_time = now

    @classmethod
    def register(cls):
        sa.event.listen(cls, 'before_insert', cls.creat_time)
