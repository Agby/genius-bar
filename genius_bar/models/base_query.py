from sqlalchemy.orm import exc


class BaseQuery(object):
    model_class = None

    def __init__(self, session):
        self.session = session

    def get_by_id(cls, id):
        try:
            return self.session.query(cls.model_class)\
                .filter(cls.model_class.id == id)\
                .one()
        except exc.NoResultFound:
            return None

    def get_all(cls):
        return self.session.query(cls.model_class)\
            .order_by(cls.model_class.id.asc())\
            .all()
