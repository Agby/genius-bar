import logging
import pyramid.threadlocal

class SlackManager(object):
    def __init__(self, request):
        self.request = request
        self.rqbody = request.params

    def check_token(self):
        registry = pyramid.threadlocal.get_current_registry()
        settings = registry.settings
        token_list = []

        token_list.append(settings['device_checkout_token'])
        token_list.append(settings['device_list_token'])
        token_list.append(settings['device_reg_token'])
        token_list.append(settings['device_dereg_token'])
        token_list.append(settings['device_audit_token']) 

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
        #payload = {"text": "test message"}
        #r = requests.post("https://hooks.slack.com/services/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", json=payload)
        return "devicereg"
    def devicedereg(self):

        x = {"channel" : "D0HKR069Z", "response_type" : "in_channel", "text": "meow devicedreg",
                           "attachments": [{"text" : "Partly cloudy today and tomorrow"}]}
        return x

    def deviceaudit():
        return "deviceaudit"