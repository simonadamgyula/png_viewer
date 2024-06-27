from typing import Literal

class Reader:
    def __init__(self, file):
        self.file = file
        self.remaining_byte = b''

    def read_bytes(self, n) -> bytes:
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

class BytesReader:
    def __init__(self, byte_string: bytes, bit_depth: Literal[2] | Literal[4] | Literal[8] | Literal[16] = 8):
        self.byte_string = byte_string
        self.bit_depth = bit_depth
        self.current_byte = None
        self.byte_index = 0
        self.remaining_bits = 0
        self.in_byte_index = 0

    def next(self):
        if self.remaining_bits == 0:
            self.current_byte = self.byte_string[self.byte_index]
            self.in_byte_index = 0
            self.byte_index += 1
            self.remaining_bits = 8
            if self.byte_index >= len(self.byte_string):
                print(self.byte_index)
                return None

        binary = bin(self.current_byte)[2:].zfill(self.bit_depth)
        end = len(binary) - self.in_byte_index
        start = end - self.bit_depth

        self.in_byte_index += self.bit_depth
        self.remaining_bits = len(binary) - self.in_byte_index

        return self.bitstring_to_bytes(binary[start:end+1])

    @staticmethod
    def bitstring_to_bytes(s):
        v = int(s, 2)
        b = bytearray()
        while v:
            b.append(v & 0xff)
            v >>= 8
        return bytes(b[::-1])



