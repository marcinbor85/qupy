import unittest

from qupy.framing.slip import Slip

from qupy.comm.client import CommClient
from qupy.comm.errors import CommTimeoutError

from .common import EchoInterface


class TestSlipFraming(unittest.TestCase):

    def setUp(self):
        self.framing = Slip()
        self.interface = EchoInterface()
        self.comm = CommClient(self.interface, self.framing)
        self.comm.start()

    def test_send_and_recv(self):
        self.interface.enabled = True
        tx_data = b'\x01\x02\x03'
        self.comm.send(tx_data)
        rx_data = self.comm.recv()
        self.assertEqual(rx_data, tx_data)
    
    def test_send_recv(self):
        self.interface.enabled = True
        tx_data = b'\x01\x02\x03'
        rx_data = self.comm.send_recv(tx_data)
        self.assertEqual(rx_data, tx_data)
    
    def test_recv_timeout(self):
        self.interface.enabled = False
        tx_data = b'\x01\x02\x03'
        with self.assertRaises(CommTimeoutError):
            self.comm.send_recv(tx_data)

    def test_recv_format(self):
        self.interface.enabled = True
        tx_data = b'\x01\x02\x03'
        with self.assertRaises(TypeError):
            self.comm.send_recv(tx_data, data_format='unknown')
        with self.assertRaises(CommTimeoutError):
            self.comm.recv()

    def test_send_recv_json(self):
        self.interface.enabled = True
        tx_data = {"str": "test", "obj": {"list": [1, 2, 3], "id": 1}}
        rx_data = self.comm.send_recv(tx_data, data_format='json')
        self.assertEqual(rx_data, tx_data)

    def test_send_recv_string(self):
        self.interface.enabled = True
        tx_data = 'test string'
        rx_data = self.comm.send_recv(tx_data, data_format='string')
        self.assertEqual(rx_data, tx_data)

if __name__ == '__main__':
    unittest.main()
