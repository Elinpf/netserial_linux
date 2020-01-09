from data import logger
import socket
import select
import threading
from data import conf

from enums import KEYBOARD


def clean_text(text):

    if text[0] == 255:
        return ""

    if text[0] == 13:
        return b'\r'

    return text

class Connection(object):

    def __init__(self, socket, port):
        from data import recv_serial
        from observe import Observer
        self._socket = socket
        self._port = port
        self._observer = Observer()
        recv_serial.add_observer(self._observer)

    def fileno(self):
        return self._socket.fileno()

    def init_tcp(self):
        """
        set up telnet
        """

        # IAC WILL ECHO
        self._socket.send(bytes.fromhex('fffb01'))

        # IAC DONT ECHO 这个无法使用
        # self._socket.send(bytes.fromhex('fffe01'))

        # don't want linemode
        self._socket.send(bytes.fromhex('fffb22'))

        self.send_tcp(
            "************************************************\r\n")
        self.send_tcp("Telnet <--> Serial Bridge by Elin\r\n")
        self.send_tcp(
            "************************************************\r\n")

        self.send_tcp("\r\n")
        self.send_tcp("You are now connected to console.\r\n")

    def send_tcp(self, data):
        self._socket.send(data.encode())

    def recv_tcp(self):
        return self._socket.recv(1024)

    def send_serial(self, data):
        data = clean_text(data)
        self._port.write_stream(data)

    def recv_serial(self):
        return self._observer.get(timeout=0.1)

    def close(self):
        self._socket.close()


class Telnet(object):

    def __init__(self, listen=23):

        self._listen = listen

        self.connection = None
        self.listener = None
        self.clist = []

        self.start_new_listener()
        self.thread = None

    def start_new_listener(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(('', self._listen))
        self.listener.listen()
        logger.info("Telnet.Start_new_listen OK")

    def __bool__(self):
        return True

    def close(self):
        self.thread_stop()
        self.clist = []
        logger.info("connect.Telnet closed")

    def run(self):
        while True:
            for conn in self.clist[:]:
                if isinstance(conn, Connection):
                    data = conn.recv_serial()
                    if data:
                        conn.send_tcp(data)

            ready = self.clist[:] # 加了[:]相当于新建一个实例

            if self.listener:
                ready.append(self.listener)

            ready = select.select(ready, ready, [], 2)[0]

            if self.stop_thread:
                for conn in self.clist:
                    conn.close()
                break

            for conn in ready:
                if conn is self.listener:
                    _socket, address = self.listener.accept()
                    conn = Connection(_socket, conf.port)
                    self.clist.append(conn)
                    conn.init_tcp()
                    conf.telnet_join = True

                    self.listener = None

                else:
                    data = conn.recv_tcp()

                    if data:
                        if data[0] == KEYBOARD.Ctrl_C: # 主动终端
                            conn.close()
                            self.clist.remove(conn)
                            self.start_new_listener()
                            conf.telnet_join = False

                        else:
                            conn.send_serial(data)

                    else:
                        # print("TCP connection closed.")
                        self.clist.remove(conn)
                        self.start_new_listener()
                        conf.telnet_join = False

    def thread_run(self):
        self.stop_thread = False
        th = threading.Thread(target=self.run)
        th.start()
        return th

    def thread_stop(self):
        self.stop_thread = True
