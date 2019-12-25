import threading

from serialport import SerialPort
from window import Screen
from debug import debug

port = SerialPort('/dev/rfcomm0', 9600)

screen = Screen(port)

screen.init_curses()

screen.run()
port.run()




