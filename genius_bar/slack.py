import logging
import pyramid.threadlocal
import requests
from pyramid.decorator import reify
from genius_bar.models.user import GeniusUser, GeniusUserQuery
from genius_bar.models.device import GeniusDevice, GeniusDeviceQuery
from genius_bar.models.event import GeniusEvent, GeniusEventQuery
from . import (DBSession)
import transaction

class SlackManager(object):
    def __init__(self, request):
        self.registry = pyramid.threadlocal.get_current_registry()
        self.settings = self.registry.settings
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

    def check_token(self):
        token_list = []
        token_list.append(self.settings['device_checkout_token'])
        token_list.append(self.settings['device_list_token'])
        token_list.append(self.settings['device_reg_token'])
        token_list.append(self.settings['device_dereg_token'])
        token_list.append(self.settings['device_audit_token']) 

        return self.request.params['token'] in token_list

    # inpute data trasns /command -> command  
    def command_manager(self):
        if self.check_token():
            cmdname = self.rqbody['command'].split("/")
            try:
                rtn = getattr(self, cmdname[1])() # run function named self.cmdname[1](input)
            except AttributeError as e:
                logging.info(e)
                rtn = "command not found or argument!"
            DBSession.commit()
            DBSession.close()
            return rtn
        else:
            return "token fail"

    def devicecheckout(self):
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
                self.add_event("checkout", check_device.id, check_user.id)
        except Exception as e:
            logging.info(e)
            rtn = e
        return rtn

    def devicelist(self):
        query_device = self.device_query.get_enable_device()
        message = "```\n{0:<16}{1:<16}\n".format("Device", "Holder")
        for x in query_device:
            message = message + ("\n{0:<16}{1:<16}\n".format(x.device_name, x.holder.user_name ))
        rtn = {"text": "Device List", "attachments": [
            {
                "color" : "good",
                "text" : message + "```",
                "mrkdwn_in" : ["text"]
            }]}
        return rtn

    def devicereg(self):
        try:
            if self.rqbody['text'] == "" or self.rqbody['text'].find(" ") is not -1:
                message = " Update: Please try again with `/devicereg devicename`"
                rtn = {"text" : message}
                return rtn
            check_device = self.device_query.get_by_name(self.rqbody['text'])
            if check_device == None:
                check_user = self.user_find()
                input_device = GeniusDevice(device_name = self.rqbody['text'], holder_id = check_user.id)
                DBSession.add(input_device)
                check_device = self.device_query.get_by_name(self.rqbody['text'])
                message = "  Device `%s` registered by @%s" % (check_device.device_name, check_user.user_name)
                rtn = {"text" : "", "attachments" : [{
                                                     "color" : "good", 
                                                     "text" : message, 
                                                     "mrkdwn_in" : ["text"]
                                                     }]}
                self.add_event("reg", check_device.id, check_user.id)
            else:
                message = "`%s` already exists. Please register with another name." % (check_device.device_name)
                rtn = {"text" : message}
        except Exception as e:
            rtn = e
        return rtn

    def devicedereg(self):
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
                self.add_event("dereg", check_device.id, check_user.id)
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
    def deviceaudit(self):
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
    def add_event(self, event_type, event_device_id, event_user_id):
        check_user = self.user_query.get_by_name(self.rqbody['user_name'])
        try:
            input_event = GeniusEvent(event_type = event_type, device_id = event_device_id, user_id = event_user_id)
            DBSession.add(input_event)
        except Exception as e:
            logging.info(e)
