import threading
import queue
import logging

from qupy.comm import common
from qupy.comm.common import CommBase
from qupy.comm.errors import CommError

from qupy.interface.errors import InterfaceIOError, InterfaceTimeoutError

from qupy.framing.errors import FramingDecodeError


log = logging.getLogger(__name__)


class CommClient(CommBase):
    def __init__(self, interface, framing):
        super().__init__(interface, framing)

        self._client_rx_queues = {}

        self.register_client(None)

    def register_client(self, client_id):
        self._client_rx_queues.setdefault(client_id, queue.Queue())

    def _before_worker_start(self):
        for k in self._client_rx_queues:
            self._tx_queue = queue.Queue()
            self._client_rx_queues[k] = queue.Queue()
    
    def send(self, message, client_id=None):
        if client_id not in self._client_rx_queues:
            raise CommError('Client ID not registered')

        self._send_to(self._tx_queue, message, client_id=client_id)

    def recv(self, client_id=None, data_format='binary'):
        rx_queue = self._client_rx_queues.get(client_id)
        if not rx_queue:
            raise CommError('Client ID not registered')
        
        return self._recv_from(rx_queue, data_format=data_format)

    def _worker(self):
        if self._is_stop():
            return True
           
        log.debug('Waiting for request...')
        try:
            request = self._tx_queue.get(timeout=1.0)
        except queue.Empty as e:
            return False

        message = request.get('message')
        client_id = request.get('client_id')
        rx_queue = self._client_rx_queues.get(client_id)

        tx_bytes = self.framing.encode_frame(message)
        log.debug('TX message: {}'.format(str(message)))

        try:
            self.interface.write(tx_bytes)
        except (InterfaceIOError, InterfaceTimeoutError) as e:
            log.error('TX error: {}'.format(str(e)))
            rx_queue.put({'error': e})
            return False

        self.framing.reset()

        while True:
            try:
                rx_bytes = self.interface.read()
            except (InterfaceIOError, InterfaceTimeoutError) as e:
                log.error('RX error: {}'.format(str(e)))
                rx_queue.put({'error': e})
                return False
            
            message = self._parse_rx_bytes(rx_bytes)
            if message is None:
                continue

            log.debug('RX message: {}'.format(str(message)))
            rx_queue.put({'message': message})
            break

        return False
