import numpy as np
from noise import pnoise2

from ScrapTiles import TileFile
from ScrapTiles.edit import mip, assets


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
    output_path = r"C:\Users\danie\AppData\Roaming\Axolot Games\Scrap Mechanic\User\User_76561198336691145\Tiles\71ac6dea-2613-4996-aff0-f4c4d187ddd0\CustomTile.tile"
    path = "debug_tiles/DEBUG_TILE_0.5.tile"  # "Empty.tile"

    tile = TileFile(path)

    with mip.Modifier(tile) as mi:
        mi.clear_ground_map(mip.Materials.DefaultGrass, 15)

        width, height = mi.get_size()

        noise = generate_perlin_noise(width, height, scale=80.0)

        min_h = -5
        max_h = 40
        terrain = ((noise + 1) / 2) * (max_h - min_h) + min_h

        for y in range(height):  # ~512
            for x in range(width):  # ~512
                mi.set_height(x, y, terrain[y, x])
                mi.set_colour(x, y, (0, 255, 0, 0))

    asset_ids = assets.Assets

    with assets.Modifier(tile) as asset:
        print(asset.get_objects())

        asset.create_object(
            asset_ids.env_nature_rocks_large01,
            (30, 30, terrain[30, 30]),
            (0.7067, 0.0237, 0.0237, 0.7067),
            (0.25, 0.25, 0.25),
            2,
            {'rock': 4285101422}
        )



    tile.write_file(output_path)

    reloaded_tile = TileFile(output_path)

    with assets.Modifier(reloaded_tile) as asset:
        pass

