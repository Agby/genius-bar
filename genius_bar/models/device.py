import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

from .base import Base, BaseMixin
from .user import GeniusUser
from .base_query import BaseQuery


class GeniusDevice(Base):
    __tablename__ = 'genius_device'
    id = sa.Column(sa.Integer, primary_key=True)
    device_name = sa.Column(sa.Unicode(16), nullable=False, unique=True)
    os_version = sa.Column(sa.Unicode(16))
    description = sa.Column(sa.Unicode(32))
    holder_id = sa.Column(sa.Integer, sa.ForeignKey('genius_user.id'))
    delete = sa.Column(sa.Boolean, default=0, nullable=False)
    remarks = sa.Column(sa.Unicode(32))

    genius_user = orm.relationship('GeniusUser')


class GeniusDeviceQuery(BaseQuery):
    model_class = GeniusDevice

    def get_enable_device(session):
        try:
            return session.query(GeniusDevice)\
                .join(GeniusUser)\
                .filter(GeniusDevice.delete == False)\
                .all()
        except exc.NoResultFound:
            return None

    def get_by_name(session, device_name):
        try:
            return session.query(GeniusDevice)\
                .filter(GeniusDevice.device_name == device_name)\
                .one()
        except exc.NoResultFound:
            return None

    def get_by_holder(session, holder):
        try:
            return session.query(GeniusDevice)\
                .filter(GeniusDevice.holder_id == holder.id)\
                .filter(GeniusDevice.delete == False)\
                .all()
        except exc.NoResultFound:
            return None

    def get_device_by_holder_name(session, name):
        try:
            return session.query(GeniusDevice)\
                .join(GeniusUser)\
                .filter(GeniusUser.user_name == name)\
                .all()
        except exc.NoResultFound:
            return None
