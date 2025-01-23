import struct


def read_mip(decompressed_data, metadata):
    height_map = []
    color_map = []

    chunk_size = metadata["size"]

    for i in range(chunk_size // 8):
        offset = i * 8
        height = struct.unpack_from("<f", decompressed_data, offset)[0]
        color = struct.unpack_from("<I", decompressed_data, offset + 4)[0]
        height_map.append(height)
        color_map.append(color)

    return color_map, height_map


def write_mip(data, metadata):
    color_map, height_map = data
    new_data = b""

    for i in range(len(height_map)):
        new_data += struct.pack("<f", height_map[i])
        new_data += struct.pack("<I", color_map[i])

    return new_data
