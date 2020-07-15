import threading
import queue
import logging
import json

from .errors import CommTimeoutError, CommClientError
from .interface.errors import InterfaceIOError
from .framing.errors import FramingDecodeError

log = logging.getLogger()


class JsonHelper:
    def send_json(self, data, client_id=None):
        tx_bytes = bytes(json.dumps(data), 'utf-8')
        self.send(tx_bytes, client_id=client_id)
    
    def recv_json(self, client_id=None):
        rx_bytes = self.recv(client_id=client_id)
        return json.loads(rx_bytes)

    def send_recv_json(self, data, client_id=None):
        self.send_json(data, client_id=client_id)
        return self.recv_json(client_id=client_id)


class CommWorker(JsonHelper):
    def __init__(self, interface, framing):
        self.interface = interface
        self.framing = framing

        self._queue = queue.Queue()
        self._client_queues = {}

        self.register_client(None)

    def register_client(self, client_id):
        self._client_queues.setdefault(client_id, queue.Queue())

    def start(self):
        self._thread = threading.Thread(target=self._worker)
        self._thread.setDaemon(True)
        self._thread.start()
    
    def send(self, data, client_id=None):
        if client_id not in self._client_queues:
            raise CommClientError('Client ID not registered')

        request = {
            'data': data,
            'client_id': client_id,
        }
        self._queue.put(request)

    def recv(self, client_id=None):
        client_queue = self._client_queues.get(client_id)
        if not client_queue:
            raise CommClientError('Client ID not registered')
        
        response = client_queue.get()
        
        error = response.get('error')
        if error:
            raise error
        data = response.get('data')
        return data

    def send_recv(self, data, client_id=None):
        self.send(data, client_id=client_id)
        return self.recv(client_id=client_id)
    
    def _worker(self):
        while True:
            request = self._queue.get()

            data = request.get('data')
            client_id = request.get('client_id')
            client_queue = self._client_queues.get(client_id)

            tx_bytes = self.framing.encode_frame(data)

            try:
                self.interface.write(tx_bytes)
            except InterfaceIOError as e:
                log.error(str(e))
                continue

            while True:
                try:
                    rx_bytes = self.interface.read()
                except InterfaceIOError as e:
                    log.error(str(e))
                    break

                if rx_bytes is None:
                    client_queue.put({'error': CommTimeoutError()})
                    break
                for byte in rx_bytes:
                    try:
                        data = self.framing.decode_frame(byte)
                        if data is None:
                            continue
                        client_queue.put({'data': data})
                        break
                    except FramingDecodeError as e:
                        log.warning(str(e))

                    
