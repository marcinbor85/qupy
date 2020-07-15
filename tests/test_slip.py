import unittest

from qupy.framing.slip import Slip


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
        self.assertEqual(self.framing.decode_frame(0xC0), None)
        self.assertEqual(self.framing.decode_frame(0x02), None)
        self.assertEqual(self.framing.decode_frame(0x03), None)
        self.assertEqual(self.framing.decode_frame(0xC1), b'\x02\x03')

        self.assertEqual(self.framing.decode_frame(0xC0), None)
        self.assertEqual(self.framing.decode_frame(0xDB), None)
        self.assertEqual(self.framing.decode_frame(0x01), None)
        self.assertEqual(self.framing.decode_frame(0x02), None)
        self.assertEqual(self.framing.decode_frame(0x03), None)
        self.assertEqual(self.framing.decode_frame(0xC1), None)

        self.assertEqual(self.framing.decode_frame(0xC0), None)
        self.assertEqual(self.framing.decode_frame(0x01), None)
        self.assertEqual(self.framing.decode_frame(0xC1), b'\x01')

if __name__ == '__main__':
    unittest.main()
