import serial
import threading
import queue as Queue

# from data import queue
from data import logger
from data import recv_serial
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
            # logger.debug("SerialPort.write <BackSpace>")
            self.port.write(b'\x08')

        elif c == KEYBOARD.Enter:
            self.port.write(b'\r')

        elif c == KEYBOARD.Ctrl_C:
            self.port.sendbreak()

        else:
            # logger.debug("SerialPort.write Char int: %s" % c)
            self.port.write(chr(c).encode())

    def write_stream(self, stream):
        """对一串流的写入"""
        for s in stream:
            self.write(s)

    def thread_loop_read(self):
        return threading.Thread(target=self.loop_read)

    def loop_read(self):
        logger.info("SerialPort.loop_read Run")
        while True:
            try:
                bytes_to_read = self.port.inWaiting()
                c = self.port.read(bytes_to_read)
                if c:
                    # logger.debug("SerialPort.Read byte: [[%s]]" % c)
                    recv_serial.notice(c.decode())
            except Queue.Empty:
                pass
