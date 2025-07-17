
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def byte_to_str(data) -> str:
    return str(data)[2:-1]


path = "test.tile"


index_pointer = 99389
size = 192
boundary = 5

with open(path, "rb") as f:
    f.seek(index_pointer - boundary)
    data = f.read(size + (boundary * 2))

    boundary_front = data[:boundary]
    boundary_back = data[-boundary:]
    main = data[boundary:-boundary]

    print(f"{bcolors.WARNING}{byte_to_str(boundary_front)}{bcolors.OKGREEN}{byte_to_str(main)}{bcolors.WARNING}{byte_to_str(boundary_back)}{bcolors.ENDC}")




