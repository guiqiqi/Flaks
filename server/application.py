"""
Application layer

Responsible for hosting the user's 
application and responding to WSGIServer.
"""

import os
import subprocess

from typing import Set
from typing import Tuple
from typing import Union
from typing import Optional
from typing import NoReturn
from typing import Callable
from typing import Iterable

from . import utils
from . import errors
from . import router
from . import consts
from . import settings
from .request import Request
from .response import Response


class Application:

    # Default mime types
    mimetype = {
        ".txt": "text/plain",
        ".js": "text/javascript",
        ".css": "text/css",
        ".json": "application/json",
        ".xml": "application/xml",
        ".html": "text/html",
        ".htm": "text/html"
    }

    """
    Application class

    Contains route processing mechanism, 
    response function to WSGIServer, 
    directory access function, 
    and CGI extension execution function.
    """

    def __init__(self, name: str, workdir: Optional[str] = '.',
                 default_access_file: Optional[str] = settings.DEFAULT_ACCESS_FILE,
                 executable: Optional[Set[str]] = settings.EXECUTABLE_EXTENSIONS):
        """
        Application initialization

        Parameters:
            name: str - Your application name
            workdir: str - Working directory of the
                           application, which can be
                           a relative path or an absolute path
            default_access_file: str - File contents returned by 
                                 default when accessing a directory
            executable: set - Executable file suffix collection
        """
        self._name = name

        # Try to chdir to workdir
        if not os.path.isdir(workdir):
            raise errors.InvalidWorkDir(workdir)
        os.chdir(workdir)

        self._router = router.Router()
        self._dfa = default_access_file
        self._executable = executable

    def real_path(self, path: str) -> str:
        """
        Generate a real path to access:
            e.g. "/" -> "/index.html", ".html"
            e.g. "/test.html" -> "/test.html", ".html"
            e.g. "/catalog" -> "/catalog/index.html", ".html"
            e.g. "/.cgi-bin/h.cgi" -> "/.cgi-bin/h.cgi", ".cgi"
        Return real path with suffix.

        Parameters:
            path: str - Raw request path
        Usage:
            real_path(path: str) -> Tuple[str, str]
        """
        _, *suffix = path.rstrip('/').split('/')[-1].split('.')

        if not suffix:
            path = path.rstrip('/') + '/' + self._dfa
            suffix = self._dfa.split('.')[-1]
            return '.' + path, '.' + suffix

        return "./" + path.strip('/'), '.' + suffix[0]

    def route(self, path: str, methods: Optional[Iterable[str]] = ("GET")) -> NoReturn:
        """Add route registry"""

        for method in methods:
            if not method in consts.ACCEPT_METHODS:
                raise errors.UnknownHTTPMethod(method)

        def wrapper(function: Callable[[Request], Union[Response, str, Tuple[int, str]]]):
            """Function Wrapper"""
            self._router.add_record(path, methods, function)

            def params(*args, **kwargs):
                """Transfer all params to handler function"""
                return function(*args, **kwargs)

            # Fix change for handler function name
            params.__name__ = function.__name__
            return params

        return wrapper

    def _distrbuted_cgi(self, scriptfile: str, environ: dict) -> Response:
        """
        Distrubuted CGI Support

        The function reads the first line of the 
        CGI document and selects the program to 
        execute it, and uses the subprocess to create
        a new process for execution.

        Parameters:
            scriptfile: str - The script file want execute
            environ: dict - Environment values for scipt
        """
        with open(scriptfile, "r") as handler:
            executer = handler.readline().strip("#! \r\n")

        # Remove wsgi environ
        removed = dict()
        for key, value in environ.items():
            if not key.startswith("wsgi."):
                removed[key] = str(value)
                os.environ[key] = str(value)

        process = subprocess.Popen((executer, scriptfile),
                                   stdout=subprocess.PIPE,
                                   env=removed)

        try:
            ret, _errs = process.communicate(
                timeout=settings.CGI_TIMEOUT)
        except subprocess.TimeoutExpired as _error:
            process.kill()
            ret, _errs = process.communicate()
            return Response(408)

        if process.returncode:
            print("Perl execution error.")
            return Response(502)

        return Response(200, ret.decode())

    def respond(self, request: Request) -> Response:
        """
        Respond to requests from WSGIServer

        First look through the router, and return HTTP-405
        if there is no suitable processing method;
        If no corresponding path is found,
        continue to look for it in the working 
        directory according to the static file.
        """
        try:
            method, path = request.method, request.path
            handler = self._router.match(path, method)
            content = handler(request)
            if isinstance(content, Response):
                return content
            return Response(200, content)

        # When not suitable method
        except errors.NoSuitableMethod as _error:
            return Response(405)

        # When path not registered
        except errors.PathNotFound as _error:
            pass

        # When exception unhandled
        except Exception as _error:
            print(_error)
            return Response(502)

        path, suffix = self.real_path(path)
        if not os.path.isfile(path):
            return Response(404)

        # CGI Execute support
        if suffix in self._executable and path.startswith(settings.CGI_CATALOGUE):
            try:
                return self._distrbuted_cgi(path, request.environ)
            except Exception as _error:
                print(_error)
                return Response(502)

        with open(path, 'r') as handler:
            mime = self.mimetype.get(suffix, "text/plain")
            hedaer = utils.DynamicDict({"Content-Type": mime})
            return Response(200, handler.read(), headers=hedaer)
