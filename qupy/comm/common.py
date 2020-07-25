import json
import threading
import logging

from qupy.comm import common
from qupy.interface import AbstractInterface
from qupy.framing import AbstractFraming
from qupy.framing.errors import FramingDecodeError

log = logging.getLogger(__name__)


_DATA_FORMAT_CONVERTERS = {
    'binary': {
        'decoder': lambda rx_bytes: bytes(rx_bytes),
        'encoder': lambda tx_bytes: bytes(tx_bytes),
    },
    'string': {
        'decoder': lambda rx_bytes: rx_bytes.decode('utf-8'),
        'encoder': lambda string: bytes(string, 'utf-8'),
    },
    'json': {
        'decoder': lambda rx_bytes: json.loads(rx_bytes.decode('utf-8')),
        'encoder': lambda json_string: bytes(json.dumps(json_string), 'utf-8')
    }
}


def get_data_format_converter(data_format):
    return _DATA_FORMAT_CONVERTERS.get(data_format)


class CommBase:
    def __init__(self, interface: AbstractInterface, framing: AbstractFraming):
        self.interface = interface
        self.framing = framing

        self._stop_cond = threading.Condition()
        self._stop_flag = False
        self._thread = None
    
    def _before_worker_start(self):
        pass

    def start(self):
        log.debug('Starting...')

        with self._stop_cond:
            self._stop_flag = False

            self._before_worker_start()
                
            self._thread = threading.Thread(target=self._worker_loop)
            self._thread.setDaemon(True)
            self._thread.start()

    def stop(self):
        if self._thread is None:
            log.warning('Already stopped')
            return

        log.debug('Stopping...')

        self._stop_cond.acquire()
        self._stop_flag = True
        self._stop_cond.wait()
        self._stop_cond.release()
        self._thread = None
    
    def _send_to(self, tx_queue, message, **kwargs):
        if isinstance(message, bytes):
            data_format = 'binary'
        elif isinstance(message, str):
            data_format = 'string'
        else:
            data_format = 'json'

        frame_bytes = common.get_data_format_converter(data_format).get('encoder')(message) if message is not None else None

        request = dict(message=frame_bytes, **kwargs)
        tx_queue.put(request)

    def _recv_from(self, rx_queue, data_format='binary'):
        response = rx_queue.get()
        
        error = response.get('error')
        if error:
            raise error

        frame_bytes = response.get('message')

        converter = common.get_data_format_converter(data_format)
        if not converter:
            raise TypeError('Unsupported data format')

        message = converter.get('decoder')(frame_bytes)
        return message
    
    def _is_stop(self):
        self._stop_cond.acquire()
        if self._stop_flag:
            return True
        self._stop_cond.release()
        return False
    
    def _parse_rx_bytes(self, rx_bytes):
        message = None
        
        for byte in rx_bytes:
            try:
                message = self.framing.decode_frame(byte)
            except FramingDecodeError as e:
                log.warning(str(e))
            if message is not None:
                break

        return message
    
    def _worker(self):
        raise NotImplementedError('_worker method must be implemented')

    def _worker_loop(self):
        log.debug('Started')

        while not self._worker():
            pass

        self._stop_cond.notify()
        self._stop_cond.release()

        log.debug('Stopped')