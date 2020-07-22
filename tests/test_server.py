import time
import unittest

from qupy.framing.slip import Slip

from qupy.comm.server import CommServer
from qupy.comm.errors import CommError
from qupy.interface.errors import InterfaceTimeoutError

from .common import EchoInterface


class TestCommServer(unittest.TestCase):

    def setUp(self):
        self.framing = Slip()
        self.interface = EchoInterface()
        self.comm = CommServer(self.interface, self.framing)
        self.comm.start()

        super().setUp()
    
    def tearDown(self):
        self.comm.stop()

        super().tearDown()

    def test_recv_and_send(self):
        self.interface.enabled = True
        tx_msg = b'\x01\x02\x03'
        tx_data = self.framing.encode_frame(tx_msg)
        self.interface.write(tx_data)
        rx_data = self.comm.recv()
        self.assertEqual(rx_data, tx_msg)

        self.interface.enabled = False
        tx_msg = b'\x04\x05\x06'
        tx_data = self.framing.encode_frame(tx_msg)
        self.comm.send(tx_msg)
        rx_data = bytearray()
        time.sleep(1.0)
        self.comm.stop()
        self.interface.enabled = True
        while True:
            try:
                rx_data += self.interface.read()
            except InterfaceTimeoutError:
                break
        self.assertEqual(rx_data, tx_data)
    
    def test_recv_and_no_recv(self):
        self.interface.enabled = True
        tx_msg = b'\x01\x02\x03'
        tx_data = self.framing.encode_frame(tx_msg)
        self.interface.write(tx_data)
        rx_data = self.comm.recv()
        self.assertEqual(rx_data, tx_msg)

        self.interface.enabled = False
        self.comm.send(None)
        rx_data = bytearray()
        time.sleep(1.0)
        self.comm.stop()
        self.interface.enabled = True
        while True:
            try:
                rx_data += self.interface.read()
            except InterfaceTimeoutError:
                break
        self.assertEqual(rx_data, bytearray())

if __name__ == '__main__':
    unittest.main()
