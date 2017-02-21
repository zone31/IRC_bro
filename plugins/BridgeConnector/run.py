import sys
import traceback
import os
from run import termPrinter
from lib.ircLib import IrcParse
from lib.pluginLib import ConfigHandler
import json
import fbchat


class DataMessage:
    pass
    

#########################################################################
class IrcConnector:
    pass

#########################################################################
#connector keeper. keeps relations between connections
class BridgeConnector:
    def __init__(self, bridgecnf):
        self.bridgecnf = bridgecnf

    def send(self,pltfrm,nick,message):
        pass

#########################################################################


class IrcPlugin:
    def __init__(self, ircBot):
        
        self.configfile = os.path.abspath(__file__) + "/config.ini" 
        #Bind the ircBot to the object, so we can call it later
        self.ircBot = ircBot
        #Refresh the variables in the class
        self.parse = IrcParse()
        self.pr = termPrinter()
        self.config = ConfigHandler() 
        self.refresh()

    # A plugin can recive a refresh at any times. If the plugin
    # Have saved variables, reload them here
    def refresh(self):
        self.nick = self.ircBot.get_nick()
        self.chan = self.ircBot.get_chan()
        self.config.load(self.configfile)
        self.bridgecnf = self.config[("Bridge info","data")]
        self.bridge = BridgeConnector(self.bridgecnf)
        return True
    
    def input(self,msg,data):

        return ([],data)


    def output(self,msg,data):
        return (msg,data)

    def stop(self):
        self.config.config["Bridge info"]["data"] = "\""+json.dumps(self.bridgecnf)+"\""
        self.config.save(self.configfile)
        return True
