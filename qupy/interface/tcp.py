import logging
import socket
import sys

from qupy.interface import AbstractInterface
from qupy.interface.errors import InterfaceIOError, InterfaceTimeoutError


log = logging.getLogger(__name__)


def require_open_connection(func):
    def _wrapper(self, *args, **kwargs):
        if not self._connection:
            raise InterfaceIOError('Connection not established')
        return func(self, *args, **kwargs)
    return _wrapper


def require_close_connection(func):
    def _wrapper(self, *args, **kwargs):
        if self._connection:
            raise InterfaceIOError('Connection already opened')
        return func(self, *args, **kwargs)
    return _wrapper


class TcpSocket(AbstractInterface):
    DEFAULT_PORT = 8030
    DEFAULT_HOST = 'localhost'
    DEFAULT_RECV_TIMEOUT = 1.0

    DEFAULT_RECV_CHUNK_SIZE = 4096

    SOCKET_TYPE_SERVER = 1
    SOCKET_TYPE_CLIENT = 2

    def __init__(self, timeout: float=DEFAULT_RECV_TIMEOUT):
        self._connection = None
        self._client_address = None
        self._socket_type = None
        self._timeout = timeout

    @require_close_connection
    def connect(self, host: str=DEFAULT_HOST, port: int=DEFAULT_PORT):
        server_address = (host, port, )

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self._timeout)
        self._socket_type = TcpSocket.SOCKET_TYPE_CLIENT

        log.info('Connecting to: {}'.format(str(server_address)))
        try:
            self.sock.connect(server_address)
        except socket.error as e:
            raise InterfaceIOError(str(e))

        log.info('Connected to: {}'.format(str(server_address)))
        self._connection = self.sock

    @require_open_connection
    def close(self):
        if self._socket_type == TcpSocket.SOCKET_TYPE_SERVER:
            self._connection.close()
            self._connection = None
            self.sock.close()
        elif self._socket_type == TcpSocket.SOCKET_TYPE_CLIENT:
            self._connection = None
            self.sock.close()

    @require_close_connection
    def listen(self, host: str=DEFAULT_HOST, port: int=DEFAULT_PORT):

        server_address = (host, port, )

        if self._socket_type != TcpSocket.SOCKET_TYPE_SERVER:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(server_address)
            self.sock.settimeout(None)
            self.sock.listen(1)

            self._socket_type = TcpSocket.SOCKET_TYPE_SERVER

        log.info('Start listening on: {}'.format(str(server_address)))
        self._connection, client_address = self.sock.accept()
        self._connection.settimeout(self._timeout)
        log.info('Incomming connection from: {}'.format(str(client_address)))
    
    @require_open_connection
    def read(self):
        try:
            rx_bytes = self._connection.recv(TcpSocket.DEFAULT_RECV_CHUNK_SIZE)
        except socket.error as e:
            raise InterfaceIOError(str(e))
        except socket.timeout as e:
            raise InterfaceTimeoutError(str(e))
    
        if len(rx_bytes) == 0:
            raise InterfaceIOError('Socket closed')

        return rx_bytes

    @require_open_connection
    def write(self, bytes_buf):
        tx_size = 0
        total_size = len(bytes_buf)
        try:
            while tx_size < total_size:
                size = self._connection.send(bytes_buf[tx_size:])
                tx_size += size
        except socket.error as e:
            raise InterfaceIOError(str(e))
        except socket.timeout as e:
            raise InterfaceTimeoutError(str(e))

        return tx_size
