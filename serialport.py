import serial
import threading
import queue as Queue

from data import queue
from data import logger
from enums import KEYBOARD


class SerialPort(object):

    def __init__(self, serialfile, baud):

        self.port = serial.Serial(serialfile, baudrate=baud, timeout=None, parity=serial.PARITY_NONE,
                                  bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, xonxoff=False)

        self.port.flushInput()
        print(self.port.name)

    def write(self, c: int):
        """对每个输入的字符进行写入"""
        if c == KEYBOARD.BackSpace:
            logger.debug("SerialPort.write <BackSpace>")
            self.port.write(b'\x08')
        elif c == KEYBOARD.Enter:
            self.port.write(b'\r')
        else:
            logger.debug("SerialPort.write Char int: %s" % c)
            self.port.write(chr(c).encode())

    def thread_loop_read(self):
        return threading.Thread(target=self.loop_read)

    def loop_read(self):
        logger.info("SerialPort.loop_read Run")
        while True:
            try:
                c = self.port.read()
                if c:
                    logger.debug("SerialPort.Read byte: [[%s]]" % c)
                    queue.put(c.decode())
            except Queue.Empty:
                pass
