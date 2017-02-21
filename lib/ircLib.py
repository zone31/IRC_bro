import socket
import ssl
import time
import queue
import threading
import os
import imp
import traceback
import sys
from lib.printLib import termPrinter,colors
## Class containing IRC related functions, such as parsing of messages, connection handeling, server class etc.
class IrcParse:
    def __init__(self):
        pass

    # Returns the shown message from the raw recived message
    def get_msg(self,msg):
        p1=msg.split(b"#",1)
        p2=p1[1].split(b":",1)
        return(p2[1][:-2])

    # Returns the nick of the sender
    def get_nick(self,msg):
        p1=msg.split(b"!",1)
        return(p1[0][1:])
    
    # Parses the message as a command for the bot, (botnick:command) return command
    def get_comm(self,msg,nick):
        rNick=self.get_nick(msg)
        rMsg=self.get_msg(msg)
        if rMsg.startswith(nick):
            ret=rMsg.split(b":",1)
            return(ret[1].strip())

    # Create a message formatted for sending
    def send_msg(self,channel,msg):
        return(b"PRIVMSG "+channel+b" :" + msg + b"\r\n")
    
    #Normally used for the chain calls, reverts the send command into the different parts
    def reverse_send_msg(self,msg):
        temp = msg.split(b" ", 2)
        command = temp[0]
        channel = temp[1]
        message = temp[2][1:-2]
        return((command,channel,message))

################################################################################################################
# Class for the connection
class IrcSession:
    def __init__(self, serv, nick, passwd, chan, port):
        #Print to terminal wrapper
        self.pr = termPrinter()
        self.serv = serv
        self.nick = nick
        self.passwd = passwd
        self.chan = chan
        self.port = port
        self.pWait = 1
        # should be limited
        self.backLog=[]

    def _connect(self):
        self.pr.notice("Connecting to " +
                       colors.YELLOW + str(self.serv) + colors.DEFAULT +
                       " channel " + colors.YELLOW + str(self.chan) + colors.DEFAULT,1)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((self.serv, self.port))
        self.soc.settimeout(self.pWait)
        self.soc.send(b"USER "+self.nick+b" "+self.nick+b" "+self.nick+b" :Dikunt bot\r\n")
        self._setNick(self.nick)
        self.soc.send(b"JOIN "+self.chan+b"\r\n")

    def _setNick(self,nick):
        self.nick=nick
        self.pr.notice("Nick is now " + colors.YELLOW + str(nick,'utf-8') + colors.DEFAULT,1)
        self.soc.send(b"NICK "+nick+b"\r\n")

    def _sendloop(self):
        self.pr.notice("Send loop started",1)
        while True:
            # If the loop should stop
            if self.quitEvent.is_set():
                self.pr.notice("Send loop stopped",1)
                return
            try:
                data = self.sendBuffer.get(True, self.pWait)
                for line in data:
                    self.pr.datapr(str(line,'utf-8'),self.pr.SEND)
                    self.soc.send(line)
                    time.sleep(1)
            except queue.Empty:
                pass
                

    def _reciveloop(self):
        self.pr.notice("Recive loop started",1)
        while True:
            # If the loop should stop
            if self.quitEvent.is_set():
                self.pr.notice("Recive loop stopped",1)
                return
            try:
                data = self.soc.recv(4096)
            except socket.timeout:
                continue
            self.pr.datapr(str(data,'utf-8'),self.pr.RECV)       
            if data.find(b'PING') == 0:
                self.soc.send(b'PONG ' + data.split()[1] + b'\r\n')
                continue
            self.recvBuffer.put(data)
            self.backLog.append(data)

    # Starts the connection in a new process, and returns two queue objects for sending and returning
    # data to the chat
    def start(self):
        self.pr.notice("Starting IRC session",1)
        self._connect()
        self.sendBuffer = queue.Queue()
        self.recvBuffer = queue.Queue()
        self.quitEvent = threading.Event()
        self.sendThr = threading.Thread(target=self._sendloop)
        self.recvThr = threading.Thread(target=self._reciveloop)
        self.sendThr.start()
        self.recvThr.start()
        return (self.sendBuffer,self.recvBuffer)

    def stop(self):
        self.pr.notice("Stopping IRC session",1)
        self.quitEvent.set()
        self.sendThr.join()
        self.recvThr.join()


