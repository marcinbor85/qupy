import unittest
import json

from qupy.framing.slip import Slip
from qupy.interface.tcp import TcpSocketClient, TcpSocketServer
from qupy.interface.errors import InterfaceTimeoutError, InterfaceIOError
from qupy.framing.errors import FramingDecodeError


class TestTcpInterface(unittest.TestCase):

    def setUp(self):
        self.tcp_server = TcpSocketServer()
        self.tcp_client = TcpSocketClient()

        self.tcp_server.bind()

        self.tcp_client.connect()
        self.tcp_server.listen()

        super().setUp()

    def tearDown(self):
        self.tcp_server.close()
        self.tcp_server.unbind()

        super().tearDown()

    def test_txrx_client(self):
        
        tx_buf = bytes([i % 256 for i in range(4000)])
        
        self.tcp_client.write(tx_buf)

        rx_buf = bytearray()
        while len(rx_buf) != len(tx_buf):
            rx_buf += self.tcp_server.read()
        self.assertEqual(tx_buf, rx_buf)

        with self.assertRaises(InterfaceTimeoutError):
            self.tcp_server.read()

        self.tcp_client.close()

    def test_txrx_server(self):

        tx_buf = bytes([255 - i % 256 for i in range(4000)])
        
        self.tcp_server.write(tx_buf)

        rx_buf = bytearray()
        while len(rx_buf) != len(tx_buf):
            rx_buf += self.tcp_client.read()
        self.assertEqual(tx_buf, rx_buf)

        with self.assertRaises(InterfaceTimeoutError):
            self.tcp_client.read()

        self.tcp_client.close()

    def test_server_close(self):

        self.tcp_server.close()

        with self.assertRaises(InterfaceIOError):
            self.tcp_client.read()
        
        self.tcp_client.close()
    
    def test_client_close(self):

        self.tcp_client.close()

        with self.assertRaises(InterfaceIOError):
            self.tcp_server.read()
        
        self.tcp_server.close()

if __name__ == '__main__':
    unittest.main()
