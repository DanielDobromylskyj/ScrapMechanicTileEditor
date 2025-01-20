from main import TileFile
import matplotlib.pyplot as plt
import numpy as np


class TileFileVisualizer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_data = None
        self.sections = []

    def load_file(self):
        with open(self.file_path, "rb") as f:
            self.file_data = f.read()

    def add_section(self, start, end, label, colour):
        self.sections.append({
            "start": start,
            "end": end,
            "label": label,
            "colour": colour
        })

    def visualise(self):
        if not self.file_data:
            raise ValueError("File data is empty. Please load a file first.")

        file_size = len(self.file_data)
        image = np.full(file_size, 0, dtype=np.uint8)
        label_map = np.full(file_size, "", dtype=object)

        for section in self.sections:
            image[section["start"]:section["end"]] = section["colour"]
            label_map[section["start"]:section["end"]] = section["label"]

        img_width = 2500
        img_height = (file_size // img_width) + 1
        image = np.pad(image, (0, img_width * img_height - file_size), constant_values=0)
        image = image.reshape((img_height, img_width))

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(image, cmap="tab20c", interpolation="nearest")
        ax.set_title("File layout Visualisation")
        ax.axis("off")

        for section in self.sections:
            y = section["start"] // img_width
            x = section["start"] % img_width
            ax.text(x, y, section["label"], fontsize=6, color="black", ha="left", va="top")

        plt.show()



if __name__ == "__main__":
    path = r"tile\Dirt Race Track Tile.tile"
    visualizer = TileFileVisualizer(path)
    visualizer.load_file()

    loaded_tile = TileFile(path)
    loaded_tile.read_file()

    visualizer.add_section(0, 60, "", 1)  # File Header

    offset = loaded_tile.header["cell_header_offset"]
    cell_size = loaded_tile.header["cell_header_size"]
    cell_count = loaded_tile.header["width"] * loaded_tile.header["height"]

    for _ in range(cell_count):
        offset += cell_size

    visualizer.add_section(loaded_tile.header["cell_header_offset"], offset, "Cell Headers", 2)  # Cell Header

    for cell_header in loaded_tile.cell_headers:
        for mip_level in range(6):
            mip_index = cell_header["mip_index"][mip_level]
            mip_size = cell_header["mip_size"][mip_level]
            mip_compressed_size = cell_header["mip_compressed_size"][mip_level]

            visualizer.add_section(mip_index, mip_index+mip_compressed_size, "", 3)  # MIP

    visualizer.visualise()
