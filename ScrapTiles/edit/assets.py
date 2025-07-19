import uuid

from ..sub_tile import SubCellData


class Modifier:
    def __init__(self, tile):
        self.tile = tile

        self.cell_size = 65

        self.tile_shape = (
            self.tile.header["width"],
            self.tile.header["height"]
        )

        self.objects = self.__clone_tile_objects_to_array()

    def __clone_tile_objects_to_array(self):
        objects = []
        for cell_x in range(self.tile_shape[0]):
            for cell_y in range(self.tile_shape[1]):
                cell_index = cell_y * self.tile_shape[0] + cell_x
                for region, chunk in enumerate(self.tile.world_data[cell_index]["assets"]):
                    if type(chunk) is not tuple:
                        for object_data in chunk.data:
                            objects.append({
                                "position": (
                                    cell_x * self.cell_size + object_data["position"][0],
                                    cell_y * self.cell_size + object_data["position"][1],
                                    object_data["position"][2]
                                ),
                                "rotation": object_data["rotation"],
                                "scale": object_data["scale"],
                                "UUID": object_data["UUID"],
                                "colour_map": object_data["colourMap"],
                            })

        return objects

    def get_objects_in_region(self, x1, y1, x2, y2):
        return [
            object_data
            for object_data in self.objects
            if (x1 <= object_data["position"][0] <= x2) and (y1 <= object_data["position"][1] <= y2)
        ]


    def __convert_array_object_to_tile_object(self, obj):
        return {
            "position": (
                obj["position"][0] % self.cell_size,
                obj["position"][1] % self.cell_size,
                obj["position"][2],
            ),
            "rotation": obj["rotation"],
            "scale": obj["scale"],
            "UUID": obj["UUID"],
            "colourMap": obj["colour_map"],
        }

    def __clone_array_to_tile_objects(self, object_array):
        for cell_x in range(self.tile_shape[0]):
            for cell_y in range(self.tile_shape[1]):
                new_raw = [(0, 0, 0) for _ in range(4)]
                #for region in range(4):  # 6 chunks

                region = 1

                bounds = [cell_x * self.cell_size, cell_y * self.cell_size,
                          (cell_x+1) * self.cell_size, (cell_y+1) * self.cell_size,]
                objects = self.get_objects_in_region(*bounds)

                if objects:
                    true_objects = [
                        self.__convert_array_object_to_tile_object(obj)
                        for obj in objects
                    ]

                    meta_data = {"index": 0, "compressed": 0, "size": 0, "count": len(true_objects)}

                    cell = SubCellData("assets", b"", meta_data, self.tile.header["version"])
                    cell.data = true_objects
                    new_raw[region] = cell

                self.tile.world_data[cell_y * self.tile_shape[0] + cell_x]["assets"] = new_raw


    def create_object(self, xyz, rotation, scale, colour_map):
        self.objects.append({
                "position": xyz,
                "rotation": rotation,
                "scale": scale,
                "UUID": uuid.uuid4().hex,
                "colour_map": colour_map,
            })

    def update(self):
        self.__clone_array_to_tile_objects(self.objects)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:  # Exception raised, Do not save changes as it may now contain bad data.
            print("[WARNING] An error occurred when modifying Asset data, No changes have been made.")
            return False  # Let it propagate
        else:
            self.update()

        return False


