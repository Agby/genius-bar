import logging
from pyramid.view import view_config
from urllib.request import Request
from urllib.parse import unquote
from urllib.request import urlopen
import requests
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger( __name__ )

#receive request and return 
@view_config(route_name='home', renderer='json')
def my_view(request):
    found_token = True
    accedlist = rq_decode(request)
    token_list = ['WyQMp2xxs4hXTpEXM43SOLzM', 'Bnh4eVVru7Xmf0WUI0a8APqs' , 'cJlNFZt2cRgehBPiQq0vD5g9',
                  'jB6UIvVFgACe18YPHltpqqPj', 'v6X6evAJ4pDcSxc0feKLxQ6D']
    try:
        token_list.index(accedlist['token'])
    except Exception as e:
        found_token = False

    # if token find
    if found_token == True: 
        logger.info("access_command！")
        resault = access_command(accedlist)
        logger.info(resault)
        # request.headers['content-type'] = 'application/json'
        logger.info(request.headers['content-type'])
        return resault

#put body in to dictionary 
def rq_decode(rq): 
    rqlist = {}
    response = (rq.body).decode("utf-8")
    response = unquote(unquote(response))
    response = response.split("&")
    for x in response:
        x = x.split("=")
        rqlist[x[0]] = x[1]
    return rqlist

# select cmd
def access_command(accedlist):
    sl = SlackManager(accedlist)
    cmdname = accedlist['command'].split("/")
    try:
        rtn = getattr(sl, cmdname[1])()
    except Exception as e:
        logger.info(e)
        rtn = "command not found or argument!"
    return rtn

# cmd define
class SlackManager(object):

    def __init__(self, body_list):
        self.body_list = body_list
    #cmd = body_list['text'].split('+')
    def devicecheckout(self):
        return "devicecheckout"
    def devicelist(self):
        return "devicelist"
    def devicereg(self):
        payload = {"text": "lalalala meow"}
        r = requests.post("https://hooks.slack.com/services/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", json=payload)
        return "devicereg"
    def devicedereg(self):

        x = {"channel" : "D0HKR069Z", "response_type" : "in_channel", "text": "meow devicedreg",
                           "attachments": [{"text" : "Partly cloudy today and tomorrow"}]}
        return x

    def deviceaudit():
        return "deviceaudit"
