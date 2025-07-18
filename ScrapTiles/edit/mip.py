from scipy.ndimage import zoom
import numpy as np
import math


class Modifier:
    def __init__(self, tile):
        self.tile = tile

        self.tile_shape = (
            self.tile.header["width"],
            self.tile.header["height"]
        )

        self.pixel_shapes = self.__calculate_true_pixel_shape()

        self.pixels = self.__clone_map_to_array("height_map", depth=0)
        self.colours = self.__clone_map_to_array("color_map", depth=0)

        #print(self.tile.world_data[0]["mip"][0].data)


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

    def __clone_map_to_array(self, data_key, depth=0):
        tile_count = len(self.tile.world_data)
        grid_dim = int(math.sqrt(tile_count))
        assert grid_dim * grid_dim == tile_count, "Non-square tile count!"


        required_dtype = np.float32 if data_key == "height_map" else np.uint32


        sample_tile = self.tile.world_data[0]["mip"][depth].data
        tile_size = sample_tile["vertex_dim"]

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

        sample_tile = self.tile.world_data[0]["mip"][depth].data
        tile_size = sample_tile["vertex_dim"]

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


    def set_height(self, x, y, height) -> None:
        self.pixels[y][x] = height

    def get_height(self, x, y) -> np.float32:
        return self.pixels[y][x]


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


