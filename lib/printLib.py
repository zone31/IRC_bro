# Lib containing pretty print functions
class colors:
    #Default text
    DEFAULT  = '\033[39m'
    #Colors
    RED         = '\033[31m'
    GREEN       = '\033[32m'
    YELLOW      = '\033[33m'
    BLUE        = '\033[34m'
    MAGENTA     = '\033[35m'
    CYAN        = '\033[36m'
    LIGHT_GRAY  = '\033[37m'
    DARK_GRAY   = '\033[38m'
    LIGHT_BLUE  = '\033[94m'
    #OPERATORS
    S_BLINK = '\033[5m'
    R_BLINK = '\033[25m'
    #Error levels
    DEBUG    = LIGHT_BLUE
    INFO     = GREEN
    WARNING  = YELLOW
    ERROR    = RED
    CRITICAL = S_BLINK + RED + R_BLINK
    SEND     = CYAN
    RECV     = MAGENTA


#Simple printer, should be changed to a logger at some point
class termPrinter:
    def __init__(self):
        self.DEBUG = 0
        self.INFO = 1
        self.WARNING = 2
        self.ERROR = 3
        self.CRITICAL = 4
        self.SEND = 5
        self.RECV = 6
        self.warnArr = [colors.DEBUG+"DEBUG"+colors.DEFAULT+"|",
                        colors.INFO+"INFO"+colors.DEFAULT+"|",
                        colors.WARNING+"WARNING"+colors.DEFAULT+"|",
                        colors.ERROR+"ERROR"+colors.DEFAULT+"|",
                        colors.CRITICAL+"CRITICAL"+colors.DEFAULT+"|"]
        self.dataprAr= [colors.SEND+"SEND"+colors.DEFAULT+"|",
                        colors.RECV+"RECV"+colors.DEFAULT+"|"]
    def pprint(self, istr):
        print(istr)
    def notice(self, istr, warnLvl):
        print(self.warnArr[warnLvl] + istr)
    def datapr(self, istr, dataType):
        print(self.dataprAr[dataType-5] + istr)