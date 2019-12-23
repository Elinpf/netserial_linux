import serial

from data import port
from data import kb


def init_serial():
    ser = serial.Serial('/dev/rfcomm0', baudrate=9600, timeout=None, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, xonxoff=False)

    kb.buffer = ""
    ser.flushInput()
    print(ser.name)

    port = ser

def write(c):
    if isinstance(c, int):
        port.write(chr(c).encode())

    elif isinstance(c, str):
        port.write(c.encode())


def loop_read():
    while True:
        bytes_to_read = port.inWaiting()
        sleep(.5)

        while bytes_to_read < port.inWaiting():
            bytes_to_read = port.inWaiting()
            sleep(1)

        kb.buffer += port.read(bytes_to_read).decode()

    



