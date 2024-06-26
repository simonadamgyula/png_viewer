from typing import Literal

class Reader:
    def __init__(self, file):
        self.file = file
        self.remaining_byte = b''

    def read_bytes(self, n):
        return self.file.read(n)

    def read_bytes_as_int(self, n):
        return int.from_bytes(self.read_bytes(n), byteorder='big')

    def read_byte_list(self, n):
        return list(self.read_bytes(n))

    def read_bits(self, n):
        if n == 8:
            return self.read_bytes(1)

    @staticmethod
    def bytes_to_int(byte, byteorder: Literal["big"] | Literal["little"] = 'big'):
        return int.from_bytes(byte, byteorder=byteorder, signed=False)