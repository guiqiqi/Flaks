"""WSGI Server Settings"""

# Current HTTP Version is equal to 1.1
HTTP_VERSION = "HTTP/1.1"

# Current Server name
SERVER_NAME = "Simple-HTTP-Server(Frask-v0.0.1)"

# Default response content-type
DEFAULT_RESPONSE_CONTENT_TYPE = "text/html"

# Max request size for request
MAX_REQUEST_SIZE = 1024

# CGI Execution Timeout(s)
CGI_TIMEOUT = 5

# CGI Execution catalogue
CGI_CATALOGUE = "./cgi-bin"

# Max connection watting queue size
DEFAULT_WATTING_QSIZE = 128

# Default access file when access a catalog
DEFAULT_ACCESS_FILE = "index.html"

# Executable CGI extensions
EXECUTABLE_EXTENSIONS = {
    ".cgi", ".py", ".sh", ".pl"
}

# Allow file suffix
ALLOW_FILE_SUFFIX = {
    ".cgi", ".py", ".pyw", ".html",
    ".js", ".css", ".htm", ".png",
    ".jpeg", ".gif", ".jpg"
}

# Defualt error response body
ERROR_RESPONSE_BODY = {
    401: "<html><body><h1>401 Unauthorized</h1></body></html>",
    403: "<html><body><h1>403 Forbidden</h1></body></html>",
    404: "<html><body><h1>404 Not Found</h1></body></html>",
    405: "<html><body><h1>405 Method Not Allowed</h1></body></html>",
    408: "<html><body><h1>408 Request Timeout</h1></body></html>",
    501: "<html><body><h1>501 Not Implemented</h1></body></html>",
    502: "<html><body><h1>502 Internal Server Error</h1></body></html>",
    503: "<html><body><h1>503 Service Unavailable</h1></body></html>"
}

# When code not specified return this as response body
DEFAULT_RESPONSE = ""
