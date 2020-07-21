import threading
import queue
import logging

from qupy.comm import common
from qupy.comm.common import CommBase

from qupy.interface.errors import InterfaceIOError, InterfaceTimeoutError

from qupy.framing.errors import FramingDecodeError


log = logging.getLogger(__name__)


class CommServer(CommBase):
    def __init__(self, interface, framing):
        super().__init__(interface, framing)

    def _before_worker_start(self):
        self._rx_queue = queue.Queue()
        self._tx_queue = queue.Queue()

    def recv(self, data_format='binary', **kwargs):
        return self._recv_from(self._rx_queue, data_format=data_format)
    
    def send(self, message, **kwargs):
        self._send_to(self._tx_queue, message)

    def _worker(self):
            
        self.framing.reset()
        message = None

        while True:
            if self._is_stop():
                return True

            log.debug('Waiting for data...')
            try:
                rx_bytes = self.interface.read()
            except InterfaceTimeoutError as e:
                continue
            except InterfaceIOError as e:
                log.error('RX error: {}'.format(str(e)))
                self._rx_queue.put({'error': e})
                return False

            message = self._parse_rx_bytes(rx_bytes)
            if message is None:
                continue

            self._tx_queue = queue.Queue()

            log.debug('RX message: {}'.format(str(message)))
            self._rx_queue.put({'message': message})

            response = None
            while response is None:
                if self._is_stop():
                    return True
                try:
                    response = self._tx_queue.get(timeout=1.0)
                except queue.Empty as e:
                    log.warning('Request confirm timeout')

            message = response.get('message')

            tx_bytes = self.framing.encode_frame(message)
            log.debug('TX message: {}'.format(str(message)))

            try:
                self.interface.write(tx_bytes)
            except (InterfaceIOError, InterfaceTimeoutError) as e:
                log.error('TX error: {}'.format(str(e)))
                self._rx_queue.put({'error': e})
                return False
        
        return False


