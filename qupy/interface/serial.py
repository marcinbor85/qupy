import serial
import logging
import threading

from qupy.interface import AbstractInterface
from qupy.interface.errors import InterfaceIOError, InterfaceTimeoutError


log = logging.getLogger(__name__)


def require_connection(func):
    def _wrapper(self, *args, **kwargs):
        if not self._serial:
            raise InterfaceIOError('Serial port closed')
        return func(self, *args, **kwargs)
    return _wrapper


def handle_serialport_exceptions(func):
    def _wrapper(self, *args, **kwargs):
        try:
            ret = func(self, *args, **kwargs)
        except serial.SerialException as e:
            msg = str(e)
            log.error(msg)
            raise InterfaceIOError(str(e))

        return ret
    return _wrapper


class SerialPort(AbstractInterface):
    DEFAULT_PORT = '/dev/ttyUSB0'
    DEFAULT_BAUDRATE = 115200
    DEFAULT_TIMEOUT = 1.0

    def __init__(self, timeout: float=DEFAULT_TIMEOUT):
        self._serial = None
        self._timeout = timeout

    def open(self, port: str=DEFAULT_PORT, baudrate: int=DEFAULT_BAUDRATE):
        try:
            self._serial = serial.serial_for_url(port)
            self._serial.baudrate = baudrate
            self._serial.timeout = self._timeout
            self._serial.write_timeout = self._timeout
        except (serial.SerialException, ValueError) as e:
            raise InterfaceIOError(str(e))

    def close(self):
        log.info('Closing serial port...')
        if not self._serial:
            log.warning('Serial port already closed')
            return

        self._serial.close()
        self._serial = None

        log.info('Serial port closed')

    @handle_serialport_exceptions
    @require_connection
    def read(self):
        rx_bytes = self._serial.read()
        if len(rx_bytes) == 0:
            raise InterfaceTimeoutError('read timeout')

        log.debug('RX bytes: {}'.format(str(rx_bytes)))
        return rx_bytes

    @handle_serialport_exceptions
    @require_connection
    def write(self, bytes_buf):
        tx_size = 0
        total_size = len(bytes_buf)

        while tx_size < total_size:
            size = self._serial.write(bytes_buf[tx_size:])
            if size == 0:
                raise InterfaceTimeoutError('write timeout')
            tx_size += size
        
        log.debug('TX bytes: {}'.format(str(bytes_buf)))
