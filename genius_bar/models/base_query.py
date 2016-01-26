from sqlalchemy.orm import exc


class BaseQuery(object):
    model_class = None

    def __init__(self, session):
        self.session = session

    def get_by_id(self, id):
        try:
            return self.session.query(self.model_class)\
                .filter(self.model_class.id == id)\
                .one()
        except exc.NoResultFound:
            return None

    def get_all(self):
        return self.session.query(self.model_class)\
            .order_by(self.model_class.id.asc())\
            .all()
