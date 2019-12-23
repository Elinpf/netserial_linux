import threading

import serialport
import window

window.init_crt()
serialport.init_serial()

threading.Thread(target=serialport.loop_read)


