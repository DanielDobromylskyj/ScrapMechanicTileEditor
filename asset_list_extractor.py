import json

overrides = (
    ("$GAME_DATA", r"E:\SteamLibrary\steamapps\common\Scrap Mechanic\Data"),
    ("$SURVIVAL_DATA", r"E:\SteamLibrary\steamapps\common\Scrap Mechanic\Survival"),
)

asset_path = r"E:\SteamLibrary\steamapps\common\Scrap Mechanic\Data\Terrain\Database\assetsets.json"

def make_path(path):
    for override in overrides:
        path = path.replace(override[0], override[1])
    return path

asset_set_locations = json.load(open(make_path(asset_path)))["assetSetList"]

assets = []
for asset_set_location in asset_set_locations:
    asset_set_json = json.load(open(make_path(asset_set_location["assetSet"])))["assetListRenderable"]

    for asset_json in asset_set_json:
        assets.append(
            (asset_json["name"], asset_json["uuid"])
        )

print("class Assets:")

for name, uuid in assets:
    print(f"    {name} = \"{uuid.replace("-", "")}\"")
