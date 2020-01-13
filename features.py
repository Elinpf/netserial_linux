import sys
import curses
import logging

from data import conf
from connect import Telnet
from data import logger
import window

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


def exit():
    box = window.DialogBox()
    box.control_label('Leave without reset?')
    box.control_button(['Yes', 'No'])
    k = box.display()

    if k == 0:
        curses.endwin()
        conf.process_running = False
        sys.exit()
    else:
        box.quit()


conf.capture = None


def capture():
    box = window.DialogBox()
    box.control_label('Set capture file')
    box.control_input('capturefile')
    box.control_button(['OK', 'Cancel'])
    k = box.display()

    if k == 0:
        conf.capture = logging.getLogger('CaptureLog')
        log_format = logging.Formatter('%(message)s')
        handle = logging.FileHandler(box.inputs['capturefile'].strip())
        handle.setFormatter(log_format)
        conf.capture.addHandler(handle)
        conf.capture.setLevel(logging.INFO)

    else:
        if conf.capture:
            conf.capture.close()
            conf.capture = None

    box.quit()
