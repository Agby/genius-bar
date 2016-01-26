import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc

from .base import Base, BaseMixin
from .base_query import BaseQuery


class GeniusUser(Base):
    
    __tablename__ = 'genius_user'
    id = sa.Column(sa.Integer, primary_key=True)
    user_name = sa.Column(sa.Unicode(16), nullable=False, unique=True)
    slack_user_id = sa.Column(sa.Unicode(16), nullable=False, unique=True)


class GeniusUserQuery(BaseQuery):
    model_class = GeniusUser

    def get_by_name(self, user_name):
        try:
            return self.session.query(GeniusUser)\
                .filter(GeniusUser.user_name == user_name)\
                .one()
        except exc.NoResultFound:
            return None
