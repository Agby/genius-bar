import logging
import requests

class SlackManager(object):
    def __init__(self, body_list):
        self.accedlist = body_list

    def command_manager(self):
        cmdname = self.accedlist['command'].split("/")
        try:
            rtn = getattr(self, cmdname[1])() # run function named self.cmdname[1](input)
        except Exception as e:
            logging.info(e)
            rtn = "command not found or argument!"
        return rtn

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