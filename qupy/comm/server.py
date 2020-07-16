import threading
import queue
import logging

from qupy.comm import common
from qupy.comm.errors import CommTimeoutError, CommClientError

from qupy.interface.errors import InterfaceIOError

from qupy.framing.errors import FramingDecodeError


log = logging.getLogger()


class CommServer:
    def __init__(self, interface, framing):
        self.interface = interface
        self.framing = framing

        self._tx_queue = queue.Queue()
        self._client_rx_queues = {}

        self.register_client(None)

    def register_client(self, client_id):
        self._client_rx_queues.setdefault(client_id, queue.Queue())

    def start(self):
        self._thread = threading.Thread(target=self._worker)
        self._thread.setDaemon(True)
        self._thread.start()
    
    def _worker(self):
        while True:
            request = self._tx_queue.get()

            data = request.get('data')
            client_id = request.get('client_id')
            rx_queue = self._client_rx_queues.get(client_id)

            tx_bytes = self.framing.encode_frame(data)

            try:
                self.interface.write(tx_bytes)
            except InterfaceIOError as e:
                log.error(str(e))
                continue

            self.framing.reset()

            while True:
                try:
                    rx_bytes = self.interface.read()
                except InterfaceIOError as e:
                    log.error(str(e))
                    break

                if rx_bytes is None:
                    rx_queue.put({'error': CommTimeoutError()})
                    break
                for byte in rx_bytes:
                    try:
                        data = self.framing.decode_frame(byte)
                        if data is None:
                            continue
                        rx_queue.put({'data': data})
                        break
                    except FramingDecodeError as e:
                        log.warning(str(e))