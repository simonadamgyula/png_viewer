from chunk import Chunk
from reader import Reader

class PNG:
    def __init__(self, path):
        self.height = None
        self.bit_depth = None
        self.color_type = None
        self.compression = None
        self.filter_type = None
        self.interlace_method = None
        self.width = None

        self.file = Reader(open(path, 'rb'))
        self.chunks: list[Chunk] = []
        self.pixels: list[tuple[int, int, int]] = []

        self.check()

        self.read_chunks()
        self.read_header()
        self.read_pixel()

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

    def read_pixel(self):
        data = [chunk for chunk in self.chunks if chunk.chunk_type == b'IDAT'][0]
        print(data.data[0] << 2)
        print((120).to_bytes(1, byteorder='little'))

        red = data.data[:1]
        green = data.data[1:2]
        blue = data.data[2:3]
        print(red, green, blue)
