from pyramid.config import Configurator
from sqlalchemy import create_engine
from genius_bar.models import (
    DBSession,
    Base,
    BaseQuery,
)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    #sqlalchemy DBSession
    config = Configurator(settings=settings)
    sqlalchemy_url  = settings['sqlalchemy_url']
    engine = create_engine(sqlalchemy_url)
    # DBSession.configure(bind=engine, extension=ZopeTransactionExtension())
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()
