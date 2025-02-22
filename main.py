import struct
import lz4.block

from readwrite import voxel_terrain
from readwrite import mip


class bcolors:
    HEADER = '\033[95m'
    GOOD = '\033[92m'
    ERROR = '\033[91m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'


class SubCellData:
    def __init__(self, data_type: str, data, meta_data):
        self.type = data_type
        self.original_data = data

        self.data = None
        self.meta_data = meta_data

    def decode(self, decode_func):
        self.data = decode_func(self.original_data, self.meta_data)

    def encode(self, encode_func=None):
        if not encode_func:
            return self.original_data
        return encode_func(self.data, self.meta_data)


class TileFile:
    MAGIC_KEY = 0x454C4954  # "TILE"

    def __init__(self, file_path):
        self.file_path = file_path
        self.header = None
        self.cell_headers = []
        self.world_data = []  # [cell_index][data_type][index]
        self.original_data = None  # Store the original file data for reconstruction

        self.read_write_functions = {
            "mip": (mip.read_mip, mip.write_mip),
        }

    def read_file(self):
        with open(self.file_path, "rb") as f:
            self.original_data = f.read()

        self.parse_header(self.original_data)
        self.parse_cell_headers(self.original_data)

        for index, cell_header in enumerate(self.cell_headers):
            cell_header_data = {}
            for data_type in cell_header:
                if data_type in self.read_write_functions:
                    read_func, write_func = self.read_write_functions[data_type]
                    cell_data = self.decode_cell_chunk(self.original_data, cell_header, data_type, read_func)

                else:
                    if index == 0:
                        print(f"{bcolors.WARNING}[WARN] Modification disabled | No Read/Write functions for '{data_type}'{bcolors.ENDC}")

                    cell_data = self.decode_cell_chunk(self.original_data, cell_header, data_type, None)

                cell_header_data[data_type] = cell_data
            self.world_data.append(cell_header_data)

        print(f"{bcolors.GOOD}[INFO] Loaded Tile. The following attributes are editable: {bcolors.ENDC}")
        for read_write in self.read_write_functions:
            print(f"{bcolors.GOOD} - {read_write}{bcolors.ENDC}")

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

        print(f"{bcolors.GOOD}[INFO] Parsed Header. Tile Version: {version}{bcolors.ENDC}")

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
        cell_format = "<6i 6i 6i i i i 4i 4i 4i 4i i i i i i i i i i i i i i i i i i i i i 4i 4i 4i 4i 4i 4i 4i 4i 4i i i i i"
        unpacked = struct.unpack(cell_format, cell_data)

        print(unpacked[96])

        return {
            "mip": {  # 6x (no count)
                "index": unpacked[0:6],
                "compressed": unpacked[6:12],
                "size": unpacked[12:18],
            },

            "clutter": {  # 1x (no count)
                "index": unpacked[18],
                "compressed": unpacked[19],
                "size": unpacked[20],
            },

            "assets": {  # 4x
                "count": unpacked[21:25],
                "index": unpacked[25:29],
                "compressed": unpacked[29:33],
                "size": unpacked[33:37],
            },

            "blueprint": {  # 1x
                "count": unpacked[37],
                "index": unpacked[38],
                "compressed": unpacked[39],
                "size": unpacked[40],
            },

            "node": {
                "count": unpacked[41],
                "index": unpacked[42],
                "compressed": unpacked[43],
                "size": unpacked[44],
            },

            "script": {
                "count": unpacked[45],
                "index": unpacked[46],
                "compressed": unpacked[47],
                "size": unpacked[48],
            },

            "prefab": {
                "count": unpacked[49],
                "index": unpacked[50],
                "compressed": unpacked[51],
                "size": unpacked[52],
            },

            "decal": {
                "count": unpacked[53],
                "index": unpacked[54],
                "compressed": unpacked[55],
                "size": unpacked[56],
            },

            "harvestable": {
                "count": unpacked[57:61],
                "index": unpacked[61:65],
                "compressed": unpacked[65:69],
                "size": unpacked[69:73],
            },

            "kinematics": {
                "count": unpacked[73:77],
                "index": unpacked[77:81],
                "compressed": unpacked[81:85],
                "size": unpacked[85:89],
            },

            "voxel_terrain": {
                "count": unpacked[89],
                "index": unpacked[90],
                "compressed": unpacked[91],
                "size": unpacked[92],
            }
        }

    @staticmethod
    def _decode_cell_chunk(data, index, size, compressed, count, header_name, parse_function):
        if index <= 0 or compressed <= 0:
            return index, size, compressed

        compressed_data = data[index:index + compressed]
        decompressed_data = lz4.block.decompress(compressed_data, uncompressed_size=size)

        meta = {"index": index, "compressed": compressed, "size": size, "count": count}
        sub_cell = SubCellData(header_name, decompressed_data, meta)

        if parse_function is not None:
            sub_cell.decode(parse_function)

        return sub_cell

    def decode_cell_chunk(self, data, cell_header, header_name, parse_function=None):
        cell_header_data = cell_header[header_name]

        sub_cells = []

        if type(cell_header_data["index"]) is tuple:
            for level in range(len(cell_header_data["index"])):
                index = cell_header_data["index"][level]
                size = cell_header_data["size"][level]
                compressed_size = cell_header_data["compressed"][level]
                count = None if "count" not in cell_header_data else cell_header_data["count"][level]

                sub_cells.append(
                    self._decode_cell_chunk(data, index, size, compressed_size, count, header_name, parse_function)
                )

        else:
            index = cell_header_data["index"]
            size = cell_header_data["size"]
            compressed_size = cell_header_data["compressed"]
            count = None if "count" not in cell_header_data else cell_header_data["count"]

            sub_cells.append(
                self._decode_cell_chunk(data, index, size, compressed_size, count, header_name, parse_function)
            )

        return sub_cells

    def write_header(self, new_data):
        new_data += struct.pack("<I", self.MAGIC_KEY)
        new_data += struct.pack("<I", self.header["version"])
        new_data += struct.pack("<16s", self.header["uuid"].encode())
        new_data += struct.pack("<Q", self.header["creator_id"])
        new_data += struct.pack("<I", self.header["width"])
        new_data += struct.pack("<I", self.header["height"])
        new_data += struct.pack("<I", self.header["cell_header_offset"])
        new_data += struct.pack("<I", self.header["cell_header_size"])
        new_data += struct.pack("<I", self.header["some_val1"])
        new_data += struct.pack("<I", self.header["some_val2"])
        new_data += struct.pack("<I", self.header["type"])
        return new_data

    @staticmethod
    def create_cell_header(header):
        cell_data = []  # Ensure its writing in the correct order
        for key in ("mip", "clutter", "assets", "blueprint", "node", "script", "prefab", "decal", "harvestable", "kinematics", "unknown_data", "voxel_terrain"):
            for value in ("count", "index", "compressed", "size"):
                if value in header[key]:
                    cell_data.append(header[key][value])

        cell_format = "<6i 6i 6i i i i 4i 4i 4i 4i i i i i i i i i i i i i i i i i i i i i 4i 4i 4i 4i 4i 4i 4i 4i 4i i i i i"
        return struct.pack(cell_format, *cell_data)



    def write_file(self, output_file_path):
        new_data = self.write_header(b"")

        if len(new_data) != self.header["cell_header_offset"]:
            raise ValueError("Header offset is incorrect, I have no setup for this :)")

        sub_cell_count = 0
        for i, _ in enumerate(self.cell_headers):
            for j in self.world_data[i]:
                for _ in self.world_data[i][j]:
                    sub_cell_count += 1

        sub_cells_processed = 0
        print(f"{bcolors.GOOD}[INFO] Processing... (0/{sub_cell_count}){bcolors.ENDC}", end="")
        for cell_index, cell_header in enumerate(self.cell_headers):
            for data_type in self.world_data[cell_index]:
                for sub_cell_index, sub_cell in enumerate(self.world_data[cell_index][data_type]):
                    if type(sub_cell) is not tuple:
                        multiple_sub_cells = type(cell_header[data_type]["index"]) is tuple

                        encode_func = None
                        if data_type in self.read_write_functions:
                            encode_func = self.read_write_functions[data_type][1]

                        raw_sub_cell_data = sub_cell.encode(encode_func)
                        compressed_cell_data = lz4.block.compress(raw_sub_cell_data)

                        if multiple_sub_cells:
                            cell_header[data_type]["compressed"] = list(cell_header[data_type]["compressed"])
                            cell_header[data_type]["compressed"][sub_cell_index] = compressed_cell_data
                        else:
                            cell_header[data_type]["compressed"] = compressed_cell_data

                    sub_cells_processed += 1

            header_data = self.create_cell_header(cell_header)

            print(f"\r{bcolors.GOOD}[INFO] Processing... ({sub_cells_processed}/{sub_cell_count}){bcolors.ENDC}", end="")

        print(f"\r{bcolors.GOOD}[INFO] Writing to... {output_file_path}{bcolors.ENDC}", end="")
        with open(output_file_path, "wb") as f:
            f.write(new_data)

        print(f"\r{bcolors.GOOD}[INFO] Saved to '{output_file_path}'{bcolors.ENDC}")


if __name__ == "__main__":
    tile_file = TileFile(r"tile\Dirt Race Track Tile.tile")
    tile_file.read_file()

    #tile_file.set_terrain_height(0, 0, 2)
    #tile_file.set_terrain_height(0, 1, 3)
    #tile_file.set_terrain_height(0, 2, 4)

    tile_file.write_file(r"test.tile")
    #load_test = TileFile(r"test.tile")
    #load_test.read_file()
