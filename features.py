import sys
import curses
import logging

from data import conf
from connect import Telnet
from data import logger
import window

conf.telnet = None  # 保存Telnet类
conf.telnet_join = False  # 保存是否有Telnet会话进入


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

        logging.shutdown()

        conf.process_running = False
        sys.exit()


conf.capture = None  # 保存拷屏Logger


def capture():
    box = window.DialogBox()
    box.control_label('Set capture file')
    box.control_input('capturefile')
    box.display()

    if not conf.capture:
        conf.capture = logging.getLogger('CaptureLog')

    else:
        for h in conf.capture.handlers[:]:
            conf.capture.removeHandler(h)

    log_format = logging.Formatter('%(message)s')

    filename = box.inputs['capturefile'].strip()

    if filename:
        handle = logging.FileHandler(filename)
        handle.setFormatter(log_format)
        conf.capture.addHandler(handle)
        conf.capture.setLevel(logging.INFO)


def close_capture():
    """关闭Capture如果有的话"""
    if has_capture():
        for h in conf.capture.handlers[:]:
            conf.capture.removeHandler(h)


def has_capture():
    """判断是否有记录文件"""

    if conf.capture:
        return len(conf.capture.handlers) > 0

    return False


def send_break():
    conf.port.send_break()
