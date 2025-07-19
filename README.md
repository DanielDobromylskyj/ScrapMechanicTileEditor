# Scrap Mechanic Tile Editor!

> **Disclaimer:** This project is still in development and may break or behave unexpectedly. Use at your own risk!
> Anything not shown in the documentation is completly untested and possibly incorrect!

This project aims to create a python module to edit/create and maybe view a scrap mechanic .tile file.
I am a LONG way of completing this, Yet as of 18/07/25 basic terrain functions work including materials, colours and heights!
I plan to add much more to this, and more documention on how to use it, and on the .tile format in general
If you have infomation on how the .tile format works not currently in this module please say!

## Contents
- [File Format](#file-format)
- [Module Usage](#usage)


# File format
> **_NOTE:_** A large amount of infomation about the .tile format has been collected from [QuestionableM's SM-Converter](https://github.com/QuestionableM/SM-Converter/)

## Binary Layout

## Usefull Info:
- '<' means little endian
- '>' means big endian


## File Header
This is the order of the data in the file, from the start.

- uint32    - Key ('TILE' if translated, should be equal to 0x454C4954, so this could also be char[4])
- uint32    - Version Number
- char[16]  - UUID (v4) (Not sure what its for. Maybe the tile UUID? Haven't looked into it)
- uint64    - Creator Id (Steam ID) (Stored as a ulong long)
- uint32    - Tile Width (Not the width of the tile in triangles or anything, but of sub tiles (cells))
- uint32    - Tile Height (Same as Width)
- uint32    - Cell Header Offset (Offset from start of file to the first byte of header data)
- uint32    - Cell Header Size
- uint32    - Unknown Value
- uint32    - Unknown Value
- uint32    - Type (Unsure what the type is for. Seems to be constant)

> **_NOTE:_** All the header values are little endian


## Cell Header
This chunk of data is from the the **_Cell Header Offset_** gathered from the **_File Header_**.

Cell headers are stored contiguosly in the data. Each header is the same size (**_Cell Header Size_** from **_File Header_**)

> **_NOTE:_** This section is rather unknown still. All compression in lz4

- int32[6]   - 6x MIP indexes (Colour data I believe)
- int32[6]   - 6x MIP Compressed Sizes (Size of the data after index)
- int32[6]   - 6x MIP Size (Uncompressed Size of MIP)
- int32      - Clutter Index
- int32      - Clutter Compressed Size
- int32      - Clutter Size (Uncompressed)
- int32[4]   - Asset List Count
- int32[4]   - Asset List Index
- int32[4]   - Asset List Compressed Size
- int32[4]   - Asset List Size
- int32      - Blueprint List Count
- int32      - Blueprint List Index
- int32      - Blueprint List CompressedSize
- int32      - Blueprint List Size
- int32      - Node Count (Unsure what a node is)
- int32      - Node Index
- int32      - Node Compressed Size
- int32      - Node Size
- int32      - Script Count
- int32      - Script Index
- int32      - Script Compressed Size
- int32      - Script Size
- int32      - Prefab Count
- int32      - Prefab Index
- int32      - Prefab Compressed Size
- int32      - Prefab Size
- int32      - Decal Count
- int32      - Decal Index
- int32      - Decal Compressed Size
- int32      - Decal Size
- int32[4]   - Harvestable List Count
- int32[4]   - Harvestable List Index
- int32[4]   - Harvestable List Compressed Size
- int32[4]   - Harvestable List Size
- int32[4]   - Kinematics List Count
- int32[4]   - Kinematics List Index
- int32[4]   - Kinematics List Compressed Size
- int32[4]   - Kinematics List Size
- int32[4]   - Unkown Data x4
- int32   - Voxel Terrain Count
- int32   - Voxel Terrain Index
- int32   - Voxel Terrain Compressed Size
- int32   - Voxel Terrain Size

> **_NOTE:_** All the header values are little endian

More Docs todo, Check **_main.py_** For info not added to the README yet.


## Usage

> **_NOTE:_** As of 19/07/25 This module only supports editing .tile files directly not the whole tile foulder, And can only edit. Simply create a new world with SM then edit it with this program until I figure something better out!

### Loading

```python
from ScrapTiles import TileFile

tile = TileFile(r"path/to/file.tile")
```

### Writing / Saving

```python
from ScrapTiles import TileFile

tile = TileFile(r"path/to/file.tile")

tile.write_file(r"path/to/new.tile")
```

### Modifiers
> **_NOTE:_** This section is VERY underdeveloped at the time of writing this

#### Mip (Terrain -> Height/Colour/Material)

```python
from ScrapTiles.edit import mip, 

with mip.Modifier(tile) as mi:
  # Retrieve the size of the largest Height/Colour map image
  # As a warning. The size of the ground map is different.
  width, height = mi.get_size()

  # Set/Get Heights as a given x/y
  mi.set_height(x, y, height)
  mi.get_height(x, y) -> float

  # Set/Get colours (0-255, rgba)
  mi.set_colour(x, y, (r, g, b, a))
  mi.get_colour(x, y) -> (r, g, b, a)

  # Ground Sizes are normally 65x65. As it is a QUAD for every "pixel" in the height map
  # And the height map is normaly 33x33
  ground_width, ground_height = mi.get_ground_size()

  # The following materials are valid:
  # DefaultGrass, StonePebbles, StoneSmooth, StoneRock, Sand, Dirt, ForrestGrass, HayFieldGrass, PlainsGrass
  materials = mip.Materials
  
  # Set a single point with. The weight is 0-15 and is the strength of the material
  # This has the same behavour as the SM tile editor. To force it to be only a given material, use overwrite=True
  mi.set_material(x, y, material, weight, overwrite=False)

  # To reset the whole ground to a single material use:
  mi.clear_ground_map(material, weight)

  # There is currently no function to sample the material. Yet it can be extracted from the get_raw() function
  maps: dict[str: np.ndarray] = mi.get_raw()

  maps = {
      "height_map": ...,
      "colour_map": ...,
      "ground_map": ...,
  }
```

> **_NOTE:_** If not using the context manager, ensure mi.update() is called before writing the file and after its modified. And do NOT write the file when still in a Modifiers context!
> This is required due to how data is managed internally. And how it is converted / downscaled back to its original format used to write to the file.





