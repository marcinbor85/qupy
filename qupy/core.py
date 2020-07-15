import threading
import queue

from .errors import CommTimeoutError, CommClientError


class CommWorker:
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
    
    def _worker(self):
        while True:
            request = self._queue.get()

            data = request.get('data')
            client_id = request.get('client_id')
            client_queue = self._client_queues.get(client_id)

            tx_bytes = self.framing.encode_frame(data)
            self.interface.write(tx_bytes)

            while True:
                rx_bytes = self.interface.read()
                if rx_bytes is None:
                    client_queue.put({'error': CommTimeoutError()})
                    break
                for byte in rx_bytes:
                    data = self.framing.decode_frame(byte)
                    if data is None:
                        continue
                    client_queue.put({'data': data})
