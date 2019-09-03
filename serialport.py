import serial
import threading
import select

from data import conf
from data import logger
from data import recv_serial
from enums import KEYBOARD


class SerialPort(object):

    def __init__(self, serialfile, baud):

        if baud not in serial.Serial.BAUDRATES:
            print("波特率%s是错误的,请重新选择" % baud)
            exit()

        try:
            self.port = serial.Serial(serialfile, baudrate=baud, timeout=None, parity=serial.PARITY_NONE,
                                      bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, xonxoff=False)
        except serial.serialutil.SerialException:
            print("未成功打开串口 %s , 是否没有打开串口" % serialfile)
            exit()

        self.port.flushInput()

    def write(self, c: int):
        """对每个输入的字符进行写入"""
        if c == KEYBOARD.BackSpace:
            self.port.write(b'\x08')

        elif c == KEYBOARD.Enter:
            self.port.write(b'\r')

        else:
            self.port.write(chr(c).encode())

    def write_byte(self, b: bytes):
        self.write(ord(b))

    def write_stream(self, stream):
        """对一串流的写入"""
        for s in stream:
            self.write(s)

    def write_hex(self, h):
        self.port.write(bytes.fromhex(h))

    def thread_loop_read(self):
        return threading.Thread(target=self.loop_read, name='serialport_thread')

    def loop_read(self):
        logger.info("SerialPort.loop_read Run")
        while conf.process_running:
            ready = select.select([self.port], [], [], 1)[0]

            if ready:
                bytes_to_read = self.port.inWaiting()
                c = self.port.read(bytes_to_read)
                if c:
                    recv_serial.notice(c.decode())
