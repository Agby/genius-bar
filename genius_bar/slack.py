import logging
import pyramid.threadlocal
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

    def command_manager(self):
        if self.check_token():
            cmdname = self.rqbody['command'].split("/")
            try:
                rtn = getattr(self, cmdname[1])() # run function named self.cmdname[1](input)
            except Exception as e:
                logging.info(e)
                rtn = "command not found or argument!"
            return rtn
        else:
            return "token fail"

    #cmd = body_list['text'].split('+')
    def devicecheckout(self):
        return "devicecheckout"
    def devicelist(self):
        return "devicelist"
    def devicereg(self):
        try:
            self.session.flush()
            check_device = GeniusDeviceQuery.get_by_name(self.session, self.rqbody['text'])
            if check_device == None: # device not exist 
                check_user = GeniusUserQuery.get_by_name(self.session, self.rqbody['user_name'])
                if check_user == None: # user not exist 
                    input_user = GeniusUser(user_name = self.rqbody['user_name'], 
                                            slack_user_id = self.rqbody['user_id'])
                    self.session.add(input_user)
                    self.session.commit()
                    check_user = GeniusUserQuery.get_by_name(self.session, self.rqbody['user_name'])
                
                input_device = GeniusDevice(device_name = self.rqbody['text'], holder_id = check_user.id)
                self.session.add(input_device)
                self.session.commit()
                check_device = GeniusDeviceQuery.get_by_name(self.session, self.rqbody['text'])
                message = "Device id: " + str(check_device.id) + "  Device name: " + check_device.device_name
                logging.info(message)
                rtn = {"text": "Regist finisth!",
                               "attachments": [{"color" : "good" , "text" : message}]}
                self.add_event("reg", check_device.id, check_user.id)
            else:
                rtn = {"text": "Device is already registed! Maybe you need to regist with a new name"}
        except Exception as e:
            self.session.rollback()
            print(e)
        #payload = {"text": "test message"}
        #r = requests.post("https://hooks.slack.com/services/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", json=payload)
        return rtn
    def devicedereg(self):
        try:
            self.session.flush()
            check_device = GeniusDeviceQuery.get_by_name(self.session, self.rqbody['text'])
            if check_device is not None: # device exist 
                check_user = GeniusUserQuery.get_by_name(self.session, self.rqbody['user_name'])
                if check_user == None: # user exist 
                    input_user = GeniusUser(user_name = self.rqbody['user_name'], 
                                            slack_user_id = self.rqbody['user_id'])
                    self.session.add(input_user)
                    self.session.commit()
                    check_user = GeniusUserQuery.get_by_name(self.session, self.rqbody['user_name'])
                check_device.delete = True 
                self.session.commit()
                message = "Device id: " + str(check_device.id) + "  Device name: " + check_device.device_name
                logging.info(message)
                rtn = {"text": "Deregist finisth!",
                               "attachments": [{"color" : "good" , "text" : message}]}
                self.add_event("dereg", check_device.id, check_user.id)
            else:
                rtn = {"text": "Device not exist!"}
        except Exception as e:
            self.session.rollback()
            print(e)
        return rtn
    def deviceaudit():

        return "deviceaudit"
    def add_event(self, event_type, event_device_id, event_user_id):
        try:
            self.session.flush()
            if event_type == "reg" or event_type == "dereg":
                input_event = GeniusEvent(event_type = event_type, device_id = event_device_id, user_id = event_user_id)
            self.session.add(input_event)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logging.info(e)