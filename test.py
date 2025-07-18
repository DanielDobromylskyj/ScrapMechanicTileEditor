import numpy as np
from noise import pnoise2

from ScrapTiles import TileFile

from ScrapTiles.edit import mip

def generate_perlin_noise(width, height, scale=50.0, octaves=4, persistence=0.5, lacunarity=2.0, base=0):
    """ Generates a 2D array of Perlin noise. """
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
    tile = TileFile("Empty.tile")

    with mip.Modifier(tile) as mi:
        width, height = mi.get_size()

        noise = generate_perlin_noise(width, height, scale=80.0)

        min_h = -5
        max_h = 40
        terrain = ((noise + 1) / 2) * (max_h - min_h) + min_h

        for y in range(height):
            for x in range(width):
                mi.set_height(x, y, terrain[y, x])


    tile.write_file(r"perlin_noise.tile")

