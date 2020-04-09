"""
Simple HTTP Server

We use sockets to manage reused connections,
which listening for new connection requests,
and using a given application argument to
handle requestswhen new connection requests come.
"""

import os
import sys
import socket
import selectors

from typing import NoReturn
from typing import Tuple
from typing import Optional

from . import errors
from . import settings
from .utils import thread
from .request import Request
from .response import Response
from .application import Application


class HTTPServer:
    """
    Simple HTTP Server class.
    """

    # socket constants
    IPV4 = socket.AF_INET
    SOCKET = socket.SOL_SOCKET
    TCP_IP = socket.IPPROTO_TCP
    STREAM = socket.SOCK_STREAM
    NO_DELAY = socket.TCP_NODELAY
    REUSE_ADDR = socket.SO_REUSEADDR
    KEEP_ALIVE = socket.SO_KEEPALIVE
    READABLE = selectors.EVENT_READ
    WRITEABLE = selectors.EVENT_WRITE

    def __init__(self, address: Tuple[str, int],
                 maxsize: Optional[int] = settings.DEFAULT_WATTING_QSIZE):
        """
        Instantiate a new server object,
        initialize a socket and bind the
        given address and port to listen for link requests;

        Parameters:
            address: Tuple[addr: str, port: int] - address to be bound
            maxsize: int - maximum pending connection queue length
        Usage Example:
            HTTPServer(("localhost", 80), 128)
        """
        # Initialize socket connection
        self._maxsize = maxsize
        self._listener = listener = socket.socket(self.IPV4, self.STREAM)
        listener.bind(address)
        listener.setsockopt(self.TCP_IP, self.NO_DELAY, True)
        listener.setsockopt(self.SOCKET, self.REUSE_ADDR, True)
        listener.setsockopt(self.SOCKET, self.KEEP_ALIVE, True)
        listener.setblocking(False)

        # Bind selector to connection
        self._poll = selectors.DefaultSelector()

        # Get server enviroment infomations
        host, port = listener.getsockname()[:2]
        self._server_name = socket.getfqdn(host)
        self._server_port = port

        # Set appliction
        self._appplication: Application = None

        # Set flag for server status
        self._running = False

    @property
    def status(self) -> bool:
        """
        Return current server status.
        """
        return self._running

    def log(self, client: Tuple[str, int],
            request: Request, response: Response) -> NoReturn:
        """
        Log request and response

        Parameters:
            client: Tuple[str, int] - client informations
            request: Request - request
            response: Response - response
        """
        print("{client} {url} - {method} > {code}".format(
            client=client[0] + ':' + str(client[1]),
            url=request.url, method=request.method,
            code=response.code
        ))

    def _handle(self, connection: socket.socket, client: Tuple[str, int],
                max_request: Optional[int] = settings.MAX_REQUEST_SIZE) -> bytes:
        """
        Takes a connection parameter so reads data.
        The parser is then used to parse the data 
        sent by the client, and the information obtained
        is passed to the application function for processing.

        Parameters:
            connection: socket.socket - Active conenction 
            client: Tuple[str, int] - Client's address
            max_request: int - Max request size for request
        """
        try:
            rawdata = connection.recv(max_request).decode()
            request = Request(rawdata)
            request.parse()
        except errors.Error as _error:
            return Response(501).done()
        except Exception as _error:
            return str().encode()

        # When there is not application registerd
        if not self._appplication:
            response = Response(404)
            self.log(client, request, response)
            return response.done()

        # Get response from application
        try:
            response = self._appplication.respond(request)
            if isinstance(response, str):
                response = Response(200, response)
            if isinstance(response, tuple):
                response = Response(*response)
        except errors.ApplicationError as _error:
            print(_error)
            response = Response(502)

        self.log(client, request, response)
        return response.done()

    def serve(self, application: Application) -> NoReturn:
        """
        Set the application to be executed by the current server.
        Applications can return a Response object, 
        a string, or an array of return codes and strings.
        """
        self._appplication = application

    @thread
    def _sock_service(self, connection: socket.socket, mask: int) -> NoReturn:
        """
        Detect event type and make some actions on it.

        """
        client = connection.getpeername()
        response = self._handle(connection, client)
        try:
            connection.sendall(response)
        except ConnectionError as _error:
            connection.close()
            self._poll.unregister(connection)

    def _sock_accpet(self, fileobj: socket.socket, mask: int) -> NoReturn:
        """
        Accept a new connection request.
        Set COnnection to non-blocking.
        Register in select poll.
        """
        connection, _address = fileobj.accept()
        connection.setblocking(False)
        events = self.READABLE

        # Register new connection to poll
        self._poll.register(connection, events, self._sock_service)

    def start(self) -> NoReturn:
        """
        Continuously process new connection requests.
        The connection information is passed to the
        handle function to generate a response.
        """
        # Start server
        self._running = True
        listener = self._listener
        listener.listen(self._maxsize)
        self._poll.register(listener, self.READABLE, self._sock_accpet)

        while self._running:
            events = self._poll.select()
            for handler, mask in events:
                handler.data(handler.fileobj, mask)

    def stop(self) -> NoReturn:
        """
        Set the _running flag to False,
        which will cause the main loop running on start stop
        """
        self._running = False
