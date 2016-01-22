from pyramid.view import view_config
import logging

from .slack import SlackManager

# receive request and return 
@view_config(route_name='home', renderer='json')
def my_view(request):
    slack = SlackManager(request)
    result = slack.command_manager()
    logging.info(result)
    return result
