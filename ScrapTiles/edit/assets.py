from collections import defaultdict

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
                                "region": region,
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
        # Step 1: bucket objects by (cell_x, cell_y, region)
        buckets = defaultdict(list)
        for obj in object_array:
            # figure out which cell the object belongs to
            cell_x = obj["position"][0] // self.cell_size
            cell_y = obj["position"][1] // self.cell_size
            region = obj["region"]

            # convert global → local position
            local_position = (
                obj["position"][0] - cell_x * self.cell_size,
                obj["position"][1] - cell_y * self.cell_size,
                obj["position"][2],
            )

            # format back into tile object
            true_obj = {
                "position": local_position,
                "rotation": obj["rotation"],
                "scale": obj["scale"],
                "UUID": obj["UUID"],
                "colourMap": obj["colour_map"],
            }

            buckets[(cell_x, cell_y, region)].append(true_obj)

        # Step 2: rebuild world_data cell by cell
        for cell_x in range(self.tile_shape[0]):
            for cell_y in range(self.tile_shape[1]):
                new_raw = [(0, 0, 0) for _ in range(4)]  # 4 possible regions
                for region in range(4):
                    objs = buckets.get((cell_x, cell_y, region), [])

                    if objs:
                        meta_data = {
                            "index": 0,
                            "compressed": 0,
                            "size": 0,
                            "count": len(objs),
                        }
                        cell = SubCellData("assets", b"", meta_data, self.tile.header["version"])
                        cell.data = objs
                        new_raw[region] = cell

                # assign back to world_data
                cell_index = cell_y * self.tile_shape[0] + cell_x
                self.tile.world_data[cell_index]["assets"] = new_raw


    def create_object(self, object_uuid, xyz, rotation, scale, region, colour_map):
        self.objects.append({
            "position": xyz,
            "rotation": rotation,
            "scale": scale,
            "UUID": object_uuid,
            "colour_map": colour_map,
            "region": region,
        })

    def get_objects(self):
        return self.objects

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


