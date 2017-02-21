import sys
import traceback
import os
from run import termPrinter
from lib.ircLib import IrcParse
from lib.pluginLib import ConfigHandler

class IrcPlugin:
    def __init__(self, ircBot):
        self.configfile = os.path.abspath(__file__) + "/config.ini" 
        #Bind the ircBot to the object, so we can call it later
        self.ircBot = ircBot
        self.parse = IrcParse()
        self.pr = termPrinter()
        self.config = ConfigHandler() 
        #Refresh the variables in the class
        self.refresh()
    

    def refresh(self):
        self.nick = self.ircBot.get_nick()
        self.chan = self.ircBot.get_chan()
        self.plugins = self.ircBot.plugins
        self.config.load(self.configfile)
        return True


    def input(self,msg,data):
        try:
            retVar = []
            admins = [b'zone_31']
            scope = self.parse.get_comm(msg,self.nick).lower()
            nick = self.parse.get_nick(msg)
            # If the nick is an admin
            if nick in admins:
                if scope==(b"reload"):
                    self.pr.notice("Reloading plugins by command",2)
                    self.ircBot.reload()
                    retVar.append(self.parse.send_msg(self.chan,b"Reloaded "+bytes(str(len(self.plugins)),'utf-8')+b" plugins"))

                if (scope!=b"") and scope.startswith(b"nick"):
                    data=scope.split()
                    if len(data) < 2:
                        return (retVar,data)
                    self.pr.notice("Setting nick by command",2)
                    self.ircBot.set_nick(data[1])
                    retVar.append(self.parse.send_msg(self.chan,b"This is my nick now"))

            return (retVar,data)
        except:
            return ([],data)

    def output(self,msg,data):
        return (msg,data)
    
    def stop(self):
        # self.config.save(self.configfile)
        return True
