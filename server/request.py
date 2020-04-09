"""
Client request from WSGIServer

The file mainly contains the Request class as a package
that passes the WSGI server information to the application
layer during the request.
"""

import sys

from . import utils
from . import errors
from . import consts
from . import settings


class Request:
    """
    The Request class encapsulates all the information
    sent by the client and contains methods to convert 
    the original packet into a request dictionary.

    __body_handler - a registry for ContentType with function
    """
    __body_handler = dict({
        "text/html": lambda body: body,
        "text/plain": lambda body: body,
        "text/css": lambda body: body,
        "text/javascript": lambda body: body
    })

    def __init__(self, rawdata: str):
        """
        Initialize a request object.

        method - request HTTP method
        url - total url requested
        path - request path info
        query - request query after '?'
        cookie - request cookie
        host - address and port bound by our server
        remote - address and port about remote user
        environ - all environment informations
        headers - request HTTP hedaer
        body - decoded request body (could be str/dict)
        args - path parameters in the request link
        http - HTTP Protocol Info

        Parameters:
            rawdata: str - Raw request string
        Usage:
            Request(rawdata: str) -> NoReturn
        """
        self._rawdata = rawdata

        self.method = None
        self.url = None
        self.path = None
        self.query = str()
        self.host = tuple()
        self.remote = tuple()
        self.cookie = utils.DynamicDict()
        self.environ = utils.DynamicDict()
        self.headers = utils.DynamicDict()
        self.body = utils.DynamicDict()
        self.args = utils.DynamicDict()
        self.http = utils.DynamicDict()

    @staticmethod
    def unquote(encoded: str) -> str:
        """
        Unquto url encoded string like:
        "Hello%20world" -> "Hello world"

        Parameters:
            encoded: str - url encoded string
        Usage:
            unquote(encoded: str) -> decoded: str
        """
        decoded = encoded
        for key, value in consts.HEX_TO_BYTE.items():
            decoded = decoded.replace(key, value)
        return decoded

    @staticmethod
    def url_decode(encoded: str, splitor="&") -> dict:
        """
        Decode string encoded with url pattern like:
        "Great=Hello%20world&Language=Python"

        Parameters:
            encoded: str - url encoded string
            splitor: str - divdor of dtring
        Usage:
            url_decode(encoded: str) -> dict
        """
        _paras = encoded.split(splitor)
        parameters = dict()
        for para in _paras:

            key, *value = para.split('=')

            # Fix for paras like &a=a
            if not value:
                value = str()
            else:
                value = value[0]

            value = Request.unquote(value)
            parameters[key] = value

        return parameters

    def _set_environ(self):
        """
        Get request enviroment informations.
        The following code snippet does not follow PEP8 conventions
        but it's formatted the way it is for demonstration purposes
        to emphasize the required variables and their values
        """

        # wsgi environment support
        self.environ["wsgi.input"] = sys.stdin
        self.environ["wsgi.errors"] = sys.stderr
        self.environ["wsgi.version"] = consts.WSGI_VERSION
        # For our SIMPLE-HTTP-WSGIServer
        self.environ["wsgi.multithread"] = False
        self.environ["wsgi.multiprocess"] = False  # we have no plan
        self.environ["wsgi.run_once"] = True      # to support these
        self.environ["wsgi.url_scheme"] = "http"  # features.

        # cgi environment support
        self.environ.REQUEST_METHOD = self.method
        self.environ.SCRIPT_FILENAME = self.path
        self.environ.SCRIPT_NAME = self.path.split('/')[-1]
        self.environ.PATH_INFO = self.url.strip(self.path)
        self.environ.QUERY_STRING = self.query
        self.environ.CONTENT_LENGTH = \
            self.headers.get("Content-Length", 0)
        self.environ.CONTENT_TYPE = \
            self.headers.get("Content-Type", None)
        self.environ.SERVER_PROTOCOL = self.http.version
        self.environ.SERVER_NAME, self.environ.SERVER_PORT = \
            self.headers.get("Host").strip("Host: ").split(':')
        self.environ.SERVER_PORT = int(self.environ.SERVER_PORT)
        self.environ.SERVER_SOFTWARE = settings.SERVER_NAME
        self.host = self.environ.SERVER_NAME, self.environ.SERVER_PORT

        # HTTP encitoment support
        self.environ.HTTP_HOST = self.environ.SERVER_NAME\
            + ':' + str(self.environ.SERVER_PORT)
        self.environ.HTTP_VERSION = self.http.version
        self.environ.HTTP_USER_AGENT = self.headers.get("User-Agent", '')
        self.environ.HTTP_COOKIE = self.headers.get("Cookie", '')

    def _makebody(self, bodydata: str):
        """
        Get the request body according to the information in the
        request header, and then find the corresponding support
        function for analysis based on the content-type information.
        """
        # If request method should not carry a body
        if not self.method in consts.HAS_BODY_METHODS:
            return

        content_length = int(self.headers.get("Content-Length", len(bodydata)))
        self.headers["Content-length"] = content_length
        content_type = self.headers.get("Content-Type", "text/plain")
        content_type = content_type.split(';', 1)[0]
        handler = self.__body_handler.get(content_type, lambda body: body)

        # Call the handler to del with body
        self.body = handler(bodydata[0: content_length])

    @staticmethod
    def register_body_handler(content_type: str, handler):
        """
        Add one hanlder function to body registry.

        Parameters:
            content_type: str - Specified content type deal with
            handler: Callable[[str], Any] - handler function
        """
        Request.__body_handler[content_type] = handler

    def parse(self):
        """
        Parse HTTP headers according to the HTTP request standard:
        HTTP requests are separated by CR-LF.
        The first line is the request method and the HTTP version.
        The following is the request's environment information (header).
        After that will only left request' body.
        """
        rawreq = self._rawdata.strip().split("\r\n")

        # Split and get the basic info in request
        basics = rawreq.pop(0)
        self._set_basics(basics)

        # Get headers - request body and header splited with '\r'
        # Traverse request, stop when a single line '\r' is found
        try:
            headers = list()
            line = rawreq.pop(0).strip()
            while line:
                headers.append(tuple(line.split(": ")))
                if not rawreq:
                    break
                line = rawreq.pop(0).strip()

            self.headers.update(dict(headers))
        except ValueError as _error:
            raise errors.InvalidRequest(rawreq)

        # Add environ informations
        self._set_environ()

        # The left part is request body
        self._makebody("\r\n".join(rawreq))

        # Try add cookie info
        cookie = self.headers.get("Cookie", '')
        if cookie:
            self.cookie = self.url_decode(cookie, "; ")

    def _set_basics(self, line):
        """
        Informations specified in the first line of request:
        Path, HTTP Method, HTTP Protocol version
        Extract these info from first line.
        """
        try:
            # Get and check data in first line
            method, path, version = line.split()
            assert method in consts.ACCEPT_METHODS

            # Set method and environ data
            self.method, self.url = method, path
            self.http.version = version

        except ValueError as _error:
            raise errors.InvalidBasciLine(line)
        except AssertionError as _error:
            raise errors.UnknownHTTPMethod(method)

        # Try extract args from query string
        pure, *args = path.split('?', 1)

        self.path = pure
        if args:
            self.query = args[0]
            self.args = self.url_decode(args[0])


Request.register_body_handler(
    "application/x-www-form-urlencoded",
    Request.url_decode)
