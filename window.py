import curses
import threading
import time
import queue as Queue

from data import logger
from data import queue


class Screen(object):
    """https://docs.python.org/3/howto/curses.html"""

    def __init__(self, port):

        self.y = 0
        self.x = 0

        self.top = 0

        self.window = None
        self.init_curses()

        self.port = port

    def init_curses(self):

        self.window = curses.initscr()
        self.window.keypad(True)
        self.window.scrollok(True)
        self.window.clear()


        curses.noecho()
        curses.cbreak()
        curses.mousemask(-1)
        curses.start_color()

        self.y, self.x = self.window.getmaxyx()

    def keyboard_input(self):
        """这里获取输入并写入serialport"""
        logger.info("Screen.keyboard_input Run")
        while True:
            ch = self.window.getch()

            if ch == curses.KEY_MOUSE:
                pass
            elif ch == 17:  # Ctrl + Q
                logger.debug('Screen.keyboard_input >>Ctrl + Q<<')
                exit()
            else:
                logger.debug('Screen.keyboard_input >>%s<<' % chr(ch))
                self.port.write(ch)
                pass

    def display_buffer(self):
        pos = 1

        logger.info("Screen.display_buffer Run")
        while True:
            try:
                e = queue.get(timeout=0.1)
                if e == "\n":
                    self.window.scroll()
                    pos = 1

                else:
                    logger.debug("Screen.display_buffer get Char: %s" % e)
                    if (ord(e) == 263):  # 退格
                        if pos > 2:
                            pos -= 1
                        self.window.addstr(self.y-1, pos, ' ')
                    else:
                        self.window.addstr(self.y-1, pos, e)
                        pos += 1

                self.window.refresh() # 需要重新刷新
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
            pass
        finally:
            curses.endwin()
