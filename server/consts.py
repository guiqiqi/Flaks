"""WSGI Server Consts"""

# All accepted HTTP methods
ACCEPT_METHODS = {
    "GET", "HEAD", "POST", "PUT",
    "DELETE", "CONNECT", "OPTIONS",
    "TRACE", "PATCH"
}

# All methods which has request body
HAS_BODY_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

# Response codes with descriptions
HTTP_RESPONSE_DESCRIPTIONS = {
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',
    103: 'Early Hints',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi-Status',
    208: 'Already Reported',
    226: 'IM Used',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: '(Unused)',
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Payload Too Large',
    414: 'URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Range Not Satisfiable',
    417: 'Expectation Failed',
    421: 'Misdirected Request',
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    425: 'Too Early',
    426: 'Upgrade Required',
    427: 'Unassigned',
    428: 'Precondition Required',
    429: 'Too Many Requests',
    430: 'Unassigned',
    431: 'Request Header Fields Too Large',
    451: 'Unavailable For Legal Reasons',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    506: 'Variant Also Negotiates',
    507: 'Insufficient Storage',
    508: 'Loop Detected',
    509: 'Unassigned',
    510: 'Not Extended',
    511: 'Network Authentication Required'
}

# WSGI Server version
WSGI_VERSION = (1, 0)

# Make a map from str to hex string
# e.g. {'%55': U, '%56': 'V', '%57': 'W'}
HEX_DIG = '0123456789ABCDEFabcdef'
_PUNCTUATIONS = {s.encode() for s in
                 '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'}
_ALL_HEX_TO_BYTE = {('%' + f + s): bytes(bytearray.fromhex(f + s))
                    for f in HEX_DIG for s in HEX_DIG}
HEX_TO_BYTE = dict()

for key, value in _ALL_HEX_TO_BYTE.items():
    if value.isalnum() or value.isspace():
        HEX_TO_BYTE[key] = value.decode()
    if value in _PUNCTUATIONS:
        HEX_TO_BYTE[key] = value.decode()
