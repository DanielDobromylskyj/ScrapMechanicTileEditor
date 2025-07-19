import struct



class MemoryWrapper:
    def __init__(self, data: bytes):
        self.data = data

    def read_vec3(self, offset):
        return struct.unpack_from('<3f', self.data, offset)

    def read_quat(self, offset):
        return struct.unpack_from('<4f', self.data, offset)

    def read_float(self, offset):
        return struct.unpack_from('<f', self.data, offset)[0]

    def read_uint8(self, offset):
        return struct.unpack_from('<B', self.data, offset)[0]

    def read_uint32(self, offset):
        return struct.unpack_from('<I', self.data, offset)[0]

    def read_uuid(self, offset):
        return self.data[offset:offset+16]  # Raw 16 bytes

    def read_string(self, offset, length):
        return self.data[offset:offset+length].decode('utf-8')



def debug(decompressed_data, metadata):
    memory = MemoryWrapper(decompressed_data)
    index = 0

    print(">>> Debug -> Count:", metadata["count"])

    for i in range(metadata["count"]):
        print("\n\n>> Object Index:", i)

        position = memory.read_vec3(index)
        print("> Position:", position)

        rotation = memory.read_quat(index + 0xC)
        print("> Rotation:", rotation)

        scale = memory.read_vec3(index + 0x1C)
        index += 0x28
        print("> Scale:", scale)

        f_uuid = memory.read_uuid(index)
        index += 0x10
        print("> UUID:", f_uuid.hex())

        bVar4 = memory.read_uint8(index)
        index += 1

        print("> Sub Count:", bVar4, "\n")

        for _ in range(bVar4):
            key_len = memory.read_uint8(index)
            index += 1

            print("> Key Length:", key_len)

            key = memory.read_string(index, key_len)
            index += key_len

            print("> Key:", key)

            color = memory.read_uint32(index)
            index += 4

            print("> Colour:", color)

        index += 1





def read_assetList(decompressed_data, metadata, version=13):
    objects = []
    memory = MemoryWrapper(decompressed_data)
    index = 0

    #debug(decompressed_data, metadata)

    for _ in range(metadata["count"]):
        position = memory.read_vec3(index)
        rotation = memory.read_quat(index + 0xC)

        if version < 5:
            scale_value = memory.read_float(index + 0x1C)
            scale = (scale_value, scale_value, scale_value)
            index += 0x20
        else:
            scale = memory.read_vec3(index + 0x1C)
            index += 0x28

        if version < 4:
            raise NotImplementedError("Pre-version 4 UUID parsing not implemented.")

        else:
            f_uuid = memory.read_uuid(index)
            index += 0x10

        colour_map = {}
        bVar4 = memory.read_uint8(index)
        index += 1

        if bVar4 != 0:
            for _ in range(bVar4):
                key_len = memory.read_uint8(index)

                index += 1
                key = memory.read_string(index, key_len)
                index += key_len
                color = memory.read_uint32(index)
                index += 4

                if key not in colour_map:
                    colour_map[key] = color

        if version >= 12:  # Unknown value
            index += 1  # Skip 1 byte for newest version of .tile

        objects.append({
            "position": position,
            "rotation": rotation,
            "scale": scale,
            "UUID": f_uuid.hex(),
            "colourMap": colour_map,
        })



    return objects



def write_assetList(data, metadata, version=13):
    output = bytearray()

    for obj in data:
        # Write position (vec3) - 3 floats
        output += struct.pack('<3f', *obj["position"])

        # Write rotation (quat) - 4 floats
        output += struct.pack('<4f', *obj["rotation"])

        # Write scale
        if version < 5:
            scale_val = obj["scale"][0]
            output += struct.pack('<f', scale_val)
            output += b'\x00' * (0x20 - 0x1C - 4)  # Fill remaining to make total 0x20
        else:
            output += struct.pack('<3f', *obj["scale"])
            output += b'\x00' * (0x28 - 0x1C - 12)  # Fill remaining to make total 0x28

        # Write UUID (16 bytes)
        uuid_bytes = bytes.fromhex(obj["UUID"])
        output += uuid_bytes

        # Write color map
        colour_map = obj.get("colourMap", {})
        output += struct.pack('<B', len(colour_map))

        for key, color in colour_map.items():
            key_bytes = key.encode('utf-8')
            key_len = len(key_bytes)

            output += struct.pack('<B', key_len)
            output += key_bytes
            output += struct.pack('<I', color)

    if version >= 12:
        output += b'\x00'  # One byte padding for version >= 12

    return bytes(output)