
class SubCellData:
    def __init__(self, data_type: str, data, meta_data, version):
        self.type = data_type
        self.original_data = data
        self.version = version

        self.data = None
        self.meta_data = meta_data

    def decode(self, decode_func):
        self.data = decode_func(self.original_data, self.meta_data, self.version)

    def encode(self, encode_func=None):
        if not encode_func:
            return self.original_data
        return encode_func(self.data, self.meta_data)
