from queue import Queue

class RecvSerialPort(object):
    """观察者模式"""

    def __init__(self):
        self._observers = []

    def add_observer(self, ob):
        self._observers.append(ob)

    def remove_observer(self, ob):
        self._observers.remove(ob)

    def notice(self, c):
        for i in self._observers:
            i.put(c)


class Observer(object):

    def __init__(self):
        self._queue = Queue()

    def put(self, c):
        self._queue.put(c)

    def get(self, timeout=0.1):
        return self._queue.get(timeout)

