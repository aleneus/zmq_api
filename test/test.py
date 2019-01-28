"""Client tests."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import unittest
import pickle

import zmq

from zmq_api import build_request, parse_response
from zmq_api import (PARSE_ERROR, INVALID_REQUEST,
                     METHOD_NOT_FOUND, INVALID_PARAMS)


class TestApiZmq(unittest.TestCase):
    # TODO: split to good and bad tests
    """Test suite for ZeroMQ API."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = zmq.Context().socket(zmq.REQ)
        self.socket.connect('tcp://127.0.0.1:43000')

    def _send_json(self, req_str):
        self.socket.send(pickle.dumps(req_str))
        res_str = pickle.loads(self.socket.recv())
        parsed = parse_response(res_str)
        return parsed

    def _request(self, method, params=None, req_id=None):
        req_str = build_request(method, params, req_id)
        return self._send_json(req_str)

    def _request_proc(self, func_name, func_data, req_id):
        """Request processing of data."""
        params = {'name': func_name,
                  'args': func_data}
        return self._request('proc', params, req_id)

    def test_just_request(self):
        """Just call some simple method."""
        self._request('some_request', req_id=1)

    def test_double_request(self):
        """Two requests, one after another."""
        self._request('some_request', req_id=1)
        self._request('some_request', req_id=1)

    def test_get_version(self):
        """Get version of API."""
        res = self._request('version', req_id=1)
        self.assertTrue(res is not None)
        result = res[0]
        self.assertTrue('.' in result)

    def test_funcs_key_res_is_not_empty(self):
        """Reqult of correct request is not empty."""
        res = self._request('activities', req_id=1)
        self.assertTrue(res is not None)
        result = res[0]
        self.assertTrue(len(result) > 0)

    def test_smooth_ok(self):
        """Call function for processing array."""
        res = self._request_proc('Smooth', [1, 3], 1)
        self.assertTrue(res is not None)
        result = res[0]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 2)

    def test_wrong_method(self):
        """Request to call non-existing method."""
        res = self._request('wrong_method', req_id=1)
        self.assertTrue(res is not None)
        error = res[1]
        self.assertEqual(error['code'], METHOD_NOT_FOUND)

    def test_id(self):
        """Id in request and id in response should be the same."""
        res = self._request('version', req_id=100)
        self.assertTrue(res is not None)
        req_id = res[2]
        self.assertEqual(req_id, 100)

    def test_positional_params(self):
        """Positional parameters."""
        res = self._request(
            method='proc',
            params=['Smooth', [1, 2]],
            req_id=1
        )
        self.assertTrue(res is not None)
        result, error = res[0], res[1]
        self.assertTrue(error is None)

    def test_wrong_json_rpc(self):
        """JSON ok, but content wrong."""
        req_str = '{"jsonrpc": "2.0", "method": 1, "params": "bar"}'
        res = self._send_json(req_str)
        error = res[1]
        self.assertEqual(error['code'], INVALID_REQUEST)

    def test_wrong_json_rpc_2(self):
        """JSON ok, but content wrong."""
        req_str = '{"jsonrpc": "2.0", "method": 1, "params": "bar", "id": 1}'
        res = self._send_json(req_str)
        error = res[1]
        self.assertEqual(error['code'], INVALID_REQUEST)

    def test_wrong_json_rpc_3(self):
        """JSON ok, but content wrong."""
        req_str = '{"jsonrpc": "2.0", "method": 1, "params": 2, "id": 1}'
        res = self._send_json(req_str)
        error = res[1]
        self.assertEqual(error['code'], INVALID_REQUEST)

    def test_wrong_json_rpc_4(self):
        """JSON ok, but content wrong."""
        req_str = '{"jsonrpc": "2.0", "method": 1, "params": 2.3, "id": 1}'
        res = self._send_json(req_str)
        error = res[1]
        self.assertEqual(error['code'], INVALID_REQUEST)

    def test_invalid_json(self):
        """Invalid JSON."""
        req_str = '{"jsonrpc":"2.0","method":"foobar,"params":"bar","baz]'
        res = self._send_json(req_str)
        error = res[1]
        self.assertEqual(error['code'], PARSE_ERROR)

    def test_wrong_processing_routine_name(self):
        """Raise error in executing function."""
        req_str = '{"jsonrpc": "2.0", "method": "proc", "params":\
        {"name": "WrongName", "args": null}, "id": 1}'
        res = self._send_json(req_str)
        error = res[1]
        self.assertTrue(error is not None)
        self.assertTrue(error['code'] == INVALID_PARAMS)


if __name__ == "__main__":
    unittest.main()
