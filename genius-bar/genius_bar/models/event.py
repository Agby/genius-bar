import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

from .base import Base, BaseMixin
from .user import GeniusUser
from .device import GeniusDevice
from .base_query import BaseQuery


class GeniusEvent(Base, BaseMixin):
    __tablename__ = 'genius_event'
    id = sa.Column(sa.Integer, primary_key=True)
    device_id = sa.Column(sa.Integer, sa.ForeignKey('genius_device.id'))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('genius_user.id'))
    event_type = sa.Column(sa.Unicode(16), nullable=False)
    genius_user = orm.relationship('GeniusUser')
    genius_device = orm.relationship('GeniusDevice')


class GeniusEventQuery(BaseQuery):
    model_class = GeniusEvent

    # @classmethod
    # def get_event(cls, session):
    #     try:
    #         return session.query(GeniusEvent)\
    #             .order_by(cls.model_class.id.desc())\
    #             .limit(20)
    #     except exc.NoResultFound:
    #         return None

    @classmethod
    def get_event(cls, session, input_type=None, limit=20):
        if input_type == None:
            try:
                return session.query(GeniusEvent)\
                    .order_by(cls.model_class.id.desc())\
                    .limit(limit)
            except exc.NoResultFound:
                return None
        else:
            try:
                return session.query(GeniusEvent)\
                    .filter(GeniusEvent.event_type == input_type)\
                    .order_by(cls.model_class.id.desc())\
                    .limit(limit)
            except exc.NoResultFound:
                return None
