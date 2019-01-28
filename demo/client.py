"""Remote call of function."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import pickle
import zmq


def request_hello():
    addr = '127.0.0.1'
    port = '43000'
    socket = zmq.Context().socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(addr, port))

    req_str = ''
    req_str += '{'
    req_str += '    "jsonrpc": "2.0", '
    req_str += '    "method": "hello", '
    req_str += '    "params": ["world"], '
    req_str += '    "id": 1'
    req_str += '}'
    socket.send(pickle.dumps(req_str))

    res_str = pickle.loads(socket.recv())
    print(res_str)


if __name__ == "__main__":
    request_hello()
