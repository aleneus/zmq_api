"""API to test lib."""

import logging
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from lib import get_activity, get_activities_info
from zmq_api import ZmqApi, MethodError, INVALID_PARAMS


def run_activity(name, args):
    """Try to run any activity and return it's result."""
    act = get_activity(name)
    if act is None:
        return MethodError(INVALID_PARAMS, "Wrong activity name")
    return act(args)


def main():
    """Entry point."""
    api = ZmqApi()
    api.link_method('version', lambda: '0.1')
    api.link_method('activities', get_activities_info)
    api.link_method('proc', run_activity)
    api.run()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
