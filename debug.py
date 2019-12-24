import curses

def debug(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    import ipdb
    ipdb.set_trace()
