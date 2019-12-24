import logging
from queue import Queue as queue_module

from data_type import AttribDict

conf = AttribDict()

kb = AttribDict()

window = AttribDict()
port = AttribDict()


# 日志
logging.basicConfig(format='%(asctime)-6s: - %(levelname)s - %(message)s', level=logging.DEBUG,
        filename="console.log")

logger = logging.getLogger('serialLogger')


# 队列
queue = queue_module()

