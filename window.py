import curses
import threading
import time
import math

from data import logger
from data import conf
from data import recv_serial
from enums import KEYBOARD
from observe import Observer

from connect import Telnet
import features


class Screen(object):
    """https://docs.python.org/3/howto/curses.html"""

    def __init__(self, port):

        self.top = 0

        self._window = None
        self.init_curses()

        self.port = port
        conf.port = port
        self._observer = Observer()
        recv_serial.add_observer(self._observer)

    def init_curses(self):

        self._window = curses.initscr()
        conf.window = self._window
        self._window.keypad(True)
        self._window.scrollok(True)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

        self._statusbar = StatusBar(self._window)

        self._window.clear()

        curses.noecho()
        curses.cbreak()
        curses.mousemask(-1)
        curses.start_color()

        self._menu = MenuEx(self._window)

    def keyboard_input(self):
        """这里获取输入并写入serialport"""
        logger.info("Screen.keyboard_input Run")
        while True:
            ch = self._window.getch()

            if ch == curses.KEY_MOUSE:
                pass
            elif ch == 17:  # Ctrl + Q
                exit()
            elif ch == 1:  # Ctrl + A
                logger.info("Screen.keyboard_input: Menu.run()")
                self._menu.run()
                self._window.refresh()
            else:
                self.port.write(ch)

    def display_buffer(self):
        """作为显示主界面的循环"""
        pos = 1

        logger.info("Screen.display_buffer Run")
        while True:
            y, x = self._window.getmaxyx()

            stream = self._observer.get()

            self._statusbar.display_statusbar(y, x)

            for e in stream:
                if e == "\n":
                    self._window.scroll()
                    pos = 1

                elif (ord(e) == 8):  # 退格
                    if pos > 0:
                        pos -= 1
                    curses.killchar()
                    self._window.move(y-2, pos)

                elif (ord(e) == 7):  # 顶头
                    curses.flash()
                    self._window.move(y-2, pos)

                else:  # 实际内容
                    if pos >= x:
                        self._window.scroll()
                        pos = 1
                    self._window.addstr(y-2, pos, e)
                    pos += 1

            self._window.refresh()  # 需要重新刷新

    def thread_keyboard_input(self):
        return threading.Thread(target=self.keyboard_input)

    def thread_display_buffer(self):
        return threading.Thread(target=self.display_buffer)

    def run(self):
        try:
            threads = []
            th1 = self.thread_keyboard_input()
            th2 = self.port.thread_loop_read()
            th3 = self.thread_display_buffer()
            threads.append(th1)
            threads.append(th2)
            threads.append(th3)

            for t in threads:
                t.setDaemon(True)
                t.start()

            for t in threads:
                t.join()
        except KeyboardInterrupt:
            exit()
        finally:
            curses.endwin()


def yxcenter(scr, text=""):
    '''
    Given a curses window and a string, return the x, y coordinates to pass to
    scr.addstr() for the provided text to be drawn in the horizontal and
    vertical center of the window.
    '''
    y, x = scr.getmaxyx()
    nx = (x // 2) - (len(text) // 2)
    ny = (y // 2) - (len(text.split('\n')) // 2)
    return ny, nx


class MenuEx:

    def __init__(self, window):
        """
        @_items
        {sortkey: [description, dirct_function]}
        """
        self._window = window
        self._menu = None
        self._options = {}

        self.max_long = 60

        self.add_item('t', 'connection Telnet turn on/off', features.telnet)

    def add_item(self, sortkey, description, dirct_func):
        """添加选项"""
        self._options[sortkey.upper()] = [description, dirct_func]

    def getch(self):
        return self._menu.getch()

    def display_menu(self):
        buf = []
        buf.append("CollConsole Command Summary")
        buf.append("---------------------------")
        buf.append("")

        for k, v in self._options.items():
            desc = v[0]
            msg = desc + "." * (self.max_long-10-len(desc)) + k
            buf.append(msg)

        y, x = yxcenter(self._window)

        self._menu = curses.newwin(
            len(buf)+2, self.max_long, y-math.ceil(len(buf)/2), x-math.ceil(self.max_long/2))

        index = 1
        for i in buf:
            self._menu.addstr(index, 2, i)
            index += 1

        # self._menu.border('|', '-', '+')
        self._menu.box()
        self._menu.refresh()

    def run(self):
        self.display_menu()

        while True:
            k = self.getch()
            if (k == ord('q') or k == KEYBOARD.Esc):
                self._menu.clear()
                self._menu.refresh()
                break

            # 执行指令
            elif chr(k).upper() in self._options.keys():
                func = self._options[chr(k).upper()][1]
                func()


class StatusBar:
    """最底下的状态栏"""

    def __init__(self, window):
        self._window = window

    def get_status(self, x):
        msg = []

        msg.append('Ctrl + A to open menu')

        msg.append('%s %s' % (conf.serial_port, conf.baudrate))

        if conf.telnet:
            if conf.telnet_join:
                msg.append('Telnet Status: Connect')
            else:
                msg.append('Telnet Status: Listen')



        msg = " | ".join(msg)
        _ = msg + " " * (x - len(msg))
        return _

    def display_statusbar(self, y, x):
        """添加状态栏"""
        self._window.setscrreg(0, y-2)
        self._window.attron(curses.color_pair(1))
        msg = self.get_status(x)
        self._window.addstr(y-1, 0, msg)
        self._window.attroff(curses.color_pair(1))
        self._window.refresh()
