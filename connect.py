from data import logger
import socket
import select
import threading
from data import conf


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
        don't want linemode
        don't want echo
        """

        data = chr(255) + chr(254) + chr(34)
        self.send_tcp(data)

        data = chr(255) + chr(254) + chr(1)
        self.send_tcp(data)

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
        self._port.write_stream(data)

    def recv_serial(self):
        return self._observer.get(timeout=0.1)


class Telnet(object):

    def __init__(self, listen=33):

        self._listen = listen

        self.connection = None
        self.listener = None
        self.clist = []

        self.start_new_listener()

    def start_new_listener(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(('127.0.0.1', self._listen))
        self.listener.listen()
        logger.info("Telnet.Start_new_listen OK")

    def __bool__(self):
        return True

    def run_(self):
        logger.debug('Telnet.run:  Start to Run')
        while True:
            # 当从串口收到了信息
            for conn in self.clist:
                if isinstance(conn, Connection):
                    data = conn.recv_serial()
                    if data:
                        self.connection.send_tcp(data)

            ready = self.clist
            if self.listener:
                ready.append(self.listener)

            ready = select.select(ready, [], [], 0.1)[0]

            logger.debug('Telnet.run self.clist => %s' % ready)
            for conn in ready:

                if conn is self.listener:
                    logger.debug('In')
                    socket, address = self.listener.accept()

                    c = Connection(socket, conf.port)
                    c.init_tcp()
                    self.clist.append(c)
                    logger.debug('Telnet append(%s)' % type(c))

                    self.listener = None  # 不需要了
                    logger.info("Telnet: init connection")

                else:
                    logger.debug('Telnet.run: conn => %s' % type(conn))
                    data = conn.recv_tcp()
                    if not data:
                        logger.info("Telnet Close, restart")
                        self.clist.remove(conn)
                        self.start_new_listener()

                    else:
                        conn.send_serial(data)

    def run(self):

        while True:
            # 当从串口收到了信息
            for conn in self.clist:
                if isinstance(conn, Connection):
                    data = conn.recv_serial()
                    if data:
                        conn.send_tcp(data)

            ready = self.clist[:]

            if self.listener is not None:
                self.clist.append(self.listener)

            ready = select.select(ready, [], [], 0.1)[0]

            for conn in ready:
                # 当还是linsten 的时候，需要连接
                if conn is self.listener:
                    socket, address = self.listener.accept()
                    cn = Connection(socket, conf.port)
                    cn.init_tcp()
                    self.clist.append(cn)
                    self.listener = None


                elif isinstance(conn, Connection):
                    data = conn.recv_tcp()
                    if not data:
                        logger.info('Telnet Close, restart')
                        self.clist.clear()
                        self.start_new_listener()

                    else:
                        conn.send_serial(data)

    def thread_run(self):
        return threading.Thread(target=self.run)
