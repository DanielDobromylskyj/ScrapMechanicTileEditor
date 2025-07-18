import matplotlib.pyplot as plt
import numpy as np
import math


def render_height_map(height_map, vertex_dim):
    # Convert the 1D height map into a 2D array
    height_array = np.array(height_map, dtype=np.float32).reshape((vertex_dim, vertex_dim))

    # Display it as a grayscale image
    plt.imshow(height_array, cmap='gray', interpolation='nearest')
    plt.colorbar(label='Height')
    plt.title('Height Map')
    plt.show()



def render_full(world_data, depth=0):  # depth = 0 is highest resolution
    tile_count = len(world_data)
    grid_dim = int(math.sqrt(tile_count))
    assert grid_dim * grid_dim == tile_count, "Non-square tile count!"

    # Assume all tiles have same vertex_dim
    sample_tile = world_data[0]["mip"][depth].data
    tile_size = sample_tile["vertex_dim"]

    # The final array is slightly overlapping (unless tiles are padded)
    full_size = tile_size * grid_dim
    full_height_map = np.zeros((full_size, full_size), dtype=np.float32)

    for idx, chunk in enumerate(world_data):
        x = idx % grid_dim
        y = idx // grid_dim

        tile = chunk["mip"][depth].data["height_map"]
        tile_array = np.array(tile, dtype=np.float32).reshape((tile_size, tile_size))

        # Compute insertion location
        x_start = x * tile_size
        y_start = y * tile_size

        full_height_map[y_start:y_start + tile_size, x_start:x_start + tile_size] = tile_array

    plt.imshow(full_height_map, cmap='gray')
    plt.colorbar(label="Height")
    plt.title("Full Terrain Heightmap")
    plt.show()