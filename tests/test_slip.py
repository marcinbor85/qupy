import unittest
import json

from qupy.framing.slip import Slip
from qupy.framing.errors import FramingDecodeError


class TestSlipFraming(unittest.TestCase):

    def setUp(self):
        self.framing = Slip()

    def test_encode(self):
        self.assertEqual(self.framing.encode_frame(b''), b'\xc0\xc1')
        self.assertEqual(self.framing.encode_frame(b'\x01\x02\x03'), b'\xc0\x01\x02\x03\xc1')
        self.assertEqual(self.framing.encode_frame(b'\xc0\x01\xc1\x02\xdb\xdc\xdd\xde\x03'), b'\xc0\xdb\xdc\x01\xdb\xdd\x02\xdb\xde\xdc\xdd\xde\x03\xc1')

    def test_decode(self):
        self.assertEqual(self.framing.decode_frame(0xC0), None)
        self.assertEqual(self.framing.decode_frame(0xC1), b'')

        self.assertEqual(self.framing.decode_frame(0xC0), None)
        self.assertEqual(self.framing.decode_frame(0x01), None)
        self.assertEqual(self.framing.decode_frame(0x02), None)
        self.assertEqual(self.framing.decode_frame(0x03), None)
        self.assertEqual(self.framing.decode_frame(0xC1), b'\x01\x02\x03')

        self.assertEqual(self.framing.decode_frame(0xC0), None)
        self.assertEqual(self.framing.decode_frame(0xDB), None)
        self.assertEqual(self.framing.decode_frame(0xDC), None)
        self.assertEqual(self.framing.decode_frame(0x01), None)
        self.assertEqual(self.framing.decode_frame(0xDB), None)
        self.assertEqual(self.framing.decode_frame(0xDD), None)
        self.assertEqual(self.framing.decode_frame(0x02), None)
        self.assertEqual(self.framing.decode_frame(0xDB), None)
        self.assertEqual(self.framing.decode_frame(0xDE), None)
        self.assertEqual(self.framing.decode_frame(0xDC), None)
        self.assertEqual(self.framing.decode_frame(0xDD), None)
        self.assertEqual(self.framing.decode_frame(0xDE), None)
        self.assertEqual(self.framing.decode_frame(0x03), None)
        self.assertEqual(self.framing.decode_frame(0xC1), b'\xc0\x01\xc1\x02\xdb\xdc\xdd\xde\x03')

        self.assertEqual(self.framing.decode_frame(0xC0), None)
        self.assertEqual(self.framing.decode_frame(0x01), None)
        with self.assertRaises(FramingDecodeError):
            self.framing.decode_frame(0xC0)
        self.assertEqual(self.framing.decode_frame(0x02), None)
        self.assertEqual(self.framing.decode_frame(0x03), None)
        self.assertEqual(self.framing.decode_frame(0xC1), b'\x02\x03')

        self.assertEqual(self.framing.decode_frame(0xC0), None)
        self.assertEqual(self.framing.decode_frame(0xDB), None)
        with self.assertRaises(FramingDecodeError):
            self.framing.decode_frame(0x01)
        with self.assertRaises(FramingDecodeError):
            self.framing.decode_frame(0x02)

        self.assertEqual(self.framing.decode_frame(0xC0), None)
        self.assertEqual(self.framing.decode_frame(0x01), None)
        self.assertEqual(self.framing.decode_frame(0xC1), b'\x01')

    def test_json(self):
        tx_data = {'str': 'test', 'obj': {'list': [1, 2, 3], 'id': 1}}
        tx_bytes = bytes(json.dumps(tx_data), 'utf-8')
        frame = self.framing.encode_frame(tx_bytes)
        for b in frame:
            r = self.framing.decode_frame(b)
        rx_data = json.loads(r)
        self.assertEqual(tx_data, rx_data)

if __name__ == '__main__':
    unittest.main()
