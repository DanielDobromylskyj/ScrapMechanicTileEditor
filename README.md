# Scrap Mechanic Tile Editor!

This project aims to create a python module to edit/create and maybe view a scrap mechanic .tile file.
I am a LONG way of completing this, Yet as of 18/07/25 basic terrain functions work including materials, colours and heights!
I plan to add much more to this, and more documention on how to use it, and on the .tile format in general
If you have infomation on how the .tile format works not currently in this module please say!

# File format (.tile)
> **_NOTE:_** A large amount of infomation about the .tile format has been collected from [QuestionableM's SM-Converter](https://github.com/QuestionableM/SM-Converter/)

# Binary Layout

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
