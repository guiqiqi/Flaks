"""Simple running exmample"""

import json

from server import Request
from server import Response
from server import HTTPServer
from server import Application

Request.register_body_handler("text/json", json.loads)
httpd = HTTPServer(("0.0.0.0", 15014))
application = Application(__name__)
httpd.serve(application)


@application.route("/hello", methods=["GET"])
def test_get_function(request):
    """Hello World!"""
    # __import__("time").sleep(10)
    return \
        """
<html>
    <body style="background: #dfe6e9; text-align:center;">
        <h1 style="margin-top:30vh;">Hello World</h1>
        <h3>From: Simple-Python-HTTP-Server</h3>
        <h4 style="font-style: italic;">Your UA info: {UA}</h4>
    </body>
</html>
        """.format(UA=request.headers.get("User-Agent", ''))


httpd.start()
