import json


_DATA_FORMAT_CONVERTERS = {
    'binary': {
        'decoder': lambda rx_bytes: bytes(rx_bytes),
        'encoder': lambda tx_bytes: bytes(tx_bytes),
    },
    'string': {
        'decoder': lambda rx_bytes: rx_bytes.decode('utf-8'),
        'encoder': lambda string: bytes(string, 'utf-8'),
    },
    'json': {
        'decoder': lambda rx_bytes: json.loads(rx_bytes.decode('utf-8')),
        'encoder': lambda json_string: bytes(json.dumps(json_string), 'utf-8')
    }
}


def get_data_format_converter(data_format):
    return _DATA_FORMAT_CONVERTERS.get(data_format)
