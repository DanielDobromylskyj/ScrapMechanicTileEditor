import struct
import lz4.block


class TileFile:
    MAGIC_KEY = 0x454C4954  # "TILE"

    def __init__(self, file_path):
        self.file_path = file_path
        self.header = None
        self.cell_headers = []
        self.terrain_data = []
        self.original_data = None  # Store the original file data for reconstruction

    def read_file(self):
        with open(self.file_path, "rb") as f:
            self.original_data = f.read()

        self.parse_header(self.original_data)
        self.parse_cell_headers(self.original_data)
        self.read_terrain(self.original_data)

    @staticmethod
    def decode_colour(colour):
        alpha = (colour >> 24) & 0xFF
        red = (colour >> 16) & 0xFF
        green = (colour >> 8) & 0xFF
        blue = colour & 0xFF

        return red, green, blue, alpha

    def parse_header(self, data):
        header_format = "<I I 16s Q I I I I I I I"
        unpacked = struct.unpack_from(header_format, data, 0)

        magic_key, version, uuid, creator_id, width, height, cell_header_offset, cell_header_size, some_val1, some_val2, v_type = unpacked

        if magic_key != self.MAGIC_KEY:  # Magic key is just "TILE" in binary form
            raise ValueError("Invalid .tile file: Missing MAGIC_KEY")

        self.header = {
            "version": version,
            "uuid": uuid.hex(),
            "creator_id": creator_id,
            "width": width,
            "height": height,
            "cell_header_offset": cell_header_offset,
            "cell_header_size": cell_header_size,
            "some_val1": some_val1,
            "some_val2": some_val2,
            "type": v_type,
        }

    def parse_cell_headers(self, data):
        offset = self.header["cell_header_offset"]
        cell_size = self.header["cell_header_size"]
        cell_count = self.header["width"] * self.header["height"]

        for _ in range(cell_count):
            cell_data = data[offset:offset + cell_size]
            cell_header = self.parse_cell_header(cell_data)
            self.cell_headers.append(cell_header)
            offset += cell_size

    @staticmethod
    def parse_cell_header(cell_data):
        cell_format = "<6i 6i 6i i i i 4i 4i 4i 4i i i i i i i i i 4i 4i 4i 4i 4i 4i 4i i i i i i i i i i i i i i i i i i i i i i i i i"
        unpacked = struct.unpack(cell_format, cell_data)

        return {
            "mip_index": unpacked[0:6],
            "mip_compressed_size": unpacked[6:12],
            "mip_size": unpacked[12:18],
        }

    def read_terrain(self, data):
        for cell_header in self.cell_headers:
            for mip_level in range(6):
                mip_index = cell_header["mip_index"][mip_level]
                mip_size = cell_header["mip_size"][mip_level]
                mip_compressed_size = cell_header["mip_compressed_size"][mip_level]

                if mip_index <= 0 or mip_compressed_size <= 0:
                    continue

                compressed_data = data[mip_index:mip_index + mip_compressed_size]
                decompressed_data = lz4.block.decompress(compressed_data, uncompressed_size=mip_size)

                height_data, color_data = self.parse_terrain_data(decompressed_data, mip_size)
                self.terrain_data.append({"height": height_data, "color": color_data})

    @staticmethod
    def parse_terrain_data(decompressed_data, chunk_size):
        height_map = []
        color_map = []

        for i in range(chunk_size // 8):
            offset = i * 8
            height = struct.unpack_from("<f", decompressed_data, offset)[0]
            color = struct.unpack_from("<I", decompressed_data, offset + 4)[0]
            height_map.append(height)
            color_map.append(color)

        return height_map, color_map

    def set_terrain_height(self, tile_index: int, height_index: int, height: float):
        self.terrain_data[tile_index]["height"][height_index] = height

    def write_file(self, output_file_path):
        new_data = bytearray(self.original_data)
        offset = self.header#cell_header_offset

        for cell_idx, cell_header in enumerate(self.cell_headers):
            for mip_level in range(6):
                mip_index = cell_header["mip_index"][mip_level]
                mip_compressed_size = cell_header["mip_compressed_size"][mip_level]

                if mip_index <= 0 or mip_compressed_size <= 0:
                    continue

                # Serialize and compress terrain data
                height_data = self.terrain_data[cell_idx]["height"]
                color_data = self.terrain_data[cell_idx]["color"]

                decompressed_data = b"".join(
                    struct.pack("<fI", height, color)
                    for height, color in zip(height_data, color_data)
                )
                compressed_data = lz4.block.compress(decompressed_data)

                # Update compressed size
                cell_header["mip_compressed_size"] = list(cell_header["mip_compressed_size"])
                cell_header["mip_compressed_size"][mip_level] = len(compressed_data)
                new_data[mip_index:mip_index + len(compressed_data)] = compressed_data

        with open(output_file_path, "wb") as f:
            f.write(new_data)


if __name__ == "__main__":
    tile_file = TileFile(r"tile\Dirt Race Track Tile.tile")
    tile_file.read_file()

    tile_file.set_terrain_height(0, 0, 2)
    tile_file.set_terrain_height(0, 1, 3)
    tile_file.set_terrain_height(0, 2, 4)

    tile_file.write_file(r"test.tile")
    load_test = TileFile(r"test.tile")
    load_test.read_file()
