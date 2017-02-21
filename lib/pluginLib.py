from lib.printLib import termPrinter,colors
import configparser
import json
import os
import traceback
import sys

class ConfigHandler:
    def __init__(self):
        self.config = configparser.SafeConfigParser()

    # if the object is called with brackets, we return one of the
    # internal default keys of the config file, will return error if not found
    def __getitem__(self, arg):
        base = 'Plugin info'
        index = arg
        # If we get a definition for other cadegories in the config file
        if type(arg) is tuple:
            base,index = arg
        return self._try_parse_type(self.config[base][index])

    # Try to parse the input data
    def _try_parse_type(self,data):
        fjson = lambda x: json.loads(x[1:-1]) # Remove first and last caracter
        fint = lambda x: int(x)
        fstr = lambda x: str(x)
        fsame = lambda x: x
        testlist = [fjson,fint,fstr,fsame]
        for func in testlist:
            try:
                return func(data)
            except:
                pass

    def _load_config_from_path(self,path):
        self.config.read_file(open(path))

    def _save_config_to_path(self,path):
        with open(path, 'w') as configfile:
            self.config.write(configfile)

    #public funcitons
    def load(self,path):
        self._load_config_from_path(path)

    def save(self,path):
        self._save_config_to_path(path)