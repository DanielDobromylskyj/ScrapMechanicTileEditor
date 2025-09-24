import struct
import lz4.block

from .sub_tile import SubCellData

from .readwrite import mip
from .readwrite import assetList


class bcolors:
    HEADER = '\033[95m'
    GOOD = '\033[92m'
    BLUE = '\033[94m'
    ERROR = '\033[91m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'


class TileFile:
    MAGIC_KEY = 0x454C4954  # "TILE"
    CELL_HEADER_SIZE = 97
    CELL_DATA_SIZE = 388

    def __init__(self, file_path):
        self.file_path = file_path
        self.header = None
        self.cell_headers = []
        self.world_data = []  # [cell_index][data_type][index]
        self.original_data = None  # Store the original file data for reconstruction

        self.read_write_functions = {
            "mip": (mip.read_mip, mip.write_mip),
            "assets": (assetList.read_assetList, assetList.write_assetList),
        }

        if self.file_path:
            self.read_file()

    def read_file(self, raw_input_bytes: bytes | bytearray | None =None):
        if not raw_input_bytes:
            with open(self.file_path, "rb") as f:
                self.original_data = f.read()
        else:
            self.original_data = raw_input_bytes

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

    def parse_cell_header(self, cell_data):
        cell_format = "<6i 6i 6i i i i 4i 4i 4i 4i i i i i i i i i i i i i i i i i i i i i 4i 4i 4i 4i 4i 4i 4i 4i 4i i i i i"
        unpacked = struct.unpack(cell_format, cell_data)

        if len(unpacked) != self.CELL_HEADER_SIZE:
            raise ValueError("Invalid .tile file: Cell Header size mismatch")

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

            "unknown": {
                "count": unpacked[89],
                "index": unpacked[90],
                "compressed": unpacked[91],
                "size": unpacked[92],
            },

            "voxel_terrain": {
                "count": unpacked[93],
                "index": unpacked[94],
                "compressed": unpacked[95],
                "size": unpacked[96],
            }
        }

    def _decode_cell_chunk(self, data, index, size, compressed, count, header_name, parse_function):
        if index <= 0 or compressed <= 0:
            return index, size, compressed

        compressed_data = data[index:index + compressed]

        try:

            decompressed_data = lz4.block.decompress(compressed_data, uncompressed_size=size)
        except:
            print("Error decompressing data", index, size, compressed, header_name)
            raise

        meta = {"index": index, "compressed": compressed, "size": size, "count": count}
        sub_cell = SubCellData(header_name, decompressed_data, meta, self.header["version"])

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
        new_data += struct.pack("<16s", bytes.fromhex(self.header["uuid"]))
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
        cell_data = [
            header["mip"]["index"][0], header["mip"]["index"][1], header["mip"]["index"][2], header["mip"]["index"][3], header["mip"]["index"][4], header["mip"]["index"][5],
            header["mip"]["compressed"][0], header["mip"]["compressed"][1], header["mip"]["compressed"][2], header["mip"]["compressed"][3], header["mip"]["compressed"][4], header["mip"]["compressed"][5],
            header["mip"]["size"][0], header["mip"]["size"][1], header["mip"]["size"][2], header["mip"]["size"][3], header["mip"]["size"][4], header["mip"]["size"][5],

            header["clutter"]["index"],
            header["clutter"]["compressed"],
            header["clutter"]["size"],

            header["assets"]["count"][0], header["assets"]["count"][1], header["assets"]["count"][2], header["assets"]["count"][3],
            header["assets"]["index"][0], header["assets"]["index"][1], header["assets"]["index"][2], header["assets"]["index"][3],
            header["assets"]["compressed"][0], header["assets"]["compressed"][1], header["assets"]["compressed"][2], header["assets"]["compressed"][3],
            header["assets"]["size"][0], header["assets"]["size"][1], header["assets"]["size"][2], header["assets"]["size"][3],

            header["blueprint"]["count"],
            header["blueprint"]["index"],
            header["blueprint"]["compressed"],
            header["blueprint"]["size"],

            header["node"]["count"],
            header["node"]["index"],
            header["node"]["compressed"],
            header["node"]["size"],

            header["script"]["count"],
            header["script"]["index"],
            header["script"]["compressed"],
            header["script"]["size"],

            header["prefab"]["count"],
            header["prefab"]["index"],
            header["prefab"]["compressed"],
            header["prefab"]["size"],

            header["decal"]["count"],
            header["decal"]["index"],
            header["decal"]["compressed"],
            header["decal"]["size"],

            header["harvestable"]["count"][0], header["harvestable"]["count"][1], header["harvestable"]["count"][2], header["harvestable"]["count"][3],
            header["harvestable"]["index"][0], header["harvestable"]["index"][1], header["harvestable"]["index"][2], header["harvestable"]["index"][3],
            header["harvestable"]["compressed"][0], header["harvestable"]["compressed"][1], header["harvestable"]["compressed"][2], header["harvestable"]["compressed"][3],
            header["harvestable"]["size"][0], header["harvestable"]["size"][1], header["harvestable"]["size"][2], header["harvestable"]["size"][3],

            header["kinematics"]["count"][0], header["kinematics"]["count"][1], header["kinematics"]["count"][2], header["kinematics"]["count"][3],
            header["kinematics"]["index"][0], header["kinematics"]["index"][1], header["kinematics"]["index"][2], header["kinematics"]["index"][3],
            header["kinematics"]["compressed"][0], header["kinematics"]["compressed"][1], header["kinematics"]["compressed"][2], header["kinematics"]["compressed"][3],
            header["kinematics"]["size"][0], header["kinematics"]["size"][1], header["kinematics"]["size"][2], header["kinematics"]["size"][3],

            header["unknown"]["count"],
            header["unknown"]["index"],
            header["unknown"]["compressed"],
            header["unknown"]["size"],

            header["voxel_terrain"]["count"],
            header["voxel_terrain"]["index"],
            header["voxel_terrain"]["compressed"],
            header["voxel_terrain"]["size"]
        ]

        cell_format = "<6i 6i 6i i i i 4i 4i 4i 4i i i i i i i i i i i i i i i i i i i i i 4i 4i 4i 4i 4i 4i 4i 4i 4i i i i i"
        return struct.pack(cell_format, *cell_data)

    def write_file(self, output_file_path):
        print(f"{bcolors.GOOD}[INFO] Creating Tile Header... {bcolors.ENDC}", end="")
        new_data = self.write_header(b"")

        if len(new_data) != self.header["cell_header_offset"]:
            raise ValueError("Header offset is incorrect, I have no setup for this :)")

        sub_cell_count = 0
        for i, _ in enumerate(self.cell_headers):
            for j in self.world_data[i]:
                for _ in self.world_data[i][j]:
                    sub_cell_count += 1

        print(f"\r{bcolors.GOOD}[INFO] Blocking Space... {bcolors.ENDC}", end="")

        # block out cell header space
        new_data += ("X" * (self.CELL_DATA_SIZE * len(self.cell_headers))).encode()

        data_blob_offset = len(new_data)
        data_blob = b""

        sub_cells_processed = 0
        print(f"\r{bcolors.GOOD}[INFO] Processing... (0/{sub_cell_count}){bcolors.ENDC}", end="")
        for cell_index, cell_header in enumerate(self.cell_headers):
            for data_type in self.world_data[cell_index]:
                for sub_cell_index, sub_cell in enumerate(self.world_data[cell_index][data_type]):
                    if type(sub_cell) is not tuple:
                        multiple_sub_cells = type(cell_header[data_type]["index"]) is not int

                        encode_func = None
                        if data_type in self.read_write_functions:
                            encode_func = self.read_write_functions[data_type][1]

                        raw_sub_cell_data = sub_cell.encode(encode_func)
                        compressed_cell_data = lz4.block.compress(raw_sub_cell_data, mode="high_compression", store_size=False)

                        if multiple_sub_cells:
                            if type(cell_header[data_type]["index"]) is tuple:
                                cell_header[data_type]["index"] = list(cell_header[data_type]["index"])

                            if type(cell_header[data_type]["compressed"]) is tuple:
                                cell_header[data_type]["compressed"] = list(cell_header[data_type]["compressed"])

                            if type(cell_header[data_type]["size"]) is tuple:
                                cell_header[data_type]["size"] = list(cell_header[data_type]["size"])

                            if "count" in cell_header[data_type]:
                                if type(cell_header[data_type]["count"]):
                                    cell_header[data_type]["count"] = list(cell_header[data_type]["count"])

                                cell_header[data_type]["count"][sub_cell_index] = sub_cell.meta_data["count"]


                            cell_header[data_type]["index"][sub_cell_index] = len(data_blob) + data_blob_offset
                            cell_header[data_type]["compressed"][sub_cell_index] = len(compressed_cell_data)
                            cell_header[data_type]["size"][sub_cell_index] = len(raw_sub_cell_data)

                        else:
                            cell_header[data_type]["index"] = len(data_blob) + data_blob_offset
                            cell_header[data_type]["compressed"] = len(compressed_cell_data)
                            cell_header[data_type]["size"] = len(raw_sub_cell_data)

                            if "count" in cell_header[data_type]:
                                cell_header[data_type]["count"] = sub_cell.meta_data["count"]

                        data_blob += compressed_cell_data

                    sub_cells_processed += 1

            header_data = self.create_cell_header(cell_header)

            if len(header_data) != self.CELL_DATA_SIZE:
                raise ValueError(f"Header data is invalid size! ({len(header_data)}) / ({self.CELL_DATA_SIZE}) ")


            start = self.header["cell_header_offset"] + (self.CELL_DATA_SIZE * cell_index)
            end = (start + self.CELL_DATA_SIZE)

            if len(header_data) != end - start:
                raise ValueError(f"Header Data Does not match the cell size {len(header_data)}/{end - start}")

            if end > len(new_data):
                raise ValueError(f"Invalid Header Index (Out of bounds). Index: {end}, Max: {len(new_data)}")

            new_data = new_data[:start] + header_data + new_data[end:]

            print(f"\r{bcolors.GOOD}[INFO] Processing... ({sub_cells_processed}/{sub_cell_count}){bcolors.ENDC}", end="")


        new_data += data_blob

        print(f"\r{bcolors.GOOD}[INFO] Writing to... {output_file_path}{bcolors.ENDC}", end="")
        with open(output_file_path, "wb") as f:
            f.write(new_data)

        print(f"\r{bcolors.GOOD}[INFO] Saved to '{output_file_path}'{bcolors.ENDC}")


