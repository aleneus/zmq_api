"""Remote API with ZeroMQ and JSON RPC."""

import pickle
import logging
import json

import zmq


__version__ = '0.1.0'

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

STANDARD_MESSAGES = {
    PARSE_ERROR: "Parse error",
    INVALID_REQUEST: "Invalid request",
    METHOD_NOT_FOUND: "Method not found",
    INVALID_PARAMS: "Invalid params",
}

LOG = logging.getLogger(__name__)


def build_request(method, params=None, req_id=None):
    """Build JSON RPC string."""
    body = {
        'jsonrpc': '2.0',
        'method': method,
    }

    if params is not None:
        body['params'] = params

    if req_id is not None:
        body['id'] = req_id

    return json.dumps(body)


def build_response(result=None, error=None, req_id=None):
    """Build response JSON RPC string."""
    body = {
        'jsonrpc': '2.0',
    }

    if result is not None:
        body['result'] = result

    if error is not None:
        body['error'] = error

    body['id'] = req_id

    return json.dumps(body)


def parse_request(request):
    """Parse request string."""
    try:
        body = json.loads(request)
    except json.decoder.JSONDecodeError:
        return PARSE_ERROR

    try:
        method = body['method']
    except KeyError:
        return INVALID_REQUEST

    try:
        params = body['params']
    except KeyError:
        params = None

    try:
        req_id = body['id']
    except KeyError:
        req_id = None

    if (method is not None) and (req_id is None):
        return INVALID_REQUEST

    # checking the type of params
    if params is not None:
        wrong = [str, int, float]
        if any([isinstance(params, cls) for cls in wrong]):
            return INVALID_REQUEST

    return method, params, req_id


def parse_response(response):
    """Parse response string."""
    try:
        body = json.loads(response)
    except json.decoder.JSONDecodeError:
        return None

    try:
        result = body['result']
    except KeyError:
        result = None

    try:
        error = body['error']
    except KeyError:
        error = None

    try:
        req_id = body['id']
    except KeyError:
        req_id = None

    return result, error, req_id


class MethodError:
    """Error class for control error from methods."""
    def __init__(self, code, message):
        self.code = code
        self.message = message


class ZmqApi:
    """API on ZeroMQ and JSON RPC."""
    def __init__(self, addr='127.0.0.1', port='43000'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind('tcp://{}:{}'.format(addr, port))
        self._funcs = {}

    def _send_ok(self, result, req_id):
        """Send response with ok status"""
        res_str = build_response(result, None, req_id)
        self.socket.send(pickle.dumps(res_str))

    def _send_error(self, code, message="", req_id=None):
        """Send response with error status."""
        error = {
            'code': code,
            'message': message,
        }
        res_str = build_response(None, error, req_id)
        self.socket.send(pickle.dumps(res_str))

    def link_method(self, method, func):
        """Connect method to function.

        Parameters
        ----------
        method: str
            Name of method.
        func: callable
            Function to be called. This function should return the
            instance of MethodError for handling details of errors.
        """
        self._funcs[method] = func

    def __proc_method(self, method, params, req_id):
        # LOG.debug("__proc_method()")
        # LOG.debug("method: {}".format(method))
        # LOG.debug("params: {}".format(params))
        if method in self._funcs:
            func = self._funcs[method]
        else:
            self._send_error(
                METHOD_NOT_FOUND,
                STANDARD_MESSAGES[METHOD_NOT_FOUND],
                req_id=req_id
            )
            return

        try:
            if params is None:
                result = func()
            elif hasattr(params, 'keys'):
                result = func(**params)
            else:
                result = func(*params)

            # check if error returned by method
            if isinstance(result, MethodError):
                self._send_error(result.code, result.message, req_id)
                return

            self._send_ok(result, req_id)
        except Exception as ex:
            # LOG.debug("Exception while proc method")
            msg = "{}: {}".format(type(ex), ex)
            LOG.info(msg)
            self._send_error(
                INTERNAL_ERROR,
                str(ex),
                req_id=req_id
            )

    def run(self):
        """Run loop for processing requests."""
        LOG.info("API started")
        while True:
            try:
                req_str = pickle.loads(self.socket.recv())
                # LOG.debug("res_str: %s" % req_str)
                parsed = parse_request(req_str)
                # LOG.debug("parsed: {}".format(parsed))
                if isinstance(parsed, int):
                    self._send_error(
                        parsed,
                        STANDARD_MESSAGES[parsed]
                    )
                    continue
                method, params, req_id = parsed
                self.__proc_method(method, params, req_id)
            except zmq.error.ZMQError as expt:
                msg = "{}: {}".format(type(expt), expt)
                LOG.info(msg)
                self._send_error(
                    INTERNAL_ERROR,
                    "{}".format(expt)
                )
            except KeyboardInterrupt:
                LOG.info("API stopped by user")
                break
