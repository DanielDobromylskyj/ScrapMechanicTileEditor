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
    output_path = r"C:\Users\danie\AppData\Roaming\Axolot Games\Scrap Mechanic\User\User_76561198336691145\Tiles\0143e8f2-5902-4e2a-88ae-5a7de9a27405\CustomTile.tile"
    path = "Empty.tile"

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
                #mi.set_colour(x, y, ((x//2), (y//2), 0, 255))


    with assets.Modifier(tile) as asset:  # todo - Make this nicer to use
        asset.create_object((5, 5, 20), (0, 0, 0, 0), (1, 5, 1), {'rock': 4285101422})
        #print(asset.objects)


    tile.write_file(output_path)

    reloaded_tile = TileFile(output_path)

    with assets.Modifier(reloaded_tile) as asset:
        print("After Reload:", asset.objects)
        print(reloaded_tile.world_data[0]["assets"][1].data)

