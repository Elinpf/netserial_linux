import curses
import threading
import time
import queue as Queue

from data import logger
# from data import queue
from data import conf
from data import recv_serial
from enums import KEYBOARD
from observe import Observer

from connect import Telnet


class Screen(object):
    """https://docs.python.org/3/howto/curses.html"""

    def __init__(self, port):

        self.y = 0
        self.x = 0

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
        self._window.clear()

        curses.noecho()
        curses.cbreak()
        curses.mousemask(-1)
        curses.start_color()

        self._menu = Menu(self._window)

        self.y, self.x = self._window.getmaxyx()

    def keyboard_input(self):
        """这里获取输入并写入serialport"""
        logger.info("Screen.keyboard_input Run")
        while True:
            ch = self._window.getch()

            if ch == curses.KEY_MOUSE:
                pass
            elif ch == 17:  # Ctrl + Q
                # logger.debug('Screen.keyboard_input >>Ctrl + Q<<')
                exit()
            elif ch == 1:  # Ctrl + A
                logger.info("Screen.keyboard_input: Menu.run()")
                self._menu.run()
                self._window.refresh()
            else:
                # logger.debug('Screen.keyboard_input >>%s<<' % chr(ch))
                self.port.write(ch)

    def display_buffer(self):
        pos = 1

        logger.info("Screen.display_buffer Run")
        while True:
            try:
                stream = self._observer.get(timeout=0.1)

                for e in stream:
                    if e == "\n":
                        self._window.scroll()
                        pos = 1

                    else:
                        # logger.debug("Screen.display_buffer get Char: %s" % e)
                        if (ord(e) == 8):  # 退格
                            # logger.debug("Screen.display_buffer BackSpace: %s" % e)
                            if pos > 0:
                                pos -= 1
                            curses.killchar()
                            self._window.move(self.y-1, pos)

                        elif (ord(e) == 7):  # 顶头
                            # logger.debug("Screen.display_buffer LEFT: %s" % ord(e))
                            curses.flash()
                        else:
                            # FIXME 当一排超出屏幕会有问题
                            self._window.addstr(self.y-1, pos, e)
                            pos += 1

                    self._window.refresh()  # 需要重新刷新
            except Queue.Empty:
                time.sleep(0.1)
                pass

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


class Menu(object):

    def __init__(self, stdscr):
        y, x = yxcenter(stdscr)

        self._window = curses.newwin(10, 40, y-5, x-20)
        self._window.border(1)

    def menu_bar(self):
        res = ['CollConsole Command Summary']
        res.append('')

        res.append('connect Telnet on/off....T')

        return res

    def show_menu(self):
        index = 1
        for i in self.menu_bar():
            self._window.addstr(index, 2, i)
            index += 1

        self._window.refresh()

    def run(self):
        self.show_menu()
        while (True):
            k = self.getch()
            logger.debug("Menu.run: getch>>%s<<" % k)

            if (k == ord('q') or k == KEYBOARD.Esc):
                self._window.clear()
                self._window.refresh()
                break

            if (chr(k).upper() == 'T'):
                if conf.telnet is None:
                    conf.telnet = Telnet()
                    th = conf.telnet.thread_run()
                    th.start()

                if conf.telnet:
                    conf.telnet = None

                logger.info("Connect %s TELNET" % conf.telnet)

    def getch(self):
        return self._window.getch()


