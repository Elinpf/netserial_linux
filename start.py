#!/usr/bin/python3
import threading

from serialport import SerialPort
from window import Screen
from debug import debug
from data import conf

port = SerialPort(conf.serial_port, conf.baudrate)

screen = Screen(port)

screen.run()
