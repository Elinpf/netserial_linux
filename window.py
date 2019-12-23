import curses

from data import window
from data import port
from data import kb

def init_crt():
    crt = curses.initscr()
    crt.clear()
    crt.refresh()

    window.crt = crt

    curses.start_color()
    curses.mousemask(-1)

def read_buffer():
    k = 0

    while (k != 17): # Ctrl + Q
        window.crt.clear()
        height, width = window.crt.getmaxyx()

        if k == curses.KEY_MOUSE: # 如果是鼠标的移动，这不动
            pass

        else:
            port.write(k)

        if port.has_new:
            window.crt.addstr(0,0, kb.buffer)



