import threading
import queue
import logging

from qupy.comm import common
from qupy.comm.errors import CommTimeoutError, CommClientError

from qupy.interface.errors import InterfaceIOError, InterfaceTimeoutError

from qupy.framing.errors import FramingDecodeError


log = logging.getLogger(__name__)


class CommClient:
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
    
    def send(self, data, client_id=None):
        if client_id not in self._client_rx_queues:
            raise CommClientError('Client ID not registered')

        if isinstance(data, bytes):
            data_format = 'binary'
        elif isinstance(data, str):
            data_format = 'string'
        else:
            data_format = 'json'

        tx_bytes = common.get_data_format_converter(data_format).get('encoder')(data)

        request = {
            'data': tx_bytes,
            'client_id': client_id,
        }
        self._tx_queue.put(request)

    def recv(self, client_id=None, data_format='binary'):
        rx_queue = self._client_rx_queues.get(client_id)
        if not rx_queue:
            raise CommClientError('Client ID not registered')
        
        response = rx_queue.get()
        
        error = response.get('error')
        if error:
            raise error

        rx_bytes = response.get('data')

        converter = common.get_data_format_converter(data_format)
        if not converter:
            raise TypeError('Unsupported data format')

        data = converter.get('decoder')(rx_bytes)
        return data

    def send_recv(self, data, client_id=None, data_format='binary'):
        self.send(data, client_id)
        return self.recv(client_id, data_format)
    
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
            except InterfaceTimeoutError as e:
                log.error(str(e))
                continue

            self.framing.reset()

            while True:
                try:
                    rx_bytes = self.interface.read()
                except InterfaceIOError as e:
                    log.error(str(e))
                    break
                except InterfaceTimeoutError as e:
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
