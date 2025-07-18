
expected_header_layout = [
    (32, "Tile Magic"),
    (32, "Version Number"),
    (8 * 16, "UUID"),
    (64, "Creator ID"),
    (32, "Tile Width"),
    (32, "Tile Height"),
    (32, "Cell Header Offset"),
    (32, "Cell Header Size"),
    (32, "Unknown 1"),
    (32, "Unknown 2"),
    (32, "Type"),



    ((32, 6), "MIP Indexes"),
    ((32, 6), "MIP Compressed Sizes"),
    ((32, 6), "MIP Sizes"),

    (32, "Clutter Index"),
    (32, "Clutter Compressed Sizes"),
    (32, "Clutter Sizes"),

    ((32, 4), "Asset List Count"),
    ((32, 4), "Asset List Indexes"),
    ((32, 4), "Asset List Compressed Sizes"),
    ((32, 4), "Asset List Sizes"),
]

def byte_to_str(data) -> str:
    """Return bytes as hex string like '8C BE 16 D9'"""
    return f"{''.join(f"{b: 02X}" for b in data)} ({int.from_bytes(data, byteorder="little")})"


def show(file_path):
    print()
    with open(file_path, "rb") as f:
        for size_data, tag in expected_header_layout:
            if type(size_data) is int:
                size = int(size_data // 8)
                data = f.read(size)

                print(f"{tag}:\n {byte_to_str(data)}")

            else:
                size_bits, amount = size_data
                size = int(size_bits // 8)

                print(f"{tag}:")

                for _ in range(amount):
                    print(f" {byte_to_str(f.read(size))}")

            print()

def compare(file_path1, file_path2):
    print()

    f1 = open(file_path1, "rb")
    f2 = open(file_path2, "rb")

    for size_data, tag in expected_header_layout:
        if type(size_data) is int:
            size = int(size_data // 8)

            data1 = f1.read(size)
            data2 = f2.read(size)

            if data1 != data2:
                print(f"{tag}:\n {byte_to_str(data1)}  vs {byte_to_str(data2)}")
                print("")

        else:
            size_bits, amount = size_data
            size = int(size_bits // 8)

            print(f"{tag}:")

            for _ in range(amount):
                data1 = f1.read(size)
                data2 = f2.read(size)

                if data1 != data2:
                    print(f" {byte_to_str(data1)}  vs {byte_to_str(data2)}")

            print()


if __name__ == "__main__":
    print("Modes -> 1: Show, 2: Compare")

    mode = input("Mode: ")

    if mode == "":
        mode = "1"

    path = input("Enter path to file: ")

    if path == "":
        path = "test.tile"


    if mode == "1":
        show(path)

    elif mode == "2":
        path2 = input("Enter path of file 2: ")

        if path2 == "":
            path2 = "tile/Dirt Race Track Tile.tile"

        compare(path, path2)
