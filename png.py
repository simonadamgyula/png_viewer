import math

from chunk import Chunk
from reader import Reader, BytesReader
import pygame
import zlib

def byteint(byte):
    return Reader.bytes_to_int(byte, "big")


def extractBits(number, num, start_pos):
    binary = bin(number)[2:].zfill(8)
    return int(binary[start_pos:start_pos+num], 2)

def set_opacity(color: tuple[int, int, int], opacity: int) -> tuple[int, ...]:
    transparency = (opacity / 255) if opacity > 0 else 0
    return tuple(map(lambda x: int(x * transparency), color))

class PNG:
    def __init__(self, path):
        self.height = None
        self.bit_depth = None
        self.color_type = None
        self.compression = None
        self.filter_type = None
        self.interlace_method = None
        self.width = None
        self.decompressed: None | bytes = None
        self.palette: None | list[tuple[int, int, int]] = None
        self.transparency: None | int | tuple[int, int, int] | list[int] = None

        self.file = Reader(open(path, 'rb'))
        self.chunks: list[Chunk] = []
        self.pixels: list[tuple[int, int, int]] = []

        self.check()

        self.read_chunks()
        self.read_header()
        self.read_palette()
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

            if chunk.chunk_type == b'IEND':
                break

    def read_header(self):
        header = list(filter(lambda chunk: chunk.chunk_type == b'IHDR', self.chunks))[0]
        self.width = Reader.bytes_to_int(header.data[:4])
        self.height = Reader.bytes_to_int(header.data[4:8])
        self.bit_depth = Reader.bytes_to_int(header.data[8:9])
        self.color_type = Reader.bytes_to_int(header.data[9:10])
        self.compression = Reader.bytes_to_int(header.data[10:11])
        self.filter_type = Reader.bytes_to_int(header.data[11:12])
        self.interlace_method = Reader.bytes_to_int(header.data[12:13])

    def read_trns(self):
        trnss: list[Chunk] = list(filter(lambda chunk: chunk.chunk_type == b'tRNS', self.chunks))
        if not trnss:
            return

        trns = trnss[0]
        if self.color_type == 0:
            self.transparency = Reader.bytes_to_int(trns.data)
        if self.color_type == 2:
            self.transparency = tuple([Reader.bytes_to_int(trns.data[i:i+2]) for i in range(3)])
        if self.color_type == 3:
            self.transparency = [Reader.bytes_to_int(trns.data[i:i+1]) for i in range(trns.length)]

    def read_palette(self):
        palette_chunks: list[Chunk] = list(filter(lambda chunk: chunk.chunk_type == b'PLTE', self.chunks))
        if not palette_chunks:
            return

        palette_chunk = palette_chunks[0]
        data = palette_chunk.data
        self.palette = []
        for index in range(0, palette_chunk.length, 3):
            red = data[index]
            green = data[index + 1]
            blue = data[index + 2]

            self.palette.append((red, green, blue))

    def decompress(self):
        data_chunks: list[Chunk] = [chunk for chunk in self.chunks if chunk.chunk_type == b'IDAT']
        data = bytes()
        for chunk in data_chunks:
            data += chunk.data

        self.decompressed: bytes = zlib.decompress(data)

    def read(self):
        if self.color_type == 0:
            line_bytes = self.width
            pixel_step = 1
        elif self.color_type == 2:
            pixel_step = 3
            line_bytes = self.width * 3
        elif self.color_type == 3:
            pixel_step = 1
            line_bytes = self.width
        elif self.color_type == 4:
            pixel_step = 2
            line_bytes = self.width * 2
        elif self.color_type == 6:
            pixel_step = 4
            line_bytes = self.width * 4
        else:
            raise TypeError("wrong PNG color type")

        print("Processing image ...")

        scanline = 0
        index = 0
        self.scanlines.append([])
        filter_type = None
        reader = BytesReader(self.decompressed, self.bit_depth)
        while True:
            byte = reader.next_byte()
            if byte is None:
                break

            if filter_type is None:
                filter_type = int.from_bytes(byte, byteorder='little')
                continue

            unfiltered_byte = None

            prev_line = scanline - 1
            prev_index = (index - pixel_step) if self.bit_depth >= 8 and self.color_type != 0 else index - 1

            a = self.scanlines[scanline][prev_index] if prev_index >= 0 else 0
            b = self.scanlines[prev_line][index] if prev_line >= 0 else 0
            c = self.scanlines[prev_line][prev_index] if prev_index >= 0 and prev_line >= 0 else 0

            if filter_type == 0:
                unfiltered_byte = byteint(byte)
            if filter_type == 1:
                unfiltered_byte = (byteint(byte) + a) % 256
            if filter_type == 2:
                unfiltered_byte = (byteint(byte) + b) % 256
            if filter_type == 3:
                unfiltered_byte = (byteint(byte) + ((a + b) // 2)) % 256

            if filter_type == 4:
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

                unfiltered_byte = (byteint(byte) + pr) % 256

            for i in range(8 // self.bit_depth):
                bits = extractBits(unfiltered_byte, self.bit_depth, i * self.bit_depth)
                self.scanlines[scanline].append(bits)

            index += 8 // self.bit_depth

            if index == line_bytes:
                scanline += 1
                index = 0
                filter_type = None
                self.scanlines.append([])

        self.scanlines.pop()

    def get_pixel(self, x: int, y: int) -> tuple[int, ...]:
        if self.color_type == 0:
            color = self.scanlines[y][x]
            if self.transparency is None or self.transparency != color:
                return color, color, color

            return set_opacity((color, color, color), 0)
        if self.color_type == 2:
            px = x * 3
            color = self.scanlines[y][px], self.scanlines[y][px + 1], self.scanlines[y][px + 2]
            if self.transparency is None or self.transparency != color:
                return color

            return set_opacity(color, 0)
        if self.color_type == 3:
            index = self.scanlines[y][x]
            if self.transparency is None or len(self.transparency) <= index:
                return self.palette[index]

            return set_opacity(self.palette[index], self.transparency[index])
        if self.color_type == 4:
            px = x * 2
            color = self.scanlines[y][px]
            alpha = self.scanlines[y][px + 1]
            return set_opacity((color, color, color), alpha)
        if self.color_type == 6:
            px = x * 4
            return set_opacity((self.scanlines[y][px], self.scanlines[y][px + 1], self.scanlines[y][px + 2]), self.scanlines[y][px + 3])


    def show(self):
        pygame.init()
        pygame.display.set_caption("PNG Viewer")
        screen = pygame.display.set_mode((self.width, self.height), pygame.SRCALPHA)
        screen.fill("white")
        pygame.display.flip()

        for y in range(self.height):
            for x in range(self.width):
                color = self.get_pixel(x, y)
                screen.set_at((x, y), color)
            pygame.display.flip()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.flip()
