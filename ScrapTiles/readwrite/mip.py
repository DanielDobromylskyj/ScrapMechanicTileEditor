import struct

def infer_dimensions(size):
    # Total size = (vertex_count * 8) + (ground_count * 8)
    # Try possible (square) sizes for vertex grid and ground grid

    for vertex_dim in range(1, 256):
        wh = vertex_dim * vertex_dim
        wh_bytes = wh * 8
        remaining = size - wh_bytes

        if remaining % 8 != 0:
            continue

        ground_count = remaining // 8
        ground_dim = int(ground_count**0.5)

        if ground_dim * ground_dim == ground_count:
            return vertex_dim, ground_dim

    raise ValueError("Could not infer dimensions")

def read_mip(decompressed_data, metadata, version=13):
    height_map = []
    color_map = []
    ground_map = []

    vertex_dim, ground_dim = infer_dimensions(metadata["size"])
    wh = vertex_dim * vertex_dim
    ground_count = ground_dim * ground_dim

    # Read height/color data
    for i in range(wh):
        offset = i * 8
        height = struct.unpack_from("<f", decompressed_data, offset)[0]
        color = struct.unpack_from("<I", decompressed_data, offset + 4)[0]
        height_map.append(height)
        color_map.append(color)

    # Read ground map
    ground_offset = wh * 8
    for i in range(ground_count):
        offset = ground_offset + i * 8
        val = struct.unpack_from("<q", decompressed_data, offset)[0]
        ground_map.append(val)

    return {
        "vertex_dim": vertex_dim,
        "ground_dim": ground_dim,
        "height_map": height_map,
        "color_map": color_map,
        "ground_map": ground_map,
    }


def write_mip(data, metadata):
    height_map = data["height_map"]
    color_map = data["color_map"]
    ground_map = data["ground_map"]

    assert len(height_map) == len(color_map)

    vertex_data = bytearray()
    for height, color in zip(height_map, color_map):
        vertex_data += struct.pack("<fI", height, color)  # float32, uint32

    ground_data = struct.pack(f"<{len(ground_map)}q", *ground_map)  # q = int64

    full_data = vertex_data + ground_data

    return full_data
