import logging
import socket
import sys
import threading

from qupy.interface import AbstractInterface
from qupy.interface.errors import InterfaceIOError, InterfaceTimeoutError


log = logging.getLogger(__name__)


def require_connection(func):
    def _wrapper(self, *args, **kwargs):
        if not self._connection:
            raise InterfaceIOError('Connection not established')
        return func(self, *args, **kwargs)
    return _wrapper


def handle_socket_exceptions(func):
    def _wrapper(self, *args, **kwargs):
        try:
            ret = func(self, *args, **kwargs)
        except socket.error as e:
            msg = str(e)
            if msg == 'timed out':
                raise InterfaceTimeoutError(str(e))
            raise InterfaceIOError(str(e))
        except socket.timeout as e:
            raise InterfaceTimeoutError(str(e))

        return ret
    return _wrapper


class TcpSocketBase(AbstractInterface):
    DEFAULT_PORT = 8020
    DEFAULT_HOST = 'localhost'
    DEFAULT_RECV_TIMEOUT = 1.0

    DEFAULT_RECV_CHUNK_SIZE = 4096

    def __init__(self, timeout: float=DEFAULT_RECV_TIMEOUT):
        self._connection = None
        self._timeout = timeout

    def close(self):
        log.info('Closing connection...')
        if not self._connection:
            log.warning('Connection already closed')
            return

        self._close()
        self._connection = None

        log.info('Connection closed')
    
    @handle_socket_exceptions
    @require_connection
    def read(self):
        rx_bytes = self._connection.recv(TcpSocketBase.DEFAULT_RECV_CHUNK_SIZE)
        if len(rx_bytes) == 0:
            msg = 'Connection remotely closed'
            log.error(msg)
            raise InterfaceIOError(msg)

        log.debug('RX bytes: {}'.format(str(rx_bytes)))
        return rx_bytes

    @handle_socket_exceptions
    @require_connection
    def write(self, bytes_buf):
        tx_size = 0
        total_size = len(bytes_buf)

        while tx_size < total_size:
            size = self._connection.send(bytes_buf[tx_size:])
            if size <= 0:
                msg = 'Connection remotely closed'
                log.error(msg)
                raise InterfaceIOError(msg)

            tx_size += size
        
        log.debug('TX bytes: {}'.format(str(bytes_buf)))


class TcpSocketServer(TcpSocketBase):
    def __init__(self, timeout: float=TcpSocketBase.DEFAULT_RECV_TIMEOUT):
        super().__init__(timeout=timeout)
    
    def _close(self):
        self._connection.shutdown(socket.SHUT_RDWR)
        self._connection.close()

    def bind(self, host: str=TcpSocketBase.DEFAULT_HOST, port: int=TcpSocketBase.DEFAULT_PORT):

        self._server_address = (host, port, )

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self._server_address)
        self.sock.settimeout(None)
        self.sock.listen(1)

        log.info('Socket binded to: {}'.format(str(self._server_address)))
    
    def listen(self):

        log.info('Start listening on: {}'.format(str(self._server_address)))
        connection, client_address = self.sock.accept()
        connection.settimeout(self._timeout)
        log.info('Connection from: {}'.format(str(client_address)))

        self._connection = connection


class TcpSocketClient(TcpSocketBase):
    def __init__(self, timeout: float=TcpSocketBase.DEFAULT_RECV_TIMEOUT):
        super().__init__(timeout=timeout)
    
    def _close(self):
        self._connection.close()

    def connect(self, host: str=TcpSocketBase.DEFAULT_HOST, port: int=TcpSocketBase.DEFAULT_PORT):
        server_address = (host, port, )

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self._timeout)

        log.info('Connecting to: {}'.format(str(server_address)))
        try:
            self.sock.connect(server_address)
        except socket.error as e:
            log.error('Connecting error: {}'.format(str(e)))
            raise InterfaceIOError(str(e))

        log.info('Connected to: {}'.format(str(server_address)))
        self._connection = self.sock
