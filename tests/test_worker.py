import unittest

from qupy.framing.slip import Slip
from qupy.core import CommWorker
from qupy.interface import AbstractInterface


class EchoInterface(AbstractInterface):
    offset = 0
    data = bytearray()

    def read(self):
        if self.offset < len(self.data):
            byte = self.data[self.offset:self.offset+1]
            self.offset += 1
            return byte
        return None
    
    def write(self, bytes_buf):
        self.data = bytes_buf
        self.offset = 0


class TestSlipFraming(unittest.TestCase):

    def setUp(self):
        self.framing = Slip()
        self.interface = EchoInterface()
        self.comm = CommWorker(self.interface, self.framing)
        self.comm.start()

    def test_send_recv(self):
        tx_data = b'\x01\x02\x03'
        self.comm.send(tx_data)
        rx_data = self.comm.recv()
        self.assertEqual(self.interface.data, self.framing.encode_frame(tx_data))
        self.assertEqual(rx_data, tx_data)

if __name__ == '__main__':
    unittest.main()