class Assets:
    env_menu_mountains02 = "06addf2ec867479384d0729fd7261dd5"
    env_menu_backdropmountains01 = "4d731377f54d4c55a7cd30e8fbdf69e0"
    env_menu_backdropmountains02 = "605b0f98d80f4a15a22f6290067f44c3"
    env_menu_backdropmountains03 = "d400d9dd77b44a158bf9cd9889f1e841"
    env_menu_backdropmountains04 = "c16c75d59e464181a465258c29f0941f"
    env_menu_backdropmountains05 = "b4bb34acb6474fe5bfb5a338c12e7b6f"
    env_menu_sky01 = "3b27030b0c0848cc905443e38b679af5"
    env_menu_buildplatform = "ce106c70b9bd43478b6cfd8a394e23bb"
    env_menu_tree_birch01 = "95d3586ad9b647599380932646ea26aa"
    env_menu_tree_leafy01 = "f3d7f7ce8f2641ce94dd64947b98daf6"
    env_menu_tree_leafy02 = "cde2918bb24e42968611c88b3653ee42"
    env_menu_tree_pine01 = "bdd17e02cf874e8495d3f94e7538258a"
    env_menu_tree_pine03 = "8a57f43b08ef4307832a8aaa8a7656b6"
    env_menu_tree_Spruce01 = "1a42442cc7744b2483d25c0a6eb19fbf"
    env_menu_tree_Spruce03 = "5f6f14babfd449dab80fb3f8908b3ebd"
    env_menu_plank_long = "e602d0f065ff464fa29e718012ee57c0"
    env_menu_plank_short = "30c6f690080b44329ce6bb51a5ceafbc"
    env_manmade_borderfence = "9a9e35ec029f45f18896cc6314e144cf"
    env_manmade_spawnplatform = "995f8c61307e47cea51907bc04016a88"
    env_manmade_antenna = "66929701591f4054aa356ef9d025bd50"
    env_manmade_borderfencecorner = "090772dffaa2407b88c5872ec33b1354"
    env_manmade_billboard01 = "413af0ef1f7a466cac5dc550b7a7638c"
    env_manmade_tank = "d69a8fb833c846b1817c2cf5fd6f71f1"
    env_manmade_tankpipe01 = "ae7ddee522014f98bbf3f94853eab59a"
    env_manmade_tankpipe02 = "11be64c0814f43d386996b07347cc226"
    env_manmade_tankpipe03 = "d8207488ec024f71a865c05ed5d0b175"
    env_manmade_tankpipe04 = "4f763d27df3c4926ae05ce314093171e"
    env_forest_oak01 = "ab2221f1b86a45aab28fdac06d2c71d8"
    env_forest_oak02 = "2160d36da3bb409f93c99ece9cd45310"
    env_forest_oak03 = "6076c649dae74fe58ca94dd98b35fd73"
    env_forest_oak04 = "1ff3a68877354375937078ef7eb407c0"
    env_forest_oak05 = "80535813ae09427ba914e6c320df6005"
    env_forest_oakleafless01 = "3d89510d2a9648f29d3b6d04cb628abe"
    env_forest_oakleafless02 = "b0f26ef0a744452686bfd5b8768c7e39"
    env_forest_pine01 = "3958948a9da34ef2bbc6f3f6c8efd69b"
    env_forest_pine02 = "89cf550e96e04b8d9fcfc4cb701eb2ce"
    env_forest_pine03 = "ad7428d8b1f9497eb20e7b6c23303ba3"
    env_forest_pinebroken01 = "3333e3fa2ea04006bb7e85a8de6cc6b4"
    env_forest_pinelog01 = "813925eec5e4423489fe139d5ca36e2a"
    env_forest_pinelog02 = "663666706ecf4000b455055c252cb6dd"
    env_forest_giantpine01 = "d033a617c1d64b58b521efa2d4e8ce3c"
    env_forest_giantpine02 = "896e086dbbe74c42923babbcc91c8756"
    env_forest_giantpine03 = "143d0faa3a0643b285e7ed049b2d7497"
    env_forest_giantpine04 = "ef5ebb10fac94bf49d25772573bcbba8"
    env_forest_giantpineroot01 = "ad3b96dbe5fb4309bbeab9707996f06d"
    env_forest_giantpineroot02 = "543db1be2afa40a59d016ad69e255b94"
    env_forest_giantpineroot03 = "f44fdd28cafe4f5cb9361d9a005dc28c"
    env_forest_giantpineroot04 = "4593fd0581f3441b8a489741228e4afc"
    env_forest_birch01 = "bc8b746d4b8546a9924cf1edb0eef5f6"
    env_forest_birch02 = "81ca86c67c744a9082eddc08734baa6d"
    env_forest_birch03 = "e8090eadb2a34765a7e09ca907c42e42"
    env_forest_birchsmall01 = "be87cfca8d8247d7a77b676c87364633"
    env_forest_birchsmall02 = "c216f3e97b764c1fbdf6d29d253b30a9"
    env_forest_birchlog01 = "813426f77bd740b1b05dda8bc0a8ba8d"
    env_forest_birchlog02 = "9e19448b29c14bd0812458dcff3aa81c"
    env_foliage_plantexotic01 = "92f4eb24e6114091a9de3acdcf53bd9f"
    env_foliage_plantexotic02 = "ac030d02b931411381d4b36a3400e1ba"
    env_foliage_plantexotic03 = "29a78f099c2145b4b738f2cd6e078031"
    env_foliage_smallbirch01 = "4bd88efa949c4c0b85172f2b1b2bdb01"
    env_foliage_smallbirch02 = "f741ad80c99a4cecb67de53ec82a7bd0"
    env_nature_foliage_wildbush01 = "09a5a0ee0fd14b3286c09e6f2b701546"
    env_nature_foliage_wildbush02 = "b1e1b1bf6175465e81c69ec9d0bf83d0"
    env_foliage_padplant01 = "2947c3b768164debb8eec95065e930ef"
    env_foliage_padplant02 = "6dd42da5fdf344979b448dc99b12133d"
    env_foliage_cornplant01 = "86295daf385747ac9fe56ce232d4b124"
    env_foliage_cornplant02 = "b9a94f83e6704f5ca2128862b51b3f62"
    env_foliage_cornplant03 = "db01052ea80548fbb3027f4ad4908f74"
    env_foliage_cornplant04 = "deedd485711e4bedb2ba028a1c803948"
    env_foliage_cucumberplant01 = "7f09455e14ea41749c9d50e8932daa8e"
    env_foliage_cucumberplant02 = "8c6f94eb35554f798d0aeb8086af49e1"
    env_foliage_eggplant01 = "dbb276df90c94fb1b9d3cc6b297c2156"
    env_foliage_eggplant02 = "07f28c2f02564a37a730b3df8a705357"
    env_foliage_fern = "213a5264bcf64ef9bd1ebf46df8d087e"
    env_foliage_perennial = "e9525271f75942dc85ab4779a8b4fbb8"
    env_nature_foliage_greensprout01 = "a5708a7e461240808ba33e09eca3fcf7"
    env_nature_foliage_greensprout02 = "ccf07c0df33b421893248acbd6b6e418"
    env_nature_foliage_buxus01 = "796cabcd570342afb4e9512c85abcf59"
    env_nature_foliage_buxus02 = "df1a36a36be04681845ed89d6c80d1a6"
    env_nature_foliage_buxus03 = "73acaa1dd208450b815999d5914bbcde"
    env_nature_foliage_boxwood = "c63b9bff0c25460ba1a3af3161592170"
    env_nature_foliage_columnshrub01 = "fd3844b558eb4cb096d6383b7fa83923"
    env_nature_foliage_columnshrub02 = "fe13442039cb450b95605d3401556f7a"
    env_nature_foliage_columnshrub03 = "40ff23e639144d859048fe012f72cba1"
    env_smallstone_boulder01 = "e5ab05eefac2484e93030d1714a348bf"
    env_smallstone_boulder02 = "f695d49a72b74fbe94d76431b9b02fff"
    env_smallstone_boulder03 = "febe352e972b4b3796928a94d2c97a68"
    env_smallstone_boulder04 = "25d2bd5d75a743249a8c097115005aa3"
    env_smallstone_boulder05 = "0ae557a01ab74de2aecea2b6f212e38e"
    env_smallstone_boulder06 = "d5883203d5ad4a1da71b2f7c4e2523fa"
    env_smallstone_boulder07 = "25e45250bc3140eeb0c09bfdc0977501"
    env_smallstone_boulder08 = "eee44137ff14474a9143e4b23612ae8c"
    env_smallstone_boulder09 = "64ef6077dc5c48388be5892365874458"
    env_smallstone_boulder10 = "8b549a6840f84b3eac566e33a460d410"
    env_smallstone_columnrubble01 = "f6a8c6a7b38b43248faa946704a4b1b9"
    env_smallstone_columnrubble02 = "6f727addd6324a3ab01892f0ea5b7bf0"
    env_smallstone_columnrubble03 = "f249f2c24ec94d6d8d0570397a307475"
    env_smallstone_columnrubble04 = "9080a4772c584541affbf6a1e6686046"
    env_smallstone_columnrubble05 = "5bc248a43c36448b9c17ac6a35941d8c"
    env_smallstone_columnrubble06 = "afeb2ad5764b4ac893641421ff865b96"
    env_smallstone_columnrubble07 = "d70d66caccd2425bb0e7e105a9631945"
    env_smallstone_columnrubble08 = "9f05a6bc265e4c63bb668a283f91ca8f"
    env_rocks_rock01 = "18d95c1063a340a58edcdc062d547b70"
    env_rocks_rock02 = "194e7c7f26de48a1b8ee775e68100ed1"
    env_rocks_rock03 = "6e8d9830c9564b1abb3ebdf724ced968"
    env_rocks_rock04 = "dabe4e2bf8f649df8f206e31999c887d"
    env_rocks_rock05 = "84b1af2576ce48a580492f042e76985f"
    env_rocks_rock06 = "1454cc81b07148f2bf508a0d8b93e393"
    env_rocks_rock07 = "2161d53a1166400fa6927055865d9fb9"
    env_rocks_rock08 = "388fdf39b2234649acebeb609aee87ef"
    env_rocks_column01 = "6cb26785c4db435896b760d7fd301c25"
    env_rocks_column02 = "df5f6444ad074e2da2f4d9e7685a4e17"
    env_rocks_column03 = "187b7f8a9b634f2ea8ae9f82d1ddcec2"
    env_rocks_columnbig01 = "338946f82215435684e26c27411e89ac"
    env_rocks_columnbig02 = "798e509391974cd5b53b5bba910b4aa3"
    env_rocks_columnbig03 = "a03b994e49ef4005bae303fc3cf85969"
    env_rocks_columnwall01 = "c7d34786cbc94877b41f3d7ac685839b"
    env_rocks_columnwall02 = "78c96044a4e045d391b7de95ee023fdd"
    env_rocks_columnwall03 = "3f730b20ae9b44fcaaf6dea55975154c"
    env_rocks_bigrock01 = "60fd7f167aa64f0390f81346d5a0ba99"
    env_rocks_bigrock02 = "ad415d9249334b3bb48e5faf84ab5651"
    env_rocks_bigrock03 = "233f71e5bbb64763a865e7d89e607fc0"
    env_rocks_bigrock04 = "b8213a8750af4b40ad9c3513df1f269c"
    env_rocks_bigrock05 = "68e8e1249c204370acd9e88ef70e3709"
    env_rocks_bigrock06 = "8769123f3fd7449db01c167e305b2ba0"
    env_rocks_bigrock07 = "ac8bbe6f517849129ce15fb6c111c1d0"
    env_rocks_bigrock08 = "6e05606c5ede48359b76a4cddcf5a787"
    env_rocks_bigrock09 = "9fdd02a603d0485297396b3bba377324"
    env_rocks_bigrock10 = "227891516a1b4c11bee9667df9afc883"
    env_rocks_bigrock11 = "a1eba609b1b64e13a461410f74a53c26"
    env_rocks_bigrock12 = "0da8e4ac792144f19f8644da83ea87df"
    env_rocks_bigrock13 = "a5d325bd2af74222be6dd6b1018e6918"
    env_nature_rocks_large01 = "68ce1275ba8142a7bba2aebe5b8426bc"
    env_nature_rocks_large02 = "e31ed236f5f943fe83c29b5a2c7412d4"
    env_nature_rocks_large03 = "eacb2d0a75eb4c01ba95821606bec1fe"
    env_nature_rocks_large04 = "33232a2d84954fd8a44b6f505eec9b5c"
    env_nature_rocks_waterrock01 = "0bba131a806e44ce81e5152063cca140"
    env_nature_rocks_waterrock02 = "6459d904f9d54549a6bc853da63a056d"
    env_racetrack_turn01 = "28c90d70deb541b7a44020da40381fff"
    env_racetrack_turn02 = "12f750c105b1471ba10f8850b7def8aa"
    env_racetrack_straight = "0e6b60f3dab2485980a3fa86e9b16523"
    env_racetrack_straight = "4147d2ca30ba45d9b2524e327446c801"
    water = "990cce84a6834ea683ccd0aee5e71e15"
    chemicals = "f0f2db631f2e4aae8dc4ab7cd6fe2658"
    oil = "40151920f8834d598f5dc9d52222a6f8"