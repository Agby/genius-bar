import datetime
import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseMixin(object):

    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = sa.Column(sa.Integer, primary_key=True)
    event_time = sa.Column('event_time', sa.DateTime, nullable=False)

    @staticmethod
    def event_time(mapper, connection, instance):
        now = datetime.datetime.utcnow()
        instance.event_time = now

    @classmethod
    def register(cls):
        sa.event.listen(cls, 'before_insert', cls.event_time)

    def accept(self, visitor, *args, **kwargs):
        klass = self.__class__.__name__
        return getattr(visitor, 'visit' + klass)(self, *args, **kwargs)
