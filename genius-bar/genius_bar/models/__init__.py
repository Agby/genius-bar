import logging

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

DBSession = scoped_session(sessionmaker())

from .base import *
from .device import *
from .user import *
from .event import *
from .base_query import *

log = logging.getLogger(__name__)

# Register the sa event, for timestamp or any custom event
GeniusUser.register()
GeniusDevice.register()
GeniusEvent.register()
