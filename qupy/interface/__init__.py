class AbstractInterface:
    def read(self):
        raise NotImplementedError()
    
    def write(self, bytes_buf):
        raise NotImplementedError()
