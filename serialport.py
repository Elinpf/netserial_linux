from ipdb import set_trace
import serial
import threading
import queue as Queue

from data import queue
from data import logger




class SerialPort(object):

    def __init__(self, serialfile, baud):

        self.port = serial.Serial(serialfile, baudrate=baud, timeout=None, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, xonxoff=False)

        self.port.flushInput()
        self.buffer = Buffer()
        print(self.port.name)

    def write(self, c):
        """对每个输入的字符进行写入"""
        if isinstance(c, int):
            logger.debug("SerialPort.write Char: %s" % c)
            self.port.write(chr(c).encode())

        elif isinstance(c, str):
            logger.debug("SerialPort.write Char: %s" % c)
            self.port.write(c.encode())

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

    def run(self):
        self.thread_loop_read().start()

class Buffer(object):

    def __init__(self):
        self._buf = ""
        self._size = 0

        self._new = False

    def append(self, long_string:str):
        self._buf += long_string

        self._new = True
        self._size = len(self._buf)

    def __len__(self):
        return self._size

    def has_new(self):
        if self._new:
            self._new = False
            return True
        return False
        


class BufferList(object):

    def __init__(self):
        self._buf = []
        self._size = 0

        self._new = False
        

    def append(self, long_string:str):
        """添加，并修改长度"""
        res = long_string.split("\n")
        res = list(res)

        if long_string[0] == "\n":
            self._buf.append(res)
        else:
            self._buf[-1] += res.pop(0)
            self._buf += res

        self._size = len(self._buf)
        self._new = True

    def get(self, top:int, bottom:int):
        """返回一段"""
        if top < 0:
            top = 0
        return self._buf[top, bottom]

    def __len__(self):
        return self._size

    def has_new(self):
        """判断是否有新内容"""
        if self._new:
            self._new = False
            return True

        return False

    




