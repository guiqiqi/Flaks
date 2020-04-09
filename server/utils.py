"""
Tools used by the WSGI server
"""

import threading


class DynamicDict(dict):
    """Dict class support attribute index"""

    # dict functions
    _functions = {
        "keys", "fromkeys", "values", "setdefault",
        "update", "get", "clear", "popitem",
        "copy", "items", "pop"
    }

    def __getattr__(self, key):
        """Return value as attribute"""
        if key in self._functions:
            # return super().__getattribute__(key)
            return super(DynamicDict, self).__getattribute__(key)
        try:
            return self[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        """Set value as attribute"""
        # super().__setitem__(key, value)
        super(DynamicDict, self).__setitem__(key, value)


def thread(function):
    """Use new thread to execute"""

    def params(*args, **kwargs):
        """Receieve paramaters"""

        def process(*args, **kwargs):
            function(*args, **kwargs)

        _thread = threading.Thread(
            target=process, args=args, kwargs=kwargs)
        _thread.setDaemon(True)
        _thread.start()

    return params
