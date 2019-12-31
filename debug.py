import curses
from data import conf

def debug():
    stdscr = conf.window
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    import ipdb
    ipdb.set_trace()
