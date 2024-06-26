class Chunk:
    def __init__(self, file):
        self.length = file.read_bytes_as_int(4)
        self.chunk_type = file.read_bytes(4)
        self.data = file.read_bytes(self.length)
        self.crc = file.read_bytes(4)
