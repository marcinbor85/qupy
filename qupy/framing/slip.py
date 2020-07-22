from qupy.framing import AbstractFraming
from qupy.framing.errors import FramingDecodeError


class Slip(AbstractFraming):
    BYTE_START         = 0xC0
    BYTE_END           = 0xC1
    BYTE_ESCAPE        = 0xDB
    BYTE_ESCAPE_START  = 0xDC
    BYTE_ESCAPE_END    = 0xDD
    BYTE_ESCAPE_ESCAPE = 0xDE

    STATUS_START    = 0
    STATUS_DATABYTE = 1
    STATUS_ESCAPE   = 2
        
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.state = Slip.STATUS_START
        self.buf = bytearray()

    def encode_frame(self, bytes_buf: bytes):
        ret = bytearray()
        ret.append(Slip.BYTE_START)

        for b in bytes_buf:
            if b == Slip.BYTE_START:
                ret.append(Slip.BYTE_ESCAPE)
                ret.append(Slip.BYTE_ESCAPE_START)

            elif b == Slip.BYTE_END:
                ret.append(Slip.BYTE_ESCAPE)
                ret.append(Slip.BYTE_ESCAPE_END)

            elif b == Slip.BYTE_ESCAPE:
                ret.append(Slip.BYTE_ESCAPE)
                ret.append(Slip.BYTE_ESCAPE_ESCAPE)

            else:
                ret.append(b)

        ret.append(Slip.BYTE_END)

        return bytes(ret)
        
    def decode_frame(self, byte):
        ret = None

        if self.state == Slip.STATUS_START:
            if byte == Slip.BYTE_START:
                self.buf = bytearray()
                self.state = Slip.STATUS_DATABYTE
            else:
                raise FramingDecodeError('Unexpected data byte before frame start')

        elif self.state == Slip.STATUS_DATABYTE:
            if byte == Slip.BYTE_START:
                self.buf = bytearray()
                raise FramingDecodeError('Unexpected start byte before frame end')

            elif byte == Slip.BYTE_END:
                self.state = Slip.STATUS_START
                ret = bytes(self.buf)

            elif byte == Slip.BYTE_ESCAPE:
                self.state = Slip.STATUS_ESCAPE

            else:
                self.buf.append(byte)

        elif self.state == Slip.STATUS_ESCAPE:
            if byte == Slip.BYTE_ESCAPE_START:
                self.buf.append(Slip.BYTE_START)
                self.state = Slip.STATUS_DATABYTE

            elif byte == Slip.BYTE_ESCAPE_END:
                self.buf.append(Slip.BYTE_END)
                self.state = Slip.STATUS_DATABYTE

            elif byte == Slip.BYTE_ESCAPE_ESCAPE:
                self.buf.append(Slip.BYTE_ESCAPE)
                self.state = Slip.STATUS_DATABYTE
                
            else:
                self.state = Slip.STATUS_START
                raise FramingDecodeError('Unexpected escaped byte')

        return ret
