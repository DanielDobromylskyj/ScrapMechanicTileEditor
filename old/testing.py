import numpy as np
from noise import pnoise2  # Make sure you have the `noise` module installed

from readwrite.mip import Modifier as MipModifier
from main import TileFile


def generate_perlin_noise(width, height, scale=50.0, octaves=4, persistence=0.5, lacunarity=2.0, base=0):
    """Generates a 2D array of Perlin noise."""
    noise_map = np.zeros((height, width), dtype=np.float32)

    for y in range(height):
        for x in range(width):
            nx = x / scale
            ny = y / scale
            noise_val = pnoise2(
                nx, ny,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=width,
                repeaty=height,
                base=base
            )
            noise_map[y][x] = noise_val
    return noise_map


if __name__ == "__main__":
    tile_file = TileFile(r"tile\Empty.tile")
    tile_file.read_file()


    with MipModifier(tile_file) as mip:
        width, height = mip.get_size()

        noise = generate_perlin_noise(width, height, scale=80.0)

        # Normalize to your desired height range
        min_h = -5
        max_h = 40
        terrain = ((noise + 1) / 2) * (max_h - min_h) + min_h  # maps from [-1,1] to [-5,40]

        for y in range(height):
            for x in range(width):
                mip.set_height(x, y, terrain[y, x])


    tile_file.write_file(r"perlin_noise.tile")  # This tile is 10Kb larger than we started with?