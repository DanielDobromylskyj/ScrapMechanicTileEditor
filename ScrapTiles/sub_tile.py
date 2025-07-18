
class SubCellData:
    def __init__(self, data_type: str, data, meta_data):
        self.type = data_type
        self.original_data = data

        self.data = None
        self.meta_data = meta_data

    def decode(self, decode_func):
        self.data = decode_func(self.original_data, self.meta_data)

    def encode(self, encode_func=None):
        if not encode_func:
            return self.original_data
        return encode_func(self.data, self.meta_data)
