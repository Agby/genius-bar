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

    def get_event(self, input_name=None, limit=20):
        if input_name is None:
            try:
                return self.session.query(GeniusEvent)\
                    .order_by(GeniusEvent.id.desc())\
                    .limit(limit)
            except exc.NoResultFound:
                return None
        else:
            try:
                return self.session.query(GeniusEvent)\
                    .join(GeniusDevice)\
                    .filter(GeniusDevice.device_name == input_name)\
                    .order_by(GeniusEvent.id.desc())\
                    .limit(limit)
            except exc.NoResultFound:
                return None
