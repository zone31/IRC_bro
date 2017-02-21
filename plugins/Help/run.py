import sys
import traceback
import os
from run import termPrinter
from lib.ircLib import IrcParse
from lib.pluginLib import ConfigHandler

class IrcPlugin:
    def __init__(self, ircBot):
        # Set the path of the IRC file
        self.configfile = os.path.abspath(__file__) + "/config.ini" 
        # Bind the ircBot to the object, so we can call it later
        self.ircBot = ircBot
        self.parse = IrcParse()
        self.pr = termPrinter()
        self.config = ConfigHandler()
        # Refresh the variables in the class
        self.refresh()
    
    def _format_plugin_help(self,plugin):
        retVar = []
        retVar.append("-----")
        helpDict = plugin.config["Help"]
        retVar.append(plugin.config["Name"] + ":")
        retVar = retVar + helpDict["Description"]
        
        for command in helpDict["Commands"]:
            retVar.append(" " + str(self.nick,"utf-8") + ":" + command["cmd"])
            for desc in command["desc"]:
                retVar.append("   " + desc)
        for passive in helpDict["Passive"]:
            retVar.append(" " + passive)
        return retVar

    def refresh(self):
        self.nick = self.ircBot.get_nick()
        self.chan = self.ircBot.get_chan()
        self.plugins = self.ircBot.plugins
        #Load the config file
        self.config.load(self.configfile)
        return True

    def input(self,msg,data):
        retVar = []
        #Message parsing block, may return error
        try:
            command = self.parse.get_comm(msg,self.nick).lower()
            nick = self.parse.get_nick(msg)
        except:
            return(retVar,data)
        
        if command==(b"help"):
            retVar.append("All plugins:")
            for i in self.plugins:
                retVar = retVar + self._format_plugin_help(i)

            #Parse line for irc
            for i in range(len(retVar)):
                retVar[i] = self.parse.send_msg(nick,bytes(retVar[i],'utf-8'))
        return(retVar,data)
    
    def output(self,msg,data):
        return (msg,data)
    
    def stop(self):
        # self.config.save(self.configfile)
        return True

