from sqlalchemy.orm import exc


class BaseQuery(object):
    model_class = None

    @classmethod
    def get_by_id(cls, DBSession, id):
        try:
            return DBSession.query(cls.model_class)\
                .filter(cls.model_class.id == id)\
                .one()
        except exc.NoResultFound:
            return None

    @classmethod
    def get_all(cls, DBSession):
        print(cls.model_class)
        return DBSession.query(cls.model_class)\
            .order_by(cls.model_class.id.asc())\
            .all()
