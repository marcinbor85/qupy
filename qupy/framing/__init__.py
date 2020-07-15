
class AbstractFraming:

    def encode_frame(self, bytes_buf):
        raise NotImplementedError()
        
    def decode_frame(self, byte):
        raise NotImplementedError()