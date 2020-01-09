from data import conf
from connect import Telnet
from data import logger

conf.telnet = None
conf.telnet_join = False

def telnet():
    if conf.telnet is None:
        conf.telnet = Telnet()
        conf.telnet_join = False

        conf.telnet.thread_run()
        return

    if conf.telnet:
        conf.telnet.close()
        conf.telnet = None
        return

