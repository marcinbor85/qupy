import unittest
import json

from qupy.framing.slip import Slip
from qupy.interface.serial import SerialPort
from qupy.interface.errors import InterfaceTimeoutError, InterfaceIOError
from qupy.framing.errors import FramingDecodeError


class TestTcpInterface(unittest.TestCase):

    def setUp(self):
        self.serial = SerialPort()
        self.serial.open('loop://')

        super().setUp()

    def tearDown(self):
        self.serial.close()

        super().tearDown()

    def test_txrx(self):
        tx_buf = bytes([i % 256 for i in range(4000)])
        
        self.serial.write(tx_buf)

        rx_buf = bytearray()
        while len(rx_buf) != len(tx_buf):
            rx_buf += self.serial.read()
        self.assertEqual(tx_buf, rx_buf)
    
    def test_timeout(self):
        with self.assertRaises(InterfaceTimeoutError):
            self.serial.read()

    def test_close_error(self):
        self.serial.close()

        with self.assertRaises(InterfaceIOError):
            self.serial.read()
        with self.assertRaises(InterfaceIOError):
            self.serial.write(b'123')

if __name__ == '__main__':
    unittest.main()
