"""Stub library."""
import logging

from dsplab.activity import Activity


LOG = logging.getLogger(__name__)


class Smooth(Activity):
    "Smooth row of numeric values."
    def __call__(self, values):
        res = []
        for prv, cur in zip(values[:-1], values[1:]):
            res.append((prv+cur)/2)
        return res


class Decompose(Activity):
    """Decompose signal to two components."""
    def __call__(self, values):
        res = []

        comp_1 = []
        for value in values:
            comp_1.append(value / 2)

        comp_2 = []
        for value, comp_1_value in zip(values, comp_1):
            comp_2 = value - comp_1_value

        res.append(comp_1)
        res.append(comp_2)
        return res


ACTIVITIES = [Smooth, Decompose]


def get_activities_info():
    res = []
    for activity in ACTIVITIES:
        portion = {
            'name': activity.__class__.__name__,
            'info': activity.class_info()
        }
        res.append(portion)
    return res


def get_activity(name):
    """Return function by name."""
    LIB = {
        'Smooth': Smooth,
        'Decompose': Decompose,
    }
    try:
        # LOG.debug("name: %s" % name)
        act = LIB[name]()
        # LOG.debug("act: {}".format(act))
        return act
    except KeyError:
        return None