################################################################################################################
#The bot class itself
class IrcBot:
    def __init__(self, ircSesh):
        #Print to terminal wrapper
        self.pr = termPrinter()
        self.ircSesh = ircSesh
        self.plugins = []
        self.inputPriority = []
        self.chainPriority = []

    def start(self):
        self.pr.notice("Starting IRC bot",1)
        (self.sendBuffer,self.recvBuffer) = self.ircSesh.start()
        self._start_plugins()
        while True:
            data = self.recvBuffer.get()
            try:
                output = self._call_plugins(data)
            except:
                print(traceback.format_exc())
                print(sys.exc_info()[0])
                self.pr.notice("Plugin returned error",4)

    def stop(self):
        self.pr.notice("Stopping IRC bot",1)
        self._kill_plugins()
        self.ircSesh.stop()

    def _kill_plugins(self):
        self.pr.notice("Stopping all plugins",1)
        fail = False
        for plug in self.plugins:
            if plug.stop():
                self.pr.notice("Plugin " + colors.YELLOW+plug.config['Name']+colors.DEFAULT+" stopped",1)
            else:
                self.pr.notice("Plugin " + colors.YELLOW+plug.config['Name']+colors.DEFAULT+" did not stop",3)
        if fail:
            self.pr.notice("Some plugins not loaded",3)

    
    # Returns the possible values from the plugins
    def _call_plugins(self,bstr):
        self._calculate_plugin_priority()
        # First we send the recived string to all plugins, if a plugin returns something, call the 
        # plugin in chains
        for inputID in self.inputPriority:
            plugin = self.plugins[inputID]
            # Try to parse the data, repport error if the plugin does
            try:
                (ret,data) = plugin.input(bstr,{})
                if not len(ret)==0:
                    self.pr.notice("Plugin "+colors.YELLOW+plugin.config['Name']+colors.DEFAULT+" returned",1)
                    for chainID in self.chainPriority:
                        plugin = self.plugins[chainID]
                        (ret,data) = plugin.output(ret,data)
                    self.sendBuffer.put(ret)
            except:
                print(traceback.format_exc())
                print(sys.exc_info()[0])
                self.pr.notice("Plugin "+ colors.YELLOW+plugin.config['Name']+colors.DEFAULT+" returned error",4)

    def _start_plugins(self):
        self.pr.notice("Loading plugins",1)
        root = "plugins/"
        self.plugins=[]
        files = os.listdir(root)
        files = [i for i in files if i not in ["__pycache__"]]
        self.pr.notice("Found folders:" +str(files),1);
        for i in files:
            self.pr.notice("Found possible plugin " + colors.YELLOW+str(i)+colors.DEFAULT,0)
            try:
                f = open(root+i+"/run.py", 'r')
                plug = imp.load_source(i,root+i,f)
                plugOBJ = self._test_and_return_plugin(plug)
                self.plugins.append(plugOBJ)
            except:
                print(traceback.format_exc())
                print(sys.exc_info()[0])
                self.pr.notice("Plugin failed to load",3)
        self.pr.notice(colors.YELLOW+str(len(self.plugins))+colors.DEFAULT+" Plugins loaded",1)
        self.pr.notice("Loaded plugins:"+colors.YELLOW+str([x.config["Name"] for x in self.plugins])+colors.DEFAULT,0)
        self._calculate_plugin_priority()

    def _calculate_plugin_priority(self):
        self.inputPriority = [i[0] for i in sorted(enumerate(self.plugins),key=lambda x: x[1].config["Input priority"],reverse=True)]
        self.chainPriority = [i[0] for i in sorted(enumerate(self.plugins),key=lambda x: x[1].config["Chain priority"])]


    def _test_and_return_plugin(self,plugin):
        self.pr.notice("Testing plugin",0)
        scope = plugin.IrcPlugin(self)


        # Test if the globals exist, and their types are correct
        if (not (type(scope.config["Name"]) is str)):
            raise Exception("config dict [Name] does not have correct type")
        
        if (not (type(scope.config["Input priority"]) is int)):
            raise Exception("config dict [Input priority] does not have correct type")
        
        if (not (type(scope.config["Chain priority"]) is int)):
            raise Exception("config dict [Chain priority] does not have correct type")

        if (not (type(scope.config["Help"]) is dict)):
            raise Exception("config dict [Help] does not have correct type")

        if (not (type(scope.config["Help"]["Description"]) is list)):
            raise Exception("config dict [Help][Description] does not have correct type")
        
        if (not (type(scope.config["Help"]["Commands"]) is list)):
            raise Exception("config dict [Help][Commands] does not have correct type")

        if (not (type(scope.config["Help"]["Passive"]) is list)):
            raise Exception("config dict [Help][Passive] does not have correct type")

        # Test if the functions exist
        if not callable(getattr(scope, "input", None)):
            raise Exception("Plugin does not have function input()")
        if not callable(getattr(scope, "stop", None)):
            raise Exception("Plugin does not have function stop()")
        if not callable(getattr(scope, "refresh", None)):
            raise Exception("Plugin does not have function refresh()")
        if not callable(getattr(scope, "output", None)):
            raise Exception("Plugin does not have function output()")
        
        #Test functions for correct return type
        (ret,data) = scope.input(b"Test Input",{'Type':'Test'})
        if (not (type(ret) is list)) and (not (type(data) is dict)):
            raise Exception("input() return is not correct types (list,dict)")

        (ret,data) = scope.output([b"Test Input"],{'Type':'Test'})
        if (not (type(ret) is list)) and (not (type(data) is dict)):
            raise Exception("output() return is not correct types (list,dict)")

        self.pr.notice("Plugin validated",0)
        return scope

    ######################################################################################
    ## API calls for the plugins
    def set_nick(self,nick):
        self.pr.notice("Setting nick to:"+colors.YELLOW+str(nick,'utf-8')+colors.DEFAULT,1)
        self.ircSesh._setNick(nick)
        self.refresh()
    
    def get_nick(self):
        return self.ircSesh.nick
    
    def get_chan(self):
        return self.ircSesh.chan

    # Refresh the plugins, aka ask for grab of possible new information.
    def refresh(self):
        self.pr.notice("Reloading plugins",1)
        for plug in self.plugins:
            if plug.refresh():
                self.pr.notice(colors.YELLOW+plug.config['Name']+colors.DEFAULT+" Reloaded",1)
            else: 
                self.pr.notice(colors.YELLOW+plug.config['Name']+colors.DEFAULT+"Not Reloaded",3)

    def reload(self):
        self._kill_plugins()
        self._start_plugins()


    def send_to_chain(self,bstr):
        pass