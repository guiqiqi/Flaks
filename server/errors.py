"""Error definitions"""


class Error(Exception):
    """Exception raised by procedure"""
    pass


class ApplicationError(Exception):
    """Exception raised by Application layer"""
    pass


class RequestError(Error):
    """Error during procedure Request"""
    pass


class ResponseError(Error):
    """Error during procedure Response"""
    pass


class InvalidRequest(RequestError):
    """Invalid Request Exception"""
    pass


class InvalidBasciLine(RequestError):
    """Invalid basic line"""
    pass


class InvalidHTTPResponseCode(ResponseError):
    """Got an invalid HTTP Response code"""
    pass


class UnknownHTTPMethod(ResponseError, ApplicationError):
    """Client sent us request with unknwon HTTP method"""
    pass


class InvalidWorkDir(ApplicationError):
    """Workdir cannot be found or have no permission to access"""
    pass


class NoSuitableMethod(ApplicationError):
    """Cannot found suitable method for path"""
    pass


class PathNotFound(ApplicationError):
    """No path registerd"""
    pass


class CGIExecutingError(ApplicationError):
    """Error occured when dealing with CGI script"""
    pass
