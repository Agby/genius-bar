import logging
import pyramid.threadlocal
import requests
from sqlalchemy import create_engine
from sqlalchemy import DDL
from genius_bar.models.user import GeniusUser, GeniusUserQuery
from genius_bar.models.device import GeniusDevice, GeniusDeviceQuery
from genius_bar.models.event import GeniusEvent, GeniusEventQuery
from genius_bar.models import (
    DBSession,
    Base,
    BaseQuery,
)

class SlackManager(object):

    def __init__(self, request):
        self.registry = pyramid.threadlocal.get_current_registry()
        self.settings = self.registry.settings
        self.request = request
        self.rqbody = request.params
        self.session = self.dbSetting()
        self.slack_url = self.settings['slack_url']

    def dbSetting(self):
        # sqlalchemy DBSession
        sqlalchemy_url  = self.settings['sqlalchemy.url']
        engine = create_engine(sqlalchemy_url)
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

        return DBSession

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
            DBSession.remove()
            return rtn
        else:
            return "token fail"

    def devicecheckout(self):
        self.session.flush()
        try:
            check_device = GeniusDeviceQuery.get_by_name(self.session, self.rqbody['text'])
            if check_device == None: # device not exist 
                rtn = {"color" : "warning", "text": "Device not found."}
            else :
                check_user = self.user_find()
                check_device.holder_id = check_user.id
                self.session.commit()
                payloadmsg = "@%s  checked out device `%s`" % (check_user.user_name, check_device.device_name)
                payload = {"attachments": [{"color" : "danger", "text": payloadmsg }]}
                r = requests.post(self.slack_url, json=payload) # post message to channel
                rtn = {"attachments": [{"color" : "warning" , "text" : payloadmsg }]}
                self.add_event("checkout", check_device.id, check_user.id)
        except Exception as e:
            self.session.rollback()
            logging.info(e)
            rtn = e
        return rtn

    def devicelist(self):
        self.session.flush()
        query_device = GeniusDeviceQuery.get_enable_device(self.session)
        message = "```\n{0:<16}{1:<16}\n".format("Device", "Holder")
        for x in query_device:
            message = message + ("\n{0:<16}{1:<16}\n".format(x.device_name, x.genius_user.user_name ))
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
            self.session.flush()
            check_device = GeniusDeviceQuery.get_by_name(self.session, self.rqbody['text'])
            if check_device == None: # device not exist 
                check_user = self.user_find()
                input_device = GeniusDevice(device_name = self.rqbody['text'], holder_id = check_user.id)
                self.session.add(input_device)
                self.session.commit()
                check_device = GeniusDeviceQuery.get_by_name(self.session, self.rqbody['text'])
                message = "  Device `%s` registered by @%s" % (check_device.device_name, check_user.user_name)
                rtn = {"attachments" : [{"color" : "good", "text" : message}]}
                self.add_event("reg", check_device.id, check_user.id)
            else:
                message = "`%s` already exists. Please register with another name." % (check_device.device_name)
                rtn = {"text" : message}
        except Exception as e:
            self.session.rollback()
            logging.info(e)
        rtn = self.rqbody['text'].find(" ")
        return rtn

    def devicedereg(self):
        try:
            self.session.flush()
            cmd = self.rqbody['text'].split(' ', 1)
            check_device = GeniusDeviceQuery.get_by_name(self.session, cmd[0])
            reason = " "
            if len(cmd) > 1:
                reason = cmd[1]
            if check_device is not None: # device exist 
                check_user = self.user_find()
                check_device.remarks = reason
                check_device.delete = True 
                self.session.commit()
                message = "Device id: " + str(check_device.id) + "  Device name: " + check_device.device_name + " reason: ", reason
                logging.info(message)
                rtn = {"text": "Deregist finisth!",
                               "attachments": [{"color" : "good" , "text" : message }]}
                self.add_event("dereg", check_device.id, check_user.id)
                payloadmsg = "@%s deregist the device `%s`" % (check_user.user_name, check_device.device_name)
                payload = {"attachments": [{"color" : "warning" , "text" : message}]}
                r = requests.post(self.slack_url, json=payload)
            else:
                rtn = {"text" : "Device not exist!"}
        except Exception as e:
            self.session.rollback()
            logging.info(e)
        return rtn
    # list event data 20
    def deviceaudit(self):
        self.session.flush()
        cmd = self.rqbody['text']
        if len(cmd) is not 0 : 
            query_event = GeniusEventQuery.get_event(self.session, cmd)
        else :
            query_event = GeniusEventQuery.get_event(self.session)
        message = "```\n%35s%20s%26s%26s\n" % ("Time", "Type", "Device", "User")
        for x in query_event:
            message = message + "%35s%20s%26s%26s\n" % ( str(x.event_time), x.event_type, 
                                                      x.genius_device.device_name, x.genius_user.user_name )

        rtn = {"text": "Device Audit",
                "attachments": [{"color" : "good" ,                 
                                 "text" : message + "```",
                                 "mrkdwn_in" : ["text"]}]}
        return rtn

    def user_find(self):
        check_user = GeniusUserQuery.get_by_name(self.session, self.rqbody['user_name'])
        if check_user == None: # user not exist 
            input_user = GeniusUser(user_name = self.rqbody['user_name'], 
                                    slack_user_id = self.rqbody['user_id'])
            self.session.add(input_user)
            self.session.commit()
            check_user = GeniusUserQuery.get_by_name(self.session, self.rqbody['user_name'])
        return check_user

    # add data into device_event  "checkout" "reg" "dereg"
    def add_event(self, event_type, event_device_id, event_user_id):
        check_user = GeniusUserQuery.get_by_name(self.session, self.rqbody['user_name'])
        try:
            self.session.flush()
            input_event = GeniusEvent(event_type = event_type, device_id = event_device_id, user_id = event_user_id)
            self.session.add(input_event)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logging.info(e)
