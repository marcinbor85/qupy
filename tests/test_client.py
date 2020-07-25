import unittest

from qupy.framing.slip import Slip

from qupy.comm.client import CommClient
from qupy.comm.errors import CommError
from qupy.interface.errors import InterfaceTimeoutError

from .common import EchoInterface


class TestCommClient(unittest.TestCase):

    def setUp(self):
        self.framing = Slip()
        self.interface = EchoInterface()
        self.comm = CommClient(self.interface, self.framing)
        self.comm.start()

        super().setUp()
    
    def tearDown(self):
        self.comm.stop()

        super().tearDown()

    def test_send_and_recv(self):
        self.interface.enabled = True
        tx_data = b'\x01\x02\x03'
        self.comm.send(tx_data)
        rx_data = self.comm.recv()
        self.assertEqual(rx_data, tx_data)
    
    def test_ask(self):
        self.interface.enabled = True
        tx_data = b'\x01\x02\x03'
        rx_data = self.comm.ask(tx_data)
        self.assertEqual(rx_data, tx_data)
    
    def test_ask_timeout(self):
        self.interface.enabled = False
        tx_data = b'\x01\x02\x03'
        with self.assertRaises(InterfaceTimeoutError):
            self.comm.ask(tx_data)

    def test_ask_format(self):
        self.interface.enabled = True
        tx_data = b'\x01\x02\x03'
        with self.assertRaises(TypeError):
            self.comm.ask(tx_data, data_format='unknown')

    def test_ask_json(self):
        self.interface.enabled = True
        tx_data = {"str": "test", "obj": {"list": [1, 2, 3], "id": 1}}
        rx_data = self.comm.ask(tx_data, data_format='json')
        self.assertEqual(rx_data, tx_data)

    def test_ask_string(self):
        self.interface.enabled = True
        tx_data = 'test string'
        rx_data = self.comm.ask(tx_data, data_format='string')
        self.assertEqual(rx_data, tx_data)

if __name__ == '__main__':
    unittest.main()
