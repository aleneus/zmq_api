"""Example of request-reply."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from zmq_api import ZmqApi


def say_hello(name):
    """Return string."""
    return "Hello, {}!".format(name)


def start_api():
    api = ZmqApi(addr='127.0.0.1', port='43000')
    api.link_method("hello", say_hello)
    print("API started")
    api.run()
    print("API stopped")


if __name__ == "__main__":
    start_api()

