import queue

from qupy.interface import AbstractInterface
from qupy.interface.errors import InterfaceTimeoutError

class EchoInterface(AbstractInterface):
    enabled = True

    def __init__(self):
        self.queue = queue.Queue()

    def read(self):
        if not self.enabled:
            raise InterfaceTimeoutError('echo interface timeout: interface disabled')

        try:
            rx_char = self.queue.get_nowait()    
        except queue.Empty:
            raise InterfaceTimeoutError('echo interface timeout: empty queue')
    
        return bytes([rx_char])

    def write(self, bytes_buf):
        for b in bytes_buf:
            self.queue.put(b)