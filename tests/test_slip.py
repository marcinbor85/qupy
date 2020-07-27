import unittest
import json

from qupy.framing.slip import Slip
from qupy.framing.errors import FramingDecodeError


class TestSlipFraming(unittest.TestCase):

    def setUp(self):
        self.framing = Slip()

        super().setUp()

    def test_encode(self):
        self.assertEqual(self.framing.encode_frame(
            bytes(
                [
                ]
            )),
            bytes(
                [
                    Slip.BYTE_START,
                    Slip.BYTE_END
                ]
            )
        )
        self.assertEqual(self.framing.encode_frame(
            bytes(
                [
                    0x01, 0x02, 0x03
                ]
            )),
            bytes(
                [
                    Slip.BYTE_START,
                    0x01, 0x02, 0x03,
                    Slip.BYTE_END
                ]
            )
        )
        self.assertEqual(self.framing.encode_frame(
            bytes(
                [
                    Slip.BYTE_START, 0x01, Slip.BYTE_END, 0x02,
                    Slip.BYTE_ESCAPE, Slip.BYTE_ESCAPE_START, Slip.BYTE_ESCAPE_END, Slip.BYTE_ESCAPE_ESCAPE, 0x03
                ]
            )),
            bytes(
                [
                    Slip.BYTE_START,
                    Slip.BYTE_ESCAPE, Slip.BYTE_ESCAPE_START, 0x01, Slip.BYTE_ESCAPE, Slip.BYTE_ESCAPE_END, 0x02,
                    Slip.BYTE_ESCAPE, Slip.BYTE_ESCAPE_ESCAPE, Slip.BYTE_ESCAPE_START, Slip.BYTE_ESCAPE_END, Slip.BYTE_ESCAPE_ESCAPE, 0x03,
                    Slip.BYTE_END
                ]
            )
        )

    def test_decode(self):
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_START), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_END), b'')

        self.assertEqual(self.framing.decode_frame(Slip.BYTE_START), None)
        self.assertEqual(self.framing.decode_frame(0x01), None)
        self.assertEqual(self.framing.decode_frame(0x02), None)
        self.assertEqual(self.framing.decode_frame(0x03), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_END),
            bytes(
                [
                    0x01, 0x02, 0x03
                ]
            )
        )

        self.assertEqual(self.framing.decode_frame(Slip.BYTE_START), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_ESCAPE), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_ESCAPE_START), None)
        self.assertEqual(self.framing.decode_frame(0x01), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_ESCAPE), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_ESCAPE_END), None)
        self.assertEqual(self.framing.decode_frame(0x02), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_ESCAPE), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_ESCAPE_ESCAPE), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_ESCAPE_START), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_ESCAPE_END), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_ESCAPE_ESCAPE), None)
        self.assertEqual(self.framing.decode_frame(0x03), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_END),
            bytes(
                [
                    Slip.BYTE_START, 0x01, Slip.BYTE_END, 0x02,
                    Slip.BYTE_ESCAPE, Slip.BYTE_ESCAPE_START, Slip.BYTE_ESCAPE_END, Slip.BYTE_ESCAPE_ESCAPE, 0x03
                ]
            )
        )

        self.assertEqual(self.framing.decode_frame(Slip.BYTE_START), None)
        self.assertEqual(self.framing.decode_frame(0x01), None)
        with self.assertRaises(FramingDecodeError):
            self.framing.decode_frame(Slip.BYTE_START)
        self.assertEqual(self.framing.decode_frame(0x02), None)
        self.assertEqual(self.framing.decode_frame(0x03), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_END),
            bytes(
                [
                    0x02, 0x03
                ]
            )
        )

        self.assertEqual(self.framing.decode_frame(Slip.BYTE_START), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_ESCAPE), None)
        with self.assertRaises(FramingDecodeError):
            self.framing.decode_frame(0x01)
        with self.assertRaises(FramingDecodeError):
            self.framing.decode_frame(0x02)

        self.assertEqual(self.framing.decode_frame(Slip.BYTE_START), None)
        self.assertEqual(self.framing.decode_frame(0x01), None)
        self.assertEqual(self.framing.decode_frame(Slip.BYTE_END),
            bytes(
                [
                    0x01,
                ]
            )
        )

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
