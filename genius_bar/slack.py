import logging
import requests
from pyramid.decorator import reify
from genius_bar.models.user import GeniusUser, GeniusUserQuery
from genius_bar.models.device import GeniusDevice, GeniusDeviceQuery
from genius_bar.models.event import GeniusEvent, GeniusEventQuery
from . import (DBSession)
import transaction

class SlackManager(object):
    def __init__(self, request):
        self.settings = request.registry.settings
        self._token_map = {
            self.settings['device_checkout_token']: self.device_checkout,
            self.settings['device_list_token']: self.device_list,
            self.settings['device_reg_token']: self.device_reg,
            self.settings['device_dereg_token']: self.device_dereg,
            self.settings['device_audit_token']: self.device_audit,
        }

        self.request = request
        self.rqbody = request.params
        self.slack_url = self.settings['slack_url']

    @reify
    def device_query(self):
        return GeniusDeviceQuery(DBSession)

    @reify
    def user_query(self):
        return GeniusUserQuery(DBSession)

    @reify
    def event_query(self):
        return GeniusEventQuery(DBSession)

    def token_method(self, token):
        return self._token_map.get(token, None)

    # inpute data trasns /command -> command 
    def command_manager(self):
        command = self.rqbody['command'].split("/")
        action = self.token_method(self.request.params['token'])
        action_command = (action.__name__).replace("_", "")
        if action is None:
            return "Token fails"
        if action_command != command[1]:
            return "Token valid, but map to incorrect action."
        rtn = action()
        DBSession.commit()
        DBSession.close()
        return rtn

    def device_checkout(self):
        try:
            check_device = self.device_query.get_by_name(self.rqbody['text'])
            if check_device == None: # device not exist 
                rtn = {"color" : "warning", "text": "Device not found."}
            else :
                check_user = self.user_find()
                check_device.holder = check_user
                payloadmsg = "@%s  checked out device `%s`" % (check_user.user_name, check_device.device_name)
                payload = {"text" : "", "attachments": [{
                                                        "color" : "danger",
                                                        "text": payloadmsg,
                                                        "mrkdwn_in" : ["text"]
                                                        }]}
                r = requests.post(self.slack_url, json=payload) # post message to channel
                rtn = payload
                self.add_event("checkout", check_device, check_user)
        except Exception as e:
            logging.info(e)
            rtn = e
        return rtn

    def device_list(self):
        query_device = self.device_query.get_enable_device()
        message = "```\n{0:<16}{1:<16}\n".format("Device", "Holder") # format output 
        for x in query_device:
            message = message + ("\n{0:<16}{1:<16}\n".format(x.device_name, x.holder.user_name ))
        rtn = {"text": "Device List", "attachments": [
            {
                "color" : "good",
                "text" : message + "```",
                "mrkdwn_in" : ["text"]
            }]}
        return rtn

    def device_reg(self):
        try:
            if self.rqbody['text'] == "" or self.rqbody['text'].find(" ") is not -1:
                message = " Update: Please try again with `/devicereg devicename`"
                rtn = {"text" : message}
                return rtn
            check_device = self.device_query.get_by_name(self.rqbody['text'])
            if check_device == None:
                check_user = self.user_find()
                input_device = GeniusDevice(device_name = self.rqbody['text'], holder = check_user)
                DBSession.add(input_device)
                check_device = self.device_query.get_by_name(self.rqbody['text'])
                message = "  Device `%s` registered by @%s" % (check_device.device_name, check_user.user_name)
                rtn = {"text" : "", "attachments" : [{
                                                     "color" : "good", 
                                                     "text" : message, 
                                                     "mrkdwn_in" : ["text"]
                                                     }]}
                self.add_event("reg", check_device, check_user)
            else:
                message = "`%s` already exists. Please register with another name." % (check_device.device_name)
                rtn = {"text" : message}
        except Exception as e:
            rtn = e
        return rtn

    def device_dereg(self):
        try:
            cmd = self.rqbody['text'].split(' ', 1)
            check_device = self.device_query.get_by_name(cmd[0])
            reason = " "
            if len(cmd) > 1:
                reason = cmd[1]
            if check_device is not None: # device exist 
                check_user = self.user_find()
                check_device.remarks = reason
                check_device.delete = True 
                self.add_event("dereg", check_device, check_user)
                payloadmsg = "@%s deregist the device `%s`" % (check_user.user_name, check_device.device_name)
                payload = {"text" : "", "attachments": [{
                                                        "color" : "warning",
                                                        "text" : payloadmsg,
                                                        "mrkdwn_in" : ["text"]
                                                        }]}
                rtn = payload
                r = requests.post(self.slack_url, json=payload)
            else:
                rtn = {"text" : "Device not exist!"}
        except Exception as e:
            rtn = e
            logging.info(e)
        return rtn

    # list event data 20
    def device_audit(self):
        cmd = self.rqbody['text']
        if len(cmd) is not 0 : 
            query_event = self.event_query.get_event(cmd)
        else :
            query_event = self.event_query.get_event()
        message = "```\n%30s%16s%16s%16s\n" % ("Time", "Type", "Device", "User")
        for x in query_event:
            message = message + "%30s%16s%16s%16s\n" % ( str(x.event_time), x.event_type, 
                                                      x.genius_device.device_name, x.genius_user.user_name )

        rtn = {"text": "Device Audit",
                "attachments": [{
                                "color" : "good" ,                 
                                "text" : message + "```",
                                "mrkdwn_in" : ["text"]
                                }]}
        return rtn

    def user_find(self):
        check_user = self.user_query.get_by_name(self.rqbody['user_name'])
        if check_user == None: # user not exist 
            input_user = GeniusUser(user_name = self.rqbody['user_name'], 
                                    slack_user_id = self.rqbody['user_id'])
            DBSession.add(input_user)
            check_user = input_user
        return check_user

    # add data into device_event  "checkout" "reg" "dereg"
    def add_event(self, event_type, event_device, event_user):
        check_user = self.user_query.get_by_name(self.rqbody['user_name'])
        try:
            input_event = GeniusEvent(event_type = event_type, device = event_device, user = event_user)
            DBSession.add(input_event)
        except Exception as e:
            logging.info(e)
