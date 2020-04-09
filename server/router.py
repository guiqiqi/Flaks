"""
Router for application
It will record path with handler function as registry.
Using for class Application.
"""

from . import errors


class Router:
    """
    Router class
    Used to record the path given by the user and
    the processing function corresponding to the request.
    """

    def __init__(self):
        """
        Initialize Route class

        self._path_methods: Registry from path to acceptable methods.
                            e.g. self._path_methods = {
                                "/calendar": {"GET", "POST"}
                            }
        self._url_map: Registry from tuple to handler function,
                       the key must be pair with path and method.
                       e.g. self._url_map = {
                           ("/calendar", "GET"): <function>,
                           ("/calendar", "POST"): <function>,
                           ...
                       }
        """
        self._path_methods = dict()
        self._url_map = dict()

    def add_record(self, path, methods, function):
        """
        Add one record to url_map

        Parameters:
            path: str - Request path
            methods: Iterable[str] - Methods bound with path
            function: Callable[[Request], str] - Handler
        """
        for method in methods:
            if not path in self._path_methods.keys():
                self._path_methods[path] = set()
            self._path_methods[path].add(method)
            self._url_map[(path, method)] = function

    def match(self, path, method):
        """
        Find one record from url_map.
        When there is no register in url_map:
            path matched, but no suitbale method - errors.NoSuitableMethod
            path not matched - errors.PathNotFound

        Usage:
            match(path: str, method: str) -> Callable[[Request], str]
        """
        if not path in self._path_methods.keys():
            raise errors.PathNotFound(path)

        handler = self._url_map.get((path, method), None)
        if not handler:
            raise errors.NoSuitableMethod(method)

        return handler
