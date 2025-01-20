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
- uint32    - Unknown Value 1
- uint32    - Unknown Value 2
- uint32    - Type (Unsure what the type is for. Seems to be constant)

> **_NOTE:_** All the header values are little endian


## Cell Header
This chunk of data is from the the offset gathered from the **_File Header_**


