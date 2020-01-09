# import queue
import multiprocessing as mp
import select

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
        # self._queue = queue.Queue()
        self._queue = mp.Queue()

    def put(self, c):
        self._queue.put(c)

    def get(self, timeout=None):
        """
        multiprocessing 的方法是在: 
        https://stackoverflow.com/questions/1123855/select-on-multiple-python-multiprocessing-queues

        还有一种是手动锁定，不需要使用select, 对windows方便
        https://stackoverflow.com/questions/17495877/python-how-to-wait-on-both-queue-and-a-socket-on-same-time
        """
        ready = select.select([self._queue._reader], [], [], timeout)[0]
        if ready:
            return self._queue.get_nowait()
        else:
            return ""

