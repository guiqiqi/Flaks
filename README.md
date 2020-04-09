# Simple HTTP Server - Flaks

![Python](https://img.shields.io/badge/Python-3.6%2B-blue?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAAD8UlEQVRoge2YTWhcVRSAv3MnaSY/SqlSNEVTartppBZN8Ye2aYwTNUh3jQqCKEoWbqKWtO6yakmoNOBWFF0EaSsFu3CKiROjRUu7aaOpolQ0hEhpQQ1pJpP37nExVUnnzcx7uS9DC/NtZjj3/N775t1zBqpUqXJbI/G4UeHg6HaD6VLlMYEtQDPQCPjANYEZFc4ZOOklvx5nYMDGEdm9gP2j20xCRoDWsCaKnlYv8RLvdlx1DZ9wsh441WD8Nd8BD0QxE2SzEd2lqU0fMj6uLikYF+OahcZdwIaV2KrweE12Z5dLfHAsQOW/5Ges0VaLbQEmw9pbeMIlPrgWYPXO/DdJc/ipKQZTv6NyPLwDucMlPkCNq4M8+gzvjG4lJ/OI7ovHZzhiKoANxsoPsXmLgNMjdCvgtGd2qHMYGC6lY/rH+hCOltLRibo+dJlOFmQStYdlT+5kSf/h060oSdAdiHyqE8nXSimWPoGDmc1GdT/oTmAj+dagkgiqR3Us+YV0Zn8LUih6Aon+L/catRdAe8m3CZVO/l+aSNBbbDG4gLfHWlR0BGhYrazySLiGTvT5YkuBBZhafYtK7Ljqrzc+y8XapJnGe4IWgk9ApdspsXD8aa137EYa28pqG+/hQHGBpC+zlojd5QqYN8gLHHn6ip5pWg8aZsO2BAkLC0h624lt0FmGRWUa5X1recgbfPI0AL43DDSVtRZZFyQueI0mMPdGbNB/EuSQr94oQ6lZkFDmqhi+qjuC6ouholitDxIXFKCq6yIcwIi9vvgq73UvhjXQM03r8XJ7mDD9iD4S1g7Ra0HiggJEyWqI/BUyWm9eZrDb028amvH9A8Be4D5KTXreEvkNijqImdkgadBNHFjpTVhV+wYDnZ5matvwvTTIXREziobxLwSKbxb4Yn4u50uUswylLmmGJAlzYtWThwXql6aCFgrfQpev/gjMl/Kmwvd567oulJYYEixHWtpYClooLOB4j69wtozDfIHKRtfMQuBh7aFii4E3saDHQrk2q96OeyC90rF0vngKAVj0E2Bm1dIqTRa4BPoRxrZJe/aDUsrB88Bg6i85MPa6wmdFdcozLO2Lb67QNjRFHwF/sPNzC50KGeD6aieyUpx6noBZNirOp3SrzsShqWQBM4i2grkfuBiX00oWkJbduSlpX5hG9ERcTt3+S1OZi9CUPauZNQ9Sm/gb3/b8b++GWwFivyVM65qnGSOT+Mvm+Gmn+Dg+QrI7NwUS7tYuZA5NnHKJD3H8Bhqzr4B+HNHqMshz0jH/h2v42GZfHa/dAWYfwqMILSh3A3Ugc6heQfgF9BwmkWZ24bz04McVu0qVKrcx/wCMzkVJcJCK+gAAAABJRU5ErkJggg==) [![LICENSE](https://img.shields.io/badge/license-Anti%20996-green.svg)](https://github.com/996icu/996.ICU/blob/master/LICENSE)

This is a simple HTTP server. It is used to understand the working mode of HTTP, from the underlying socket to the composition mode of HTTP packets.

The server supports **CGI & WSGI** standards.

## Usage

The using is not difficult, there is a sample file `run.py` in the project, here is some details:

### Server

Just use the `server.HTTPServer` module to create an HTTP server.

Bind the `Application` instance to the server and use the `start` method to start the server.

```python
HTTPServer(self, address: Tuple[str, int], maxsize: Optional[int] = settings.DEFAULT_WATTING_QSIZE)
```

- address: which address you want to bind and listen
- maxsize: max waiting queue size of HTTP client

### Request

Generally speaking, you do not need to use the `Request` class directly, but you can process the return value of the specified mime type.

```python
request = Request(rawdata: str)
# Return reverse
request.register_body_handler("text/plain", lambda obj: obj[::-1])
```

### Response

You can instantiate a `Response` class as follows:

```Python
Response(200, "Hello World")
Response(200, "Hello World", environ={"HOSTNAME": "localhost"})
Response(200, "Hello World", headers={"UA": "Test-UA"})
```

### Application

Instantiate an `Application` and use the `route` method to bind your view function to it.

Then just bind the Application instance to the HTTP server.

```python
ttpd = HTTPServer(("0.0.0.0", 15014))
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
```

Your view function's return can be:

```python
return 200, "Hello world" # HTTP Code, Content
return "Hello world" # Content
return Response(200, "Hello world") # HTTP Response instance
```

### CGI & WSGI Support

You can define CGI extensions and catalogue such as `Settings` below.

Then just write you CGI extension.

Using WSGI with tutorial [here](http://wsgi.tutorial.codepoint.net/).

### Settings

You can modify `server/settings.py` to imply your own settings, for example:

```python
# CGI Execution Timeout(s)
CGI_TIMEOUT = 5

# CGI Execution catalogue
CGI_CATALOGUE = "./cgi-bin"
```

## About Flaks

### Name

Why named **Flaks**? 

Because it mimics **Flask**'s routing pattern, such as:

```python
@application.route("/hello", methods=["GET", POST])
```

And there is also `request` environ support (but provided in the form of parameters):

```python
def simple_hello_world(request: server.Request)
```

### Author

Author: guiqiqi187@gmail.com

GitHub: https://github.com/guiqiqi

A back-end programmer, speak English, русский, Python, C++, C.

***Wish you happy using.***