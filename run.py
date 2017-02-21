#!/bin/python3
import socket
import ssl
import time
import queue
import threading
import os
import imp
import traceback
import sys
from lib.ircLib import *
from lib.printLib import *
#from multiprocessing import Process, Manager
#Default setting
SERV = "irc.freenode.org"
NICK = b"irc_bro"
PASS = ""
CHAN = b"#dikufags"
PORT = 6667

def main():
    pr = termPrinter()
    ircSesh = IrcSession(SERV, NICK, PASS, CHAN, PORT)
    botSesh = IrcBot(ircSesh)
    try:
        botSesh.start()
    except (KeyboardInterrupt, SystemExit):
        pr.notice("Termination signal recived",2)
        botSesh.stop()

if __name__ == "__main__":
    main()
