from pyramid.view import view_config
import logging
import pyramid.threadlocal

from .slack import SlackManager

# receive request and return 
@view_config(route_name='home', renderer='json')
def my_view(request):
    registry = pyramid.threadlocal.get_current_registry()
    settings = registry.settings
    token_list = []

    token_list.append(settings['device_checkout_token'])
    token_list.append(settings['device_list_token'])
    token_list.append(settings['device_reg_token'])
    token_list.append(settings['device_dereg_token'])
    token_list.append(settings['device_audit_token']) 
    found_token = True
    try:
        token_list.index(request.params['token'])
    except Exception as e:
        found_token = False
    # if token find
    if found_token == True: 
        logging.info("access_command！")
        slk = SlackManager(request.params)
        result = slk.command_manager()
        logging.info(result)
        return result
