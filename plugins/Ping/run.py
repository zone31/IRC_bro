import sys
import traceback
import os
from run import termPrinter
from lib.ircLib import IrcParse
from lib.pluginLib import ConfigHandler

class IrcPlugin:
    def __init__(self, ircBot):
        #Bind the ircBot to the object, so we can call it later
        self.configfile = os.path.abspath(__file__) + "/config.ini" 
        self.ircBot = ircBot
        #Refresh the variables in the class
        self.config = ConfigHandler() 
        self.parse = IrcParse()
        self.pr = termPrinter()
        self.refresh()


    # A plugin can recive a refresh at any times. If the plugin
    # Have saved variables, reload them here
    def refresh(self):
        self.nick = self.ircBot.get_nick()
        self.chan = self.ircBot.get_chan()
        self.config.load(self.configfile)
        return True
    
    def input(self,msg,data):
        try:
            senderNick = self.parse.get_nick(msg)
            comm = self.parse.get_comm(msg,self.nick).lower()
            if comm == (b"ping"):
                data["pinger"] = senderNick
                return(([self.parse.send_msg(self.chan,senderNick+b":pong")],data))
            return ([],data)
        except:
            return ([],data)


    def output(self,msg,data):
        try:
            senderNick = data["pinger"]
            (_,_,comm) = self.parse.reverse_send_msg(msg[0])
            return(([self.parse.send_msg(self.chan,comm+b" "+senderNick+b"!")],data))
        except:
            return (msg,data)

    def stop(self):
        return True
