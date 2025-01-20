# File format (.tile)

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

> **_NOTE:_** This section is rather unknown still

- int32[6]   - 6x MIP indexes (Hieght data I believe)
- int32[6]   - 6x MIP Compressed Sizes (Size of the data after index)
- int32[6]   - 6x MIP Size (Uncompressed Size of MIP, Uses lz4 compression)
- int32      - Unkown Value
- int32      - Unkown Value
- int32      - Unkown Value
- int32[4]   - Unkown Values
- int32[4]   - Unkown Values
- int32[4]   - Unkown Values
- int32[4]   - Unkown Values
- int32      - Unkown Value
- int32      - Unkown Value
- int32      - Unkown Value
- int32      - Unkown Value
- int32      - Unkown Value
- int32      - Unkown Value
- int32      - Unkown Value
- int32      - Unkown Value
- int32[4]   - Unkown Values
- int32[4]   - Unkown Values
- int32[4]   - Unkown Values
- int32[4]   - Unkown Values
- int32[4]   - Unkown Values
- int32[4]   - Unkown Values
- int32[4]   - Unkown Values
- +24 int32  - Unkown Values

> **_NOTE:_** All the header values are little endian

More Docs todo, Check **_main.py_** For info not added to the README yet.
