import logging
from data_type import AttribDict
from queue import Queue as queue_module
from observe import RecvSerialPort

conf = AttribDict()
import settings

# 日志
logging.basicConfig(format='%(asctime)-6s: - %(levelname)s - %(message)s', level=logging.DEBUG,
        filename="console.log")

logger = logging.getLogger('serialLogger')

logger.info("============= Start New Process =============")


# 队列
recv_serial = RecvSerialPort()
