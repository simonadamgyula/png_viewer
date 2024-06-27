import math

from chunk import Chunk
from reader import Reader
from bitstring import BitArray
import zlib

def byteint(byte):
    return Reader.bytes_to_int(byte, "big")

class PNG:
    def __init__(self, path):
        self.height = None
        self.bit_depth = None
        self.color_type = None
        self.compression = None
        self.filter_type = None
        self.interlace_method = None
        self.width = None
        self.decompressed = None

        self.file = Reader(open(path, 'rb'))
        self.chunks: list[Chunk] = []
        self.pixels: list[tuple[int, int, int]] = []

        self.check()

        self.read_chunks()
        self.read_header()
        self.decompress()


        self.scanlines = []

        self.read()

    def check(self):
        check_bytes = self.file.read_byte_list(8)
        return check_bytes == [137, 80, 78, 71, 13, 10, 26, 10]

    def read_chunks(self):
        while True:
            chunk = Chunk(self.file)
            self.chunks.append(chunk)
            print(chunk.chunk_type)

            if chunk.chunk_type == b'IEND':
                break

    def read_header(self):
        header = self.chunks[0]
        self.width = Reader.bytes_to_int(header.data[:4])
        self.height = Reader.bytes_to_int(header.data[4:8])
        self.bit_depth = Reader.bytes_to_int(header.data[8:9])
        self.color_type = Reader.bytes_to_int(header.data[9:10])
        self.compression = Reader.bytes_to_int(header.data[10:11])
        self.filter_type = Reader.bytes_to_int(header.data[11:12])
        self.interlace_method = Reader.bytes_to_int(header.data[12:13])

        print(self.width, self.height, self.bit_depth, self.color_type, self.compression, self.filter_type)

    def decompress(self):
        data: Chunk = [chunk for chunk in self.chunks if chunk.chunk_type == b'IDAT'][0]
        self.decompressed = zlib.decompress(data.data)
        print(self.decompressed[:100])

    def read(self):
        scanline = 0
        index = 0
        self.scanlines.append([])
        filter_type = None
        print("first")
        for i in range(len(self.decompressed)):
            byte = self.decompressed[i:i+1]

            if filter_type is None:
                filter_type = int.from_bytes(byte, byteorder='little')
                continue

            if filter_type == 0:
                self.scanlines[scanline].append(byteint(byte))
            if filter_type == 1:
                a = self.scanlines[scanline][index - 3] if index - 3 >= 0 else 0
                self.scanlines[scanline].append((byteint(byte) + a) % 256)
            if filter_type == 2:
                b = self.scanlines[scanline - 1][index]
                self.scanlines[scanline].append((byteint(byte) + b) % 256)
            if filter_type == 3:
                a = self.scanlines[scanline][index - 3] if index - 3 >= 0 else 0
                b = self.scanlines[scanline - 1][index]
                self.scanlines[scanline].append((byteint(byte) + math.floor((a + b) % 256) / 2) % 256)
            if filter_type == 4:
                a = self.scanlines[scanline][index - 3] if index - 3 >= 0 else 0
                b = self.scanlines[scanline - 1][index]
                c = self.scanlines[scanline - 1][index - 3] if index - 3 >= 0 else 0
                p = a + b - c
                pa = abs(p - a)
                pb = abs(p - b)
                pc = abs(p - c)
                if pa <= pb and pa <= pc:
                    pr = a
                elif pb <= pc:
                    pr = b
                else:
                    pr = c

                self.scanlines[scanline].append((byteint(byte) + pr) % 256)

            index += 1

            if index % 3 == 0 and index != 0:
                print(self.scanlines[scanline][index - 3], self.scanlines[scanline][index - 2], self.scanlines[scanline][index - 1])

            if index == self.width * 3:
                scanline += 1
                index = 0
                filter_type = None
                self.scanlines.append([])



