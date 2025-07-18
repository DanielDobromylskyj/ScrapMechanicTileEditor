from scipy.ndimage import zoom
import numpy as np
import math


class Materials:
    DefaultGrass = 0
    StonePebbles = 1
    Sand = 3
    StoneSmooth = 5
    Dirt = 7
    ForrestGrass = 9
    StoneRock = 11
    HayFieldGrass = 13
    PlainsGrass = 15



class Modifier:
    def __init__(self, tile):
        self.tile = tile

        self.tile_shape = (
            self.tile.header["width"],
            self.tile.header["height"]
        )

        self.pixel_shapes = self.__calculate_true_pixel_shape()
        self.ground_shapes = self.__get_ground_shape()

        self.pixels = self.__clone_map_to_array("height_map", depth=0)
        self.colours = self.__clone_map_to_array("color_map", depth=0)
        self.ground_map = self.__clone_map_to_array("ground_map", depth=0)



    def get_size(self):
        return self.pixel_shapes[0]

    def __calculate_true_pixel_shape(self) -> list[tuple[int, int]]:
        return [
            (
                sum([  # Width
                    self.tile.world_data[cell_index]["mip"][img_depth].data["vertex_dim"]
                    for cell_index in range(self.tile_shape[0])
                ]),
                sum([  # Height
                    self.tile.world_data[cell_index * self.tile_shape[0]]["mip"][img_depth].data["vertex_dim"]
                    for cell_index in range(self.tile_shape[1])
                ])
            )
            for img_depth in range(6)
        ]

    def __get_ground_shape(self):
        return [
            (
                sum([  # Width
                    self.tile.world_data[cell_index]["mip"][img_depth].data["ground_dim"]
                    for cell_index in range(self.tile_shape[0])
                ]),
                sum([  # Height
                    self.tile.world_data[cell_index * self.tile_shape[0]]["mip"][img_depth].data["ground_dim"]
                    for cell_index in range(self.tile_shape[1])
                ])
            )
            for img_depth in range(6)
        ]

    def __clone_map_to_array(self, data_key, depth=0):
        tile_count = len(self.tile.world_data)
        grid_dim = int(math.sqrt(tile_count))
        assert grid_dim * grid_dim == tile_count, "Non-square tile count!"


        required_dtype = np.float32 if data_key == "height_map" else np.int64 if data_key == "ground_map" else np.uint32
        tile_size_key = "vertex_dim" if data_key != "ground_map" else "ground_dim"


        sample_tile = self.tile.world_data[0]["mip"][depth].data
        tile_size = sample_tile[tile_size_key]

        full_size = tile_size * grid_dim
        full_map = np.zeros((full_size, full_size), dtype=required_dtype)

        for idx, chunk in enumerate(self.tile.world_data):
            x = idx % grid_dim
            y = idx // grid_dim

            tile = chunk["mip"][depth].data[data_key]
            tile_array = np.array(tile, dtype=required_dtype).reshape((tile_size, tile_size))

            x_start = x * tile_size
            y_start = y * tile_size

            full_map[y_start:y_start + tile_size, x_start:x_start + tile_size] = tile_array

        return full_map

    def __clone_array_to_map(self, full_map, data_key, depth=0):
        tile_count = len(self.tile.world_data)
        grid_dim = int(math.sqrt(tile_count))
        assert grid_dim * grid_dim == tile_count, "Non-square tile count!"

        tile_size_key = "vertex_dim" if data_key != "ground_map" else "ground_dim"

        sample_tile = self.tile.world_data[0]["mip"][depth].data
        tile_size = sample_tile[tile_size_key]

        full_size = tile_size * grid_dim
        assert full_map.shape == (full_size,
                                  full_size), f"Expected shape {(full_size, full_size)}, got {full_map.shape}"

        for idx, chunk in enumerate(self.tile.world_data):
            x = idx % grid_dim
            y = idx // grid_dim

            x_start = x * tile_size
            y_start = y * tile_size

            tile_chunk = full_map[y_start:y_start + tile_size, x_start:x_start + tile_size]#.astype(np.float32)

            # Update the data in the mip level
            chunk["mip"][depth].data[data_key] = tile_chunk.flatten().tolist()

    @staticmethod
    def __down_scale(arr, new_shape):
        zoom_factors = (
            new_shape[0] / arr.shape[0],
            new_shape[1] / arr.shape[1]
        )
        # order=1: bilinear interpolation (acts like average-ish for downscaling)
        return zoom(arr, zoom_factors, order=1).astype(arr.dtype)

    def update(self):
        self.__clone_array_to_map(self.pixels, "height_map", depth=0)
        for depth in range(1, 6):
            self.__clone_array_to_map(self.__down_scale(
                self.pixels, self.pixel_shapes[depth]
            ), "height_map", depth=depth)


        self.__clone_array_to_map(self.colours, "color_map", depth=0)
        for depth in range(1, 6):
            self.__clone_array_to_map(self.__down_scale(
                self.colours, self.pixel_shapes[depth]
            ), "color_map", depth=depth)


        self.__clone_array_to_map(self.ground_map, "ground_map", depth=0)
        for depth in range(1, 6):
            self.__clone_array_to_map(self.__down_scale(
                self.ground_map, self.ground_shapes[depth]
            ), "ground_map", depth=depth)


    @staticmethod
    def __int_to_colour(colour) -> tuple[int, int, int, int]:
        r = colour & 0xFF
        g = (colour >> 8) & 0xFF
        b = (colour >> 16) & 0xFF
        a = (colour >> 24) & 0xFF
        return r, g, b, a

    @staticmethod
    def __colour_to_int(r: int, g: int, b: int, a: int) -> int:
        return (a << 24) | (b << 16) | (g << 8) | r

    def set_height(self, x, y, height) -> None:
        self.pixels[y][x] = height

    def get_height(self, x, y) -> np.float32:
        return self.pixels[y][x]


    def set_colour(self, x, y, rgba) -> None:
        self.colours[y][x] = self.__colour_to_int(*rgba)

    def get_colour(self, x, y) -> tuple[int, int, int, int]:
        return self.__int_to_colour(self.colours[y][x])


    def set_material(self, x, y, material_idx, weight, overwrite=False):
        """
        Set a 4-bit material weight (0-15) at position (y, x) for a specific material index.

        - arr: 2D np.ndarray of dtype=np.int64
        - x, y: coordinates in array
        - material_idx: index from 0 to 15
        - weight: new weight value (0–15)
        """
        if not (0 <= material_idx < 16):
            raise ValueError("Material index must be between 0 and 15")
        if not (0 <= weight <= 15):
            raise ValueError("Weight must be a 4-bit value (0–15)")

        if overwrite:
            self.ground_map[y, x] = 0

        shift = material_idx * 4
        mask = np.int64(0xF) << shift
        value_shifted = np.int64(weight & 0xF) << shift

        # Clear existing 4 bits
        self.ground_map[y][x] &= ~mask
        # Set new value
        self.ground_map[y][x] |= value_shifted


    def clear_ground_map(self, material_idx, weight):
        for y in range(self.ground_shapes[0][1]):
            for x in range(self.ground_shapes[0][0]):
                self.set_material(x, y, material_idx, weight, overwrite=True)



    def get_raw(self) -> dict[str: np.ndarray]:
        return {
            "height_map": self.pixels,
            "color_map": self.colours,
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:  # Exception raised, Do not save changes as it may now contain bad data.
            print("[WARNING] An error occurred when modifying MIP data, No changes have been made.")
            return False  # Let it propagate
        else:
            self.update()

        return False